# 构建一个终端机器人

import os

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver


def create_robot():
    print("create_robot")

    # 启动终端交互
    print("🤖 你好！我是你的DeepSeek助手。输入 'exit' 或 'quit' 可以结束对话。")
    print("-" * 50)

    # use_message_list()
    use_memory()


def use_message_list():
    # 初始化 DeepSeek 模型
    MODEL = ChatDeepSeek(
        model=os.getenv("DEEPSEEK_MODEL"),
        temperature=0.7,
    )
    # 创建智能体
    agent = create_agent(
        model=MODEL,
        system_prompt="你是一个友好助人的AI助手",
    )
    message_list = []

    while True:
        # 获取用户输入内容
        user_msg = input("\n你:")

        # 检查退出条件
        if user_msg.lower() in ["exit", "quit", "退出"]:
            print("👋 再见！")
            break

        # 用户未输入则跳过 -  # 去掉首尾空白 → 如果结果为空
        if not user_msg.strip():
            continue

        message_list.append({"role": "user", "content": user_msg})

        try:
            result = agent.invoke({"messages": message_list})
            # 提取助手的回复
            ai_response = result["messages"][-1].content

            # 追加AI消息
            message_list.append({"role": "assistant", "content": ai_response})

            print(f"🤖 助手：{ai_response}")
        except (KeyboardInterrupt, SystemExit):
            # 用户主动退出，向上抛出让外层处理
            raise
        except Exception as e:  # noqa: BLE001 — 终端机器人需要兜底，不能因单次 API 调用异常而退出
            print(f"❌ 出错了：{e}")


def use_memory():
    MODEL = ChatDeepSeek(
        model=os.getenv("DEEPSEEK_MODEL"),
        temperature=0.7,
    )

    # MemorySaver 自动持久化对话历史，无需手动维护 message_list
    agent = create_agent(
        model=MODEL,
        system_prompt="你是一个友好助人的AI助手",
        checkpointer=MemorySaver(),
    )

    # 同一 thread_id 共享记忆，不同会话用不同 id
    config = {"configurable": {"thread_id": "session-1"}}

    while True:
        user_msg = input("\n你:")

        if user_msg.lower() in ["exit", "quit", "退出"]:
            print("👋 再见！")
            break

        if not user_msg.strip():
            continue

        try:
            # 每次只传当前消息，历史由 MemorySaver 自动注入
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_msg}]},
                config=config,
            )
            ai_response = result["messages"][-1].content
            print(f"🤖 助手：{ai_response}")
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # noqa: BLE001 — 终端机器人需要兜底，不能因单次 API 调用异常而退出
            print(f"❌ 出错了：{e}")
