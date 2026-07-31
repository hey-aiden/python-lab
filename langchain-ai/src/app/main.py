from dotenv import load_dotenv

# from .chat import ai_chat
from .agent import run_agent

# 入口文件调用一次就够了，后续其他地方，只需要通过 os.getenv(key)就能拿到环境变量
load_dotenv()


def start():
    print("chat start")
    # ai_chat()
    run_agent()
