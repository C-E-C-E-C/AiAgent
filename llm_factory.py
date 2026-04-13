import os
from pathlib import Path

from hello_agents import HelloAgentsLLM


# 读取本项目目录下的 .env 文件，并把配置放进环境变量。
# 这样后续代码统一用 os.getenv 取值，避免到处硬编码。
def load_env_file(env_path: str = ".env") -> None:
    env_file = Path(__file__).with_name(env_path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# 统一创建大模型客户端。
# 这里把模型名、Key、Base URL、温度、token 上限都集中在一个地方管理。
def create_llm() -> HelloAgentsLLM:
    load_env_file()
    return HelloAgentsLLM(
        # 模型名，例如 qwen-plus、gpt-4o-mini 等。
        model=os.getenv("OPENAI_MODEL", "qwen-plus"),
        # API Key 优先读 OPENAI_API_KEY，兼容旧变量 LLM_API_KEY。
        api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY"),
        # 服务地址，例如通义千问兼容模式、OpenAI 官方地址等。
        base_url=os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        # provider 只用于标识模型供应商，方便上层统一处理。
        provider=os.getenv("LLM_PROVIDER", "qwen"),
        # 温度越低越稳定，越高越发散。
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        # 控制单次输出的最大 token 数。
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "32666")),
        # 请求超时时间，避免接口卡死。
        timeout=int(os.getenv("LLM_TIMEOUT", "120")),
        # 默认启用流式输出，便于前端一边生成一边展示。
        stream=True
    )