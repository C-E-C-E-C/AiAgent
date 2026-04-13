class TravelPlanner:
    def __init__(self, llm=None):
        from llm_factory import create_llm

        # 外部传进来的 llm 优先使用；没传就自己创建一个默认实例。
        self.llm = llm or create_llm()

    def clean_text(self, text):
        # 把可能带有编码问题的文本清洗一下，避免输出乱码。
        return text.encode("utf-8", "ignore").decode("utf-8", "ignore")

    def build_prompt(self, destination, days, budget, preferences):
        # 把用户输入包装成一段完整提示词，明确告诉模型要输出什么。
        return f"""
你是专业旅行规划师。
目的地：{destination}
天数：{days}
预算：{budget}
偏好：{preferences}

请生成：
1. 每日行程，必须结合目的地真实地名和街区
2. 每个地点要给出可用于地图的经纬度,必须真实！
3. 路线中至少包含 6 个点位，尽量覆盖景点、酒店等
4. 生成的地点必须有名气！！！
4. 总预算明细
5. 返回的数据中必须包含省市区的信息。

输出要求：
- 先输出自然语言行程正文
- 最后一行必须输出 `ROUTE_JSON:`，后面紧跟严格 JSON
- JSON 格式：
    {{
        "route_points": [
            {{"day": 1, "title": "", "subtitle": "文庙", "time": "09:00", "lat": 0.0, "lng": 0.0, "note": "...",
            "province" : "云南", "city": "昆明","district":"五华区"}}
        ]
    }}
- 不要输出 Markdown 代码块，不要输出额外解释
"""

    def llm_chat(self, prompt, stream: bool = False):
        # 统一把 prompt 转成 messages 格式，符合 Chat Completions 风格。
        messages = [
            {"role": "system", "content": "你是专业旅行规划师，擅长生成清晰、可执行、预算合理的中文旅行方案。"},
            {"role": "user", "content": self.clean_text(prompt)},
        ]

        # 如果支持流式输出，就边生成边打印。
        if stream and hasattr(self.llm, "stream_invoke"):
            chunks = []
            for chunk in self.llm.stream_invoke(messages):
                print(chunk, end="", flush=True)
                chunks.append(chunk)
            print()
            return "".join(chunks)

        # 不支持流式时，就一次性返回完整结果。
        return self.llm.invoke(messages)

    def plan(self, destination, days, budget, preferences, stream: bool = False):
        # 对外最常用的入口：输入旅行参数，输出完整行程文本。
        return self.llm_chat(self.build_prompt(destination, days, budget, preferences), stream=stream)

    def stream_plan(self, destination, days, budget, preferences):
        # 给 SSE / 前端流式展示用的版本，逐块 yield 模型输出。
        prompt = self.build_prompt(destination, days, budget, preferences)
        messages = [
            {"role": "system", "content": "你是专业旅行规划师，擅长生成清晰、可执行、预算合理的中文旅行方案。"},
            {"role": "user", "content": self.clean_text(prompt)},
        ]

        # 优先走模型自带的流式接口。
        if hasattr(self.llm, "stream_invoke"):
            for chunk in self.llm.stream_invoke(messages):
                yield chunk
            return

        # 如果模型不支持流式，就退回到一次性输出。
        yield self.llm.invoke(messages)