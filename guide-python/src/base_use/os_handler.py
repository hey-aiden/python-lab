import os


def os_use() -> int:
    pwdPath = os.getcwd()
    print("当前执行目录：", pwdPath)
    return 1
