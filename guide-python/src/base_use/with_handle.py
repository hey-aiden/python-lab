# with 关键字：自动资源管理
#
# 机制：with obj as x:
#   1. x = obj.__enter__()   ← 进入时获取资源
#   2. 执行 with 块内的代码
#   3. obj.__exit__(...)     ← 离开时释放资源（即使抛了异常也会执行）
#
# 任何实现了 __enter__ + __exit__ 的对象都能用 with

import time
from pathlib import Path


def use_with():
    """演示 with 的常见场景。"""
    with_file()
    # with_nested_files()
    # with_custom()


def with_file():
    """场景 1：文件读取 — 自动关闭。

    with 离开时自动 f.close()，不用 try-finally。
    """
    print("=== with file ===")
    with open("test.txt", "w") as f:
        f.write("hello with")
    # 到这里文件已关闭

    with open("test.txt", "r") as f:
        print(f.read())  # "hello with"


def with_nested_files():
    """场景 2：同时打开多个文件。

    用逗号分隔多个 with 对象，所有文件在离开时一起关闭。
    """
    print("=== with nested ===")
    with open("test.txt", "r") as src, open("copy.txt", "w") as dst:
        dst.write(src.read())
    print("done copy")


def with_custom():
    """场景 3：自定义上下文管理器。

    实现 __enter__ / __exit__，任何对象都能用 with。
    """

    class Timer:
        """计时器 — with 块结束时打印耗时。"""

        def __enter__(self):
            self.start = time.time()
            return self  # return 的值赋给 as 后面的变量

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.time() - self.start
            print(f"耗时: {elapsed:.3f}s")
            return False  # False = 不吞异常，让异常继续传播

    print("=== with custom ===")
    with Timer():
        total = sum(range(1_000_000))
        print(f"sum: {total}")
    # 自动打印耗时


# ─── pathlib：文件路径处理 ───
#
# Python 的 pathlib（标准库）对标 Node.js 的 path 模块。
# 用 / 拼接路径，比 os.path.join("a", "b") 更直观。


def use_pathlib():
    """演示 pathlib 操作：拼接、读取、写入。

    不需要手动 join——直接用 / 运算符拼接即可。
    Path 对象可以传进 open()，字符串和 Path 都能工作。
    """

    base = Path(".")  # 当前目录

    # 拼接路径 — 用 / 运算符
    file = base / "test.txt"
    print("path:", file)  # test.txt
    print("name:", file.name)  # test.txt
    print("suffix:", file.suffix)  # .txt
    print("parent:", file.parent)  # .
    print("absolute:", file.resolve())

    # 一步到位：读 / 写（不需要 open）
    if file.exists():
        content = file.read_text()
        print("content:", content)

    out = base / "output.txt"
    out.write_text("hello from pathlib")
    print("wrote to:", out.name)


# ─── 其他常见 with 场景（概念展示） ───
#
# 线程锁 — 自动 acquire + release
#   with threading.Lock():
#       shared_data += 1
#
# HTTP 客户端 — 自动断开连接
#   with httpx.Client() as client:
#       resp = client.get("https://api.example.com")
#
# contextlib 装饰器 — 把生成器快速变成上下文管理器
#   from contextlib import contextmanager
#   @contextmanager
#   def temp_dir():
#       import tempfile, shutil
#       d = tempfile.mkdtemp()
#       try:
#           yield d
#       finally:
#           shutil.rmtree(d)
