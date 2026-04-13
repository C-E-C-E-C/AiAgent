import os
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP


# 这个函数和其它入口文件一致：先把 .env 读进来，方便后面取配置。
def load_env_file(env_path: str = ".env") -> None:
    env_file = Path(__file__).with_name(env_path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


# 启动前先加载环境变量，这样 MCP 工具内部也能直接读到配置。
load_env_file()

# 创建一个 MCP 服务实例，名字就是 travel-agent。
mcp = FastMCP("travel-agent")


def build_prompt(prompt: str) -> list[dict[str, str]]:
    # 把用户输入包装成标准 Chat 消息格式。
    return [
        {
            "role": "system",
            "content": "你是专业旅行规划师，擅长生成清晰、可执行、预算合理的中文旅行方案。",
        },
        {"role": "user", "content": prompt},
    ]


# 暴露给 MCP 客户端调用的工具函数。
@mcp.tool()
def llm_chat(prompt: str) -> str:
    # 这些配置都来自 .env 或环境变量。
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # 没有 Key 就直接报错，避免发出无效请求。
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY 或 LLM_API_KEY，无法调用大模型")

    # 直接调用 OpenAI 兼容接口的 chat/completions。
    response = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": build_prompt(prompt),
            "temperature": 0.7,
        },
        timeout=60,
    )
    response.raise_for_status()

    # 把返回 JSON 拿出来，继续向下解析模型回答。
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"大模型返回为空：{data}")

    # OpenAI 兼容接口里，真正的文本在 choices[0].message.content。
    message = choices[0].get("message", {})
    content = message.get("content")
    if not content:
        raise RuntimeError(f"大模型响应缺少 content：{data}")

    return content


if __name__ == "__main__":
    # 直接运行这个文件时，就启动 MCP 服务。
    mcp.run()