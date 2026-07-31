# 在 langChain 框架内，使用 deepseek 模型，对于标准化输出，也就是 response_format 参数的支持度是不太够的。

import os

from langchain.agents import create_agent


def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"{city}的天气是晴朗的，温度25°C。"


def run_agent():
    print("run agent")
    # 1. 创建智能体（DeepSeek 不支持 response_format，去掉）
    agent = create_agent(
        model=os.getenv("DEEPSEEK_MODEL"),
        tools=[get_weather],
        system_prompt="你是一个乐于助人的天气助手，可以查询全球城市的天气。",
    )

    # 2. 运行智能体
    result = agent.invoke({"messages": [{"role": "user", "content": "我想知道上海今天的天气怎么样？"}]})

    print(result["messages"][-1].content_blocks)
