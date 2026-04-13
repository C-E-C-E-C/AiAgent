from __future__ import annotations

from datetime import datetime
from functools import lru_cache
import json
import os
import re
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from llm_factory import create_llm
from map_tool import MapTool
from planner import TravelPlanner
from hello_agents.tools import MemoryTool


# 统一读取项目根目录下的 .env。
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


# FastAPI 主应用。
app = FastAPI(title="Travel Agent API", version="0.1.0")



# 跨域配置：前端本地开发时要允许不同端口访问。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 行程规划请求体：前端发来目的地、天数、预算、偏好。
class TripPlanRequest(BaseModel):
    destination: str = Field(min_length=1, description="旅行目的地")
    days: int = Field(ge=1, le=30, description="旅行天数")
    budget: float = Field(gt=0, description="旅行预算")
    preferences: str = Field(default="", description="旅行偏好")


# 行程规划响应体：不仅返回文本，还返回地图路线和 POI 信息。
class TripPlanResponse(BaseModel):
    status: Literal["ok"] = "ok"
    generated_at: str
    destination: str
    days: int
    budget: float
    preferences: str
    plan_text: str
    plan_char_count: int
    poi_count: int
    route_points: list[dict[str, Any]]
    location_info: dict[str, Any]


# 单轮聊天时，每条消息都带角色，方便模型区分 system/user/assistant。
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, description="消息内容")


# 聊天接口请求体：一个用户最新问题 + 历史消息。
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="用户最新输入")
    history: list[ChatMessage] = Field(default_factory=list, description="历史消息")
    username: str | None = Field(default=None, description="当前登录用户名")
    user_id: str = Field(default="user123", description="用户标识")


# 聊天接口响应体：统一返回状态、时间戳和最终回复。
class ChatResponse(BaseModel):
    status: Literal["ok"] = "ok"
    generated_at: str
    reply: str



@lru_cache(maxsize=32)
def _get_memory_tool(user_id: str) -> MemoryTool:
    return MemoryTool(user_id=user_id)


def _resolve_user_key(payload: ChatRequest) -> str:
    username = (payload.username or '').strip()
    if username:
        return username

    user_id = (payload.user_id or '').strip()
    if user_id:
        return user_id

    return 'anonymous'


def _is_identity_question(text: str) -> bool:
    normalized = text.strip()
    return any(
        phrase in normalized
        for phrase in ("我是谁", "你知道我是谁", "请问我是谁", "我叫什么", "你记得我是谁")
    )


def _extract_explicit_identity(text: str) -> str | None:
    patterns = [
        r"我是([^，。！？、\n\r]{1,30})",
        r"我叫([^，。！？、\n\r]{1,30})",
        r"我的名字是([^，。！？、\n\r]{1,30})",
        r"我的名字叫([^，。！？、\n\r]{1,30})",
        r"我名字叫([^，。！？、\n\r]{1,30})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            if candidate and candidate not in {"谁", "谁呀", "什么", "什么呀"}:
                return candidate
    return None


def _should_store_memory(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    if _is_identity_question(stripped):
        return False

    if _extract_explicit_identity(stripped):
        return True

    preference_markers = ("我喜欢", "我不喜欢", "我常用", "我常去", "我住在", "我来自")
    return any(marker in stripped for marker in preference_markers)


def _is_bad_identity_memory(content: str) -> bool:
    text = content.strip()
    return bool(
        re.search(r"^(我是谁|我是谁呀|你是谁|你知道我是谁|请问我是谁).*$", text)
        or re.search(r"^用户身份：\s*(谁|谁呀|什么|什么呀)\s*$", text)
    )


@lru_cache(maxsize=32)
def _cleanup_bad_identity_memories(user_id: str) -> int:
    memory_tool = _get_memory_tool(user_id)
    candidate_queries = ["我是谁", "用户身份", "谁呀", "你是谁"]
    seen_ids: set[str] = set()
    removed_count = 0

    for query in candidate_queries:
        try:
            memories = memory_tool.memory_manager.retrieve_memories(
                query=query,
                memory_types=["episodic", "semantic"],
                limit=20,
                min_importance=0.0,
            )
        except Exception:
            continue

        for memory in memories:
            if memory.id in seen_ids:
                continue
            if not _is_bad_identity_memory(memory.content):
                continue

            seen_ids.add(memory.id)
            try:
                if memory_tool.memory_manager.remove_memory(memory.id):
                    removed_count += 1
            except Exception:
                continue

    return removed_count


def _store_user_memory(memory_tool: MemoryTool, user_message: str) -> int:
    text = user_message.strip()
    if not text:
        return 0

    stored_count = 0

    if not _should_store_memory(text):
        return 0

    # 先存原句，使用 episodic 才会真正落到持久化存储（SQLite + Qdrant）。
    memory_tool.execute("add", content=text, importance=0.7, memory_type="episodic")
    stored_count += 1

    # 再把“我是X / 我叫X / 我的名字是X / 我的名字叫X”规范成结构化记忆，提升后续检索命中率。
    explicit_identity = _extract_explicit_identity(text)
    if explicit_identity:
        normalized = f"用户身份：{explicit_identity}"
        memory_tool.execute("add", content=normalized, importance=0.9, memory_type="episodic")
        stored_count += 1

    return stored_count


def _build_chat_messages(payload: ChatRequest) -> list[dict[str, str]]:
    # 把前端消息、历史和长期记忆整理成大模型标准 messages 格式。
    memory_tool = _get_memory_tool(payload.user_id)
    if _is_identity_question(payload.message):
        memory_context = memory_tool.get_context_for_query("用户身份", limit=5)
        system_prompt = (
            "你是一个简洁、自然、友好的中文助手，回答要准确、直接。"
            "如果用户在问‘我是谁’这类身份问题，只能根据明确的身份记忆回答；"
            "如果记忆中存在冲突，优先说‘我目前记得你曾说过X’，不要编造。"
        )
    else:
        memory_context = memory_tool.get_context_for_query(payload.message, limit=3)
        system_prompt = "你是一个简洁、自然、友好的中文助手，回答要准确、直接。"

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "system",
            "content": f"你可以参考下面的长期记忆，但不要编造不存在的信息：\n{memory_context}",
        },
    ]

    for item in payload.history:
        messages.append({"role": item.role, "content": item.content})

    messages.append({"role": "user", "content": payload.message})
    return messages


def _parse_location_value(location_value: Any) -> tuple[float, float] | None:
    # 高德返回的位置字段可能是字符串、数组或者字典，这里做兼容解析。
    if isinstance(location_value, str) and "," in location_value:
        parts = [part.strip() for part in location_value.split(",")]
        if len(parts) >= 2:
            try:
                return float(parts[0]), float(parts[1])
            except ValueError:
                return None

    if isinstance(location_value, (list, tuple)) and len(location_value) >= 2:
        try:
            return float(location_value[0]), float(location_value[1])
        except (TypeError, ValueError):
            return None

    if isinstance(location_value, dict):
        try:
            return float(location_value.get("lng")), float(location_value.get("lat"))
        except (TypeError, ValueError):
            return None

    return None


def _extract_route_payload(plan_text: str) -> tuple[str, dict[str, Any] | None]:
    # 模型输出里最后可能带一段 ROUTE_JSON，用来单独提取路线数据。
    marker = "ROUTE_JSON:"
    marker_index = plan_text.rfind(marker)
    if marker_index == -1:
        return plan_text.strip(), None

    clean_text = plan_text[:marker_index].strip()
    payload_text = plan_text[marker_index + len(marker):].strip()

    if payload_text.startswith("```"):
        payload_text = re.sub(r"^```(?:json)?\s*", "", payload_text, count=1).strip()
        payload_text = re.sub(r"\s*```$", "", payload_text).strip()

    try:
        return clean_text, json.loads(payload_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", payload_text, re.DOTALL)
        if not match:
            return clean_text, None
        try:
            return clean_text, json.loads(match.group(0))
        except json.JSONDecodeError:
            return clean_text, None


def _build_route_points_from_payload(payload_data: dict[str, Any] | None) -> list[dict[str, Any]]:
    # 把模型输出里的 JSON 路线点，整理成前端地图更容易用的格式。
    if not isinstance(payload_data, dict):
        return []

    raw_points = payload_data.get("route_points")
    if not isinstance(raw_points, list):
        return []

    route_points: list[dict[str, Any]] = []
    for index, point in enumerate(raw_points):
        if not isinstance(point, dict):
            continue

        try:
            lat = float(point.get("lat"))
            lng = float(point.get("lng"))
        except (TypeError, ValueError):
            continue

        route_points.append(
            {
                "day": int(point.get("day", index // 3 + 1)),
                "title": str(point.get("title", f"地点 {index + 1}")),
                "subtitle": str(point.get("subtitle", "行程点")),
                "time": str(point.get("time", "09:00")),
                "lat": lat,
                "lng": lng,
                "note": str(point.get("note", "")),
                "province": str(point.get("province", "")),
                "city": str(point.get("city", "")),
                "district": str(point.get("district", "")),
            }
        )

    return route_points


def _build_fallback_route_points(destination: str, location_info: dict[str, Any], days: int) -> list[dict[str, Any]]:
    # 如果模型没有给出可用路线，就直接从高德 POI 里构造一个兜底路线。
    pois = location_info.get("pois", []) if isinstance(location_info, dict) else []
    if not isinstance(pois, list):
        pois = []

    time_slots = ["09:00", "11:30", "14:30", "17:30", "19:00"]
    route_points: list[dict[str, Any]] = []

    for index, poi in enumerate(pois[: max(6, days * 2)]):
        if not isinstance(poi, dict):
            continue

        location_value = _parse_location_value(poi.get("location"))
        if location_value is None:
            continue

        lng, lat = location_value
        route_points.append(
            {
                "day": min(days, index // 2 + 1),
                "title": str(poi.get("name") or destination),
                "subtitle": str(poi.get("type") or "周边地点"),
                "time": time_slots[index % len(time_slots)],
                "lat": lat,
                "lng": lng,
                "note": str(poi.get("address") or "由高德 POI 动态生成"),
            }
        )

    return route_points


def format_sse(event: str, data: Any) -> str:
    # 统一封装 SSE 文本格式，前端可以按 event/data 解析。
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def build_trip_plan_response(payload: TripPlanRequest) -> TripPlanResponse:
    # 同步模式：先生成文本行程，再抽取路线，再补充地图 POI。
    llm = create_llm()
    planner = TravelPlanner(llm=llm)
    plan_text = planner.plan(
        payload.destination,
        str(payload.days),
        str(payload.budget),
        payload.preferences,
        stream=False,
    )

    # 从返回文本里拆出纯文本和路线 JSON。
    clean_plan_text, route_payload = _extract_route_payload(str(plan_text))

    # 用高德地图补充真实地理信息。
    map_tool = MapTool()
    location_info = map_tool.get_location(payload.destination, "景点,餐饮,酒店,地铁站")
    poi_count = len(location_info.get("pois", [])) if isinstance(location_info, dict) else 0
    route_points = _build_route_points_from_payload(route_payload)
    if not route_points:
        route_points = _build_fallback_route_points(payload.destination, location_info, payload.days)

    # 组装最终返回对象。
    return TripPlanResponse(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        destination=payload.destination,
        days=payload.days,
        budget=payload.budget,
        preferences=payload.preferences,
        plan_text=clean_plan_text,
        plan_char_count=len(clean_plan_text),
        poi_count=poi_count,
        route_points=route_points,
        location_info=location_info,
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    # 健康检查接口，用来确认 Python 服务是否在线。
    return {"status": "ok", "service": "travel-agent-api"}


@app.post("/api/trips/plan", response_model=TripPlanResponse)
def create_trip_plan(payload: TripPlanRequest) -> TripPlanResponse:
    # 非流式版本：一次性返回完整行程。
    return build_trip_plan_response(payload)


@app.post("/api/trips/plan/stream")
def stream_trip_plan(payload: TripPlanRequest):
    def event_stream():
        # 先发一个 meta 事件，让前端知道请求已经开始。
        yield format_sse(
            "meta",
            {
                "status": "started",
                "destination": payload.destination,
                "days": payload.days,
                "budget": payload.budget,
                "preferences": payload.preferences,
            },
        )

        # 生成器式流输出：边生成边推给前端。
        llm = create_llm()
        planner = TravelPlanner(llm=llm)
        chunks: list[str] = []
        route_emitted = False

        try:
            # 逐块输出模型文本。
            for chunk in planner.stream_plan(
                payload.destination,
                str(payload.days),
                str(payload.budget),
                payload.preferences,
            ):
                chunks.append(chunk)
                yield format_sse("chunk", {"text": chunk})

            # 流结束后，把完整文本拼起来，尝试解析路线 JSON。
            plan_text = "".join(chunks)
            clean_plan_text, route_payload = _extract_route_payload(plan_text)
            route_points = _build_route_points_from_payload(route_payload)

            # 如果模型成功输出了路线点，就额外发一个 route 事件。
            if route_points and not route_emitted:
                route_emitted = True
                yield format_sse("route", {"route_points": route_points})

            # 再补一次高德 POI，确保前端至少能拿到真实地点信息。
            map_tool = MapTool()
            location_info = map_tool.get_location(payload.destination, "景点,餐饮,酒店,地铁站")
            poi_count = len(location_info.get("pois", [])) if isinstance(location_info, dict) else 0
            if not route_points:
                route_points = _build_fallback_route_points(payload.destination, location_info, payload.days)

            # 最后发 done，表示整轮行程生成完成。
            final_payload = TripPlanResponse(
                generated_at=datetime.now().isoformat(timespec="seconds"),
                destination=payload.destination,
                days=payload.days,
                budget=payload.budget,
                preferences=payload.preferences,
                plan_text=clean_plan_text,
                plan_char_count=len(clean_plan_text),
                poi_count=poi_count,
                route_points=route_points,
                location_info=location_info,
            )
            yield format_sse("done", final_payload.model_dump())
        except Exception as exc:
            # 出错时直接发 error，前端可以据此显示失败原因。
            yield format_sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/chat/stream")
def stream_chat(payload: ChatRequest):
    def event_stream():
        # 先通知前端：聊天生成开始了。
        yield format_sse(
            "meta",
            {
                "status": "started",
                "message": payload.message,
                "history_count": len(payload.history),
            },
        )

        # 聊天接口只做一件事：把消息送给大模型并把输出流式返回。
        llm = create_llm()
        memory_tool = _get_memory_tool(payload.user_id)
        cleaned_count = _cleanup_bad_identity_memories(payload.user_id)
        if cleaned_count:
            print(f"已清理错误身份记忆 {cleaned_count} 条。")
        print("接收到聊天请求，消息内容：", payload.message)
        stored_count = _store_user_memory(memory_tool, payload.message)
        print(f"本轮已写入长期记忆 {stored_count} 条。")
        messages = _build_chat_messages(payload)
        print("大模型输入消息：", messages)
        reply_chunks: list[str] = []

        try:
            # 如果 LLM 支持流式接口，就一边生成一边推给前端。
            if hasattr(llm, "stream_invoke"):
                for chunk in llm.stream_invoke(messages):
                    chunk_text = str(chunk)
                    reply_chunks.append(chunk_text)
                    yield format_sse("chunk", {"text": chunk_text})
            else:
                # 不支持流式时，就一次性调用，再当作一个 chunk 返回。
                reply_text = str(llm.invoke(messages))
                reply_chunks.append(reply_text)
                yield format_sse("chunk", {"text": reply_text})

            # 生成完毕后，拼成完整回复并发 done。
            final_payload = ChatResponse(
                generated_at=datetime.now().isoformat(timespec="seconds"),
                reply="".join(reply_chunks),
            )

            user_key = _resolve_user_key(payload)
            conversation_id = getattr(memory_tool,"conversation_count",0)

            memory_tool.execute(
            "add",
            content=f"对话 - 用户: {payload.message}\n对话 - 助手: {final_payload.reply}",
            importance=0.85,
            memory_type="episodic",
            metadata={
                "type": "interaction",
                "conversation_id": conversation_id,
                "username": user_key,
            },
        )

            yield format_sse("done", final_payload.model_dump())
        except Exception as exc:
            # 任何异常都通过 error 事件返回给前端。
            yield format_sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# 拉取聊天历史接口：根据用户名查询长期记忆，返回相关对话记录。
@app.get("/api/chat/history")
def chat_history(username: str, page: int = 1, page_size: int = 20):
    user_key = (username or "").strip() or "anonymous"
    memory_tool = _get_memory_tool(user_key)

    memories = memory_tool.memory_manager.retrieve_memories(
        query="对话",
        memory_types=["working", "episodic"],
        limit=page_size,
        min_importance=0.0,
    )

    items = []
    for memory in memories:
        items.append({
            "id": memory.id,
            "role": "assistant" if memory.metadata.get("type") == "assistant_response" else "user",
            "content": memory.content,
            "timestamp": memory.timestamp.isoformat(timespec="seconds"),
        })

    return {
        "username": user_key,
        "items": items,
    }