# with 关键字 — 上下文管理器

"""
with 语句用于自动管理资源（如文件、网络连接、数据库连接等）。
无论代码块是否发生异常，退出 with 块时都会自动执行清理操作（如关闭文件）。

with语句的优势：
1. 自动资源释放：确保资源在使用后被正确关闭
2. 代码简洁：减少样板代码
3. 异常安全：即使在代码块中发生异常，资源也会被正确释放
4. 可读性强：明确标识资源的作用域

语法：
    with 表达式 as 变量:
        代码块

等价于手动写 try/finally，但更简洁、更安全。
"""

# ── 传统写法（try/finally）────────────────────────────
# 缺点：需要手动调用 close()，容易忘记
# 注意：运行前需确保 1.txt 文件存在，否则抛出 FileNotFoundError
try:
    file = open("1.txt", "r")
    try:
        content = file.read()
        print("传统写法读取内容:", content)
    finally:
        file.close()  # 无论是否报错，都必须手动关闭
except FileNotFoundError:
    print("传统写法: 文件 1.txt 不存在")


# ── with 写法（推荐）─────────────────────────────────
# 退出 with 块时自动调用 file.close()，无需手动关闭
try:
    with open("1.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("with 写法读取内容:", content)
    # 离开 with 块后 file 已自动关闭
    print("文件是否已关闭:", file.closed)  # True
except FileNotFoundError:
    print("with 写法: 文件 1.txt 不存在")


# ── with 写法：写文件示例 ────────────────────────────
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("第一行内容\n")
    f.write("第二行内容\n")
print("output.txt 写入完成，文件已自动关闭")


# ── 同时打开多个文件 ─────────────────────────────────
# Python 3.1+ 支持在一个 with 语句中管理多个资源
try:
    with (
        open("output.txt", "r", encoding="utf-8") as src,
        open("output_copy.txt", "w", encoding="utf-8") as dst,
    ):
        for line in src:
            dst.write(line)
    print("文件复制完成")
except FileNotFoundError as e:
    print("文件不存在:", e)


# ── 自定义上下文管理器 ────────────────────────────────
# 实现 __enter__ 和 __exit__ 方法即可让类支持 with 语句
class ManagedResource:
    def __enter__(self):
        print("__enter__: 资源已获取")
        return self  # 赋值给 as 后面的变量

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exc_type/exc_val/exc_tb：异常信息，无异常时均为 None
        print("__exit__: 资源已释放")
        return False  # 返回 False 表示不吞掉异常，异常会继续向上抛出


with ManagedResource() as res:
    print("with 块内部，正在使用资源:", res)
# 离开 with 块后自动调用 __exit__
