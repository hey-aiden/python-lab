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
    MODEL = ChatDeepSeek(
        model=os.getenv("DEEPSEEK_MODEL"),
        temperature=0.7,
    )
    agent = create_agent(
        model=MODEL,
        system_prompt="你是一个友好助人的AI助手",
    )

    # thread_id → message_list 映射表，替代 MemorySaver 实现会话隔离
    sessions: dict[str, list] = {}

    def get_session(session_id: str) -> list:
        """获取或创建 session 对应的 message_list"""
        if session_id not in sessions:
            sessions[session_id] = []
            print(f"📂 新建会话: {session_id}")
        return sessions[session_id]

    # 当前会话
    current_id = "default"
    message_list = get_session(current_id)

    while True:
        prompt = f"\n[{current_id}] 你: "
        user_msg = input(prompt)

        if user_msg.lower() in ["exit", "quit", "退出"]:
            print("👋 再见！")
            break

        if not user_msg.strip():
            continue

        # 切换会话命令
        if user_msg.startswith("/switch "):
            target_id = user_msg[len("/switch "):].strip()
            if target_id not in sessions:
                print(f"⚠️  会话 '{target_id}' 不存在，创建新会话")
            current_id = target_id
            message_list = get_session(current_id)
            continue

        # 查看所有会话
        if user_msg == "/sessions":
            print("当前会话列表：")
            for sid, msgs in sessions.items():
                marker = " ←" if sid == current_id else ""
                print(f"  {sid}: {len(msgs)} 条消息{marker}")
            continue

        message_list.append({"role": "user", "content": user_msg})

        try:
            result = agent.invoke({"messages": message_list})
            ai_response = result["messages"][-1].content

            # 追加 AI 消息
            message_list.append({"role": "assistant", "content": ai_response})

            print(f"🤖 助手：{ai_response}")
        except (KeyboardInterrupt, SystemExit):
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
