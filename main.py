import os

from dotenv import load_dotenv


# 先加载本地 .env，这样后面的 LLM / 地图 / 记忆模块都能直接读取配置。
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# 主流程里用到的能力：PDF 导出、智能体、记忆、LLM、地图、行程规划、上下文构建。
from exporter import Exporter
from hello_agents import SimpleAgent, ToolRegistry
from hello_agents.tools import MemoryTool
from llm_factory import create_llm
from map_tool import MapTool
from planner import TravelPlanner
from SimpleContextBuilder import SimpleContextBuilder

# 控制台启动提示，让用户知道程序已经开始运行。
print("=" * 50)
print("欢迎使用智能旅行助手！")
print("=" * 50)


# 这里先直接从命令行收集最核心的旅行参数。
# 这四个字段就是后续生成行程时最基础的输入。
destination = input("请输入旅行目的地：")
days = input("请输入旅行天数：")
budget = input("请输入旅行预算：")
preferences = input("请输入旅行偏好（如：文化、美食、自然等）：")


# 整个程序共用一个 LLM 实例，避免重复初始化。
llm = create_llm()

# 创建一个简单智能体对象，后面可以挂载工具。
agent = SimpleAgent(name="travel_assistant", llm=llm)



# 记忆模块：让智能体具备“记住用户”的能力。
username = input("请输入用户名，用于区分向量数据库中的记忆：")
# MemoryTool 会根据 user_id 去读取 / 写入长期记忆，这里直接使用用户名。
memory_tool = MemoryTool(user_id=username or "anonymous")
tool_registry = ToolRegistry()
tool_registry.register_tool(memory_tool)
agent.tool_registry = tool_registry

# 这里预留一个聊天历史列表，后面如果改成多轮对话，可以直接往这里追加。
chat_history = []



# 行程规划器：根据目的地、天数、预算、偏好生成完整旅行方案。
planner = TravelPlanner(llm=llm)

# 先输出自然语言版行程正文。
print("\n生成的旅行计划：")
plan_result = planner.plan(destination, days, budget, preferences, stream=True)

print("\n")

# 调用高德地图工具，拉取目的地附近的真实 POI 信息。
map_tool = MapTool()
location = map_tool.get_location(destination, "景点,餐饮,酒店")
print("\n目的地相关景点信息：", location)

# 最后把生成结果导出为 PDF，方便保存和交付。
exporter = Exporter()
exporter.export_pdf(plan_result)

print("\n 行程完成，导出为pdf")