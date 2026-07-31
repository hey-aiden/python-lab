from langchain_deepseek import ChatDeepSeek


def ai_chat():
    # 2. 初始化 DeepSeek 模型
    # model 参数可以是 "deepseek-chat" (非思考模式) 或 "deepseek-reasoner" (思考模式)
    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0.7,
    )
    # 3. 发起提问并打印结果
    response = llm.invoke("今天天气怎么样？🌦️")
    print(response.content)
