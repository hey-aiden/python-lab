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

FIRE_DIE = Path(".") / "assets"


def use_file():
    """演示 with 的常见场景。"""
    use_open()
    # with_file()
    # with_nested_files()
    # with_custom()


# File 操作： open(file, mode='r') - 使用 open() 方法一定要保证关闭文件对象，即调用 close() 方法
# 通过 open() 函数，可以创建 file 对象，用于对文件进行操作
#
# ⚠️ Linter 会提示 "Use a context manager for opening files"，原因：
#   1. file 对象实现了 __enter__ / __exit__，天生支持 with 语句
#   2. 手动 try-finally 虽然功能正确，但：
#      - 容易忘记写 finally 块或忘记调用 close()
#      - open() 成功但 try 之前如果抛异常（虽然罕见），文件句柄会泄漏
#      - 代码冗长，不如 with open(...) as f: 简洁
#   3. with 保证无论正常退出、return、break、continue 还是异常，__exit__ 都会执行
#   4. 这是 Python 的惯用写法（Pythonic），linter 强制推荐
#
#   对比写法（等价且更安全）：
#     with open(filePath, "r") as fileHandler:
#         content = fileHandler.read()
#         print(content)
def use_open():
    filePath = FIRE_DIE / "test.txt"
    # "r+" = 读写模式（不截断，从文件开头开始），区别于 "w"（先清空）和 "a"（强制追加）
    fileHandler = open(filePath, "r+")  # linter 警告：建议改用 with open(...)
    try:
        content = fileHandler.read()
        print(content)
        contentLen = len(content)
        print(contentLen, "打印文本内容")
        # seek(contentLen) → 跳到文件末尾（EOF），后续 write 等价于追加
        #
        # ❓ 如果 seek(contentLen + 1) 越过 EOF 再 write，gap 为什么用 \x00 填充而不是空格？
        #    这是 POSIX 文件系统行为，不是 Python 特有的：
        #    1. 文件系统只认字节，不区分"文本"和"二进制" → \x00 是字节的"零值默认"
        #    2. 越过 EOF 写入会创建稀疏文件（sparse file）：
        #       - 内核不为空洞（hole）分配磁盘块，只记录逻辑文件大小
        #       - 读取空洞区域时，内核直接返回全零字节
        #    3. 如果用空格（0x20）填充，对二进制文件（图片、压缩包等）就毫无意义
        #    4. C 标准 fseek / POSIX lseek 都有同样的语义，Python 只是继承
        #
        #    示例：文件 "hello"(5字节) → seek(8) → write("X")
        #          结果：h e l l o \x00 \x00 \x00 X  （3 个 null 填充 gap）
        fileHandler.seek(contentLen)
        # 当前 seek 到 EOF（contentLen 位置），没有越过，所以 write 直接在末尾追加，无 null 填充
        fileHandler.write("update after use open api")
    finally:
        fileHandler.close()


# ─── 边界情况处理策略 ───
# seek 越过 EOF 再写入产生 null 填充的问题，常见处理方式：
#
# 策略 1：避免越过 EOF — 先获取文件大小，不越界
#   file.seek(0, 2)             # 跳到 EOF（whence=2 末尾）
#   file_size = file.tell()      # 获取当前文件大小
#   file.seek(min(target_pos, file_size))  # 不越过 EOF
#
# 策略 2：追加用 "a" 模式，系统保证每次 write 前自动 seek 到 EOF
#   with open(path, "a") as f:
#       f.write("always at end")
#
# 策略 3：原地插入/替换 — 用临时文件 + shutil.move，比 seek + write 安全得多
#   import shutil, tempfile
#   with open(src, "r") as fin, tempfile.NamedTemporaryFile("w", delete=False) as fout:
#       for line in fin:
#           fout.write(line.replace("old", "new"))  # 逐行处理，适合大文件
#   shutil.move(fout.name, src)  # 原子替换
#
# 策略 4：truncate() 控制大小 — 写完后截断多余内容
#   file.seek(insert_pos)
#   file.write(new_data)
#   file.truncate()  # 截断到当前位置，丢掉后面的旧数据
#
# 策略 5：小文件直接读写（读-改-写模式），最简单
#   content = Path(path).read_text()
#   Path(path).write_text(content + "append")
#
# 策略 6：显式填充（特殊场景） — 预先用空格或任意字符填充 gap
#   gap = target_pos - file.tell()
#   file.write(" " * gap)  # 用空格代替 null


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
