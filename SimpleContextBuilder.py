# simple_context_builder.py
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional

# 提前加载环境变量，确保记忆模块和大模型配置都能读取到 .env。
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from hello_agents.tools import MemoryTool


class SimpleContextBuilder:
    """极简上下文构建器（初学者版）"""
    def __init__(self, user_id: str = "user123"):
        # 这里的 MemoryTool 是长期记忆入口，会去连 Qdrant / Neo4j。
        self.memory_tool = MemoryTool(user_id=user_id)
        
        # 对话历史：保存最近几轮内容，属于短期记忆。
        self.chat_history: List[str] = []
        # 结构化笔记：把任务过程中提炼出的重要信息单独保存下来。
        self.notes: List[dict] = []

    def _gather(self, user_query: str) -> str:
        """Gather阶段：先把所有可用上下文收集起来。"""
        # 1. 从长期记忆里检索与当前问题最相关的内容。
        memory_context = self.memory_tool.get_context_for_query(user_query, limit=3)
        # 2. 取最近 3 条对话，避免把过长历史全塞进 prompt。
        recent_history = "\n".join(self.chat_history[-3:]) if self.chat_history else "无"
        # 3. 取最近的结构化笔记，方便保留任务关键信息。
        note_context = "\n".join([f"[{n['type']}] {n['content']}" for n in self.notes[-3:]]) if self.notes else "无"
        
        return f"""
【长期记忆】
{memory_context}

【最近对话】
{recent_history}

【任务笔记】
{note_context}
"""

    def _select(self, context: str, max_tokens: int = 4000) -> str:
        """Select阶段：做最简单的内容筛选，防止上下文过长。"""
        # 这里没有做复杂压缩，先用字符长度模拟 token 截断。
        if len(context) <= max_tokens:
            return context
        return context[:max_tokens] + "\n[... 内容已精简，仅保留关键信息 ...]"

    def _structure(self, user_query: str, context: str) -> str:
        """Structure阶段：把收集到的信息整理成模型更容易理解的格式。"""
        return f"""
【角色】你是一个有记忆的AI助手，只根据提供的信息回答，不编造内容。
【任务】{user_query}
【上下文信息】
{context}
【输出要求】用简洁、准确的语言回答，只说和问题相关的内容。
"""

    def build(self, user_query: str) -> str:
        """完整 GSSC 流水线：收集 → 筛选 → 结构化。"""
        # 1. 先收集上下文。
        gathered = self._gather(user_query)
        # 2. 再做简单筛选。
        selected = self._select(gathered)
        # 3. 最后组织成适合大模型输入的结构。
        structured = self._structure(user_query, selected)
        return structured

    def add_note(self, note_type: str, content: str):
        """把任务中提炼出的关键信息存成结构化笔记。"""
        self.notes.append({
            "type": note_type,
            "content": content,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def update_history(self, user_input: str, ai_response: str):
        """把当前轮的用户输入和 AI 回复都写入短期历史。"""
        self.chat_history.append(f"用户：{user_input}")
        self.chat_history.append(f"AI：{ai_response}")