# 读取键盘输入
# Python 3 中 raw_input() 已移除,统一使用 input()
# input() 始终返回字符串类型,需要数字时要手动转换

import shutil
import os
from pathlib import Path
import random


# 读取字符串
def read_string():
    user_str = input("请输入一段文字：")
    print("你输入的内容是:", user_str)
    print("输入内容的类型:", type(user_str))  # <class 'str'>

    # 读取数字：input() 返回的是字符串,需用 int() 或 float() 转换
    # user_num = int(input("请输入一个整数："))
    # print("输入的整数加 10:", user_num + 10)

    # 安全读取：用 try/except 防止用户输入非数字时报错
    try:
        user_float = float(input("请输入一个小数："))
        print("输入的小数乘 2:", user_float * 2)
    except ValueError:
        print("输入的不是有效数字")
    return user_float


# read_string()


"""
文件操作：

打开和关闭文件:
先用Python内置的open()函数打开一个文件,创建一个file对象,相关的方法才可以调用它进行读写

语法：file object = open(file_name [, access_mode][, buffering])
access_mode：打开文件的模式,常见的比如：r（只读）,w（只写）,a（追加）,r+（读写）,w+（读写）,a+（读写）
w+: 打开一个文件用于读写。如果该文件已存在则打开文件，并从开头开始编辑，即原有内容会被删除。如果该文件不存在，创建新文件
r+: 打开一个文件用于读写。文件指针将会放在文件的开头
a+: 打开一个文件用于读写。如果该文件已存在，文件指针将会放在文件的结尾。文件打开时会是追加模式。如果该文件不存在，创建新文件用于读写。
b: 以二进制模式打开文件。
t: 以文本模式打开文件(默认)
x: 写模式，新建一个文件，如果该文件已存在则会报错。

如果buffering的值被设为0，就不会有寄存。如果buffering的值取1，访问文件时会寄存行。如果将buffering的值设为大于1的整数，表明了这就是的寄存区的缓冲大小。如果取负值，寄存区的缓冲大小则为系统默认

一个文件被打开后，会有一个file对象，包括属性：
file.closed: 返回true如果文件已被关闭，否则返回false。
file.mode: 返回被打开文件的访问模式。
file.name: 返回文件的名称。
file.softspace: 如果用print输出后，必须跟一个空格符，则返回false。否则返回true

file.close(): 关闭文件。关闭后文件不能再进行读写操作。

file.write(string): 可将任何字符串写入一个打开的文件
将string写入到文件中，并返回写入的字符数。
需要重点注意的是，Python字符串可以是二进制数据，而不是仅仅是文字; 
write()方法不会在字符串的结尾添加换行符('\n')：

file.seek(offset, from_what): 
将文件指针从from_what（0，1，2 代表从文件开头，当前位置，文件末尾）偏移offset字节。
from_what值为0表示从文件开头偏移，1表示从当前位置偏移，2表示从文件末尾偏移。
offset可以为正或负数，表示移动的字节数。
返回当前位置。

file.tell(): 返回文件当前位置。

file.read([size]): 从文件读取指定的字节数，如果未给定或为负则读取所有。


重命名和删除文件：

os.rename(current_file_name, new_file_name);
os.remove(file_name);

"""


def open_file():
    with (
        open("1.txt", "a+") as file1,  # a+ 开启读写的追加模式；
        open("2.txt", "r") as file2,
    ):
        len = file1.write("\n追加一些内容\n")
        print(len)
        content1 = file1.read()
        content2 = file2.read()
        print(content1)
        print(content2)
        print("写入的字符数:", len, "文件指针位置:", file1.tell())
        return content1, content2


print(open_file())

# Path(__file__) 获取脚本文件: 这里返回的是：/Users/aiden/Documents/code/ai-skills/python/io.py
script_dir = Path(__file__).parent
print("看看脚本路径：", script_dir, Path(__file__))
src_file = script_dir / "1.txt"
dst_file = script_dir / "1.txt.bak"

os.rename(src_file, dst_file)


"""
文件夹操作

============================================================
核心概念：Path 对象 vs 字符串路径
============================================================

Q: 为什么可以直接用 target_dir.mkdir()，而不是 os.mkdir(target_dir)？
A: 因为 target_dir 是 pathlib.Path 对象，不是字符串！

Path 对象自带很多方法，比如：
  - mkdir()      创建目录
  - exists()     检查是否存在
  - is_file()    是否是文件
  - is_dir()     是否是目录
  - rename()     重命名
  - unlink()     删除文件
  - rmdir()      删除空目录
  - read_text()  读取文本内容
  - write_text() 写入文本内容
  - glob()       模式匹配查找文件

这是 Python 面向对象的设计：把路径和相关操作封装成一个对象。

============================================================
两种方式的对比
============================================================

# 方式 A：os 模块（传统方式，Python 2 时代）
# 传入字符串路径，调用函数操作
import os
os.mkdir("/path/to/dir")                    # 创建目录
os.path.exists("/path/to/dir")              # 检查是否存在
os.path.join("/path/to", "dir", "file.txt") # 拼接路径

# 方式 B：pathlib 模块（现代方式，Python 3.4+）
# 路径是一个对象，方法挂在这个对象上
from pathlib import Path
p = Path("/path/to/dir")
p.mkdir()           # 创建目录
p.exists()          # 检查是否存在
p / "dir" / "file.txt"  # 拼接路径（更直观！）

pathlib 的优势：
1. 面向对象，代码更清晰
2. 路径拼接用 / 运算符，直观优雅
3. 自带很多实用方法，不用记 os.path.xxx
4. 跨平台，自动处理 Windows/Unix 路径差异
5. Python 3.6+ 推荐使用 pathlib

============================================================
"""

# ============================================================
# 创建目录：Path.mkdir() vs os.mkdir()
# ============================================================

# --- 方式 1：os.mkdir()（传统方式）---
# 缺点：
#   1. 只能创建单层目录，父目录不存在会报错
#   2. 目录已存在会报 FileExistsError
#   3. 需要手动检查或处理异常
# 示例：
#   os.mkdir("test")  # 如果 test 已存在，或父目录不存在，会报错
#   # 需要这样写才安全：
#   if not os.path.exists("test"):
#       os.mkdir("test")

# --- 方式 2：os.makedirs()（传统方式，创建多层目录）---
# 示例：
#   os.makedirs("a/b/c/d", exist_ok=True)  # Python 3.2+ 支持 exist_ok
#   # 类似 mkdir -p，会创建所有缺失的父目录

# --- 方式 3：Path.mkdir()（现代方式，推荐）---
# 优点：
#   1. parents=True 自动创建所有父目录（类似 mkdir -p），针对新建目录：a/b/c; 如果不存在a/b,会自动创建，避免报错；
#   2. exist_ok=True 目录已存在不报错
#   3. 面向对象，代码更清晰
target_dir = script_dir / "test"
target_dir.mkdir(parents=True, exist_ok=True)
print("创建目录:", target_dir)
print("target_dir 的类型:", type(target_dir))  # <class 'pathlib.PosixPath'>

# Path 对象可以和字符串比较，但类型不同！
print("转成字符串:", str(target_dir))  # 转成字符串
print("类型对比:", type(target_dir), "vs", type(str(target_dir)))

# --- 方式 4：创建随机目录名（如果需要）---
random_dir = script_dir / f"test_{random.randint(1, 1000000)}"
random_dir.mkdir(parents=True, exist_ok=True)
print("创建随机目录:", random_dir)

# --- 方式 5：创建临时目录（最佳实践）---
# 系统会自动清理，不用担心残留
# import tempfile
# with tempfile.TemporaryDirectory() as tmpdir:
#     print("临时目录:", tmpdir)
#     # 在这里操作文件...
# # 退出 with 块后自动删除

# ============================================================
# Path 对象常用方法演示
# ============================================================

# 检查路径状态
print("目录是否存在:", target_dir.exists())  # True
print("是否是目录:", target_dir.is_dir())  # True
print("是否是文件:", target_dir.is_file())  # False

# 路径操作
print("父目录:", target_dir.parent)  # 上一级目录
print("目录名:", target_dir.name)  # 目录名称
print("绝对路径:", target_dir.resolve())  # 解析成绝对路径

# 路径拼接（Path 对象的 / 运算符）
nested_dir = target_dir / "sub" / "deep" / "dir"
print("嵌套路径:", nested_dir)
nested_dir.mkdir(parents=True, exist_ok=True)  # 一键创建所有层级

# 删除空目录
# target_dir.rmdir()  # 只能删除空目录，非空会报错

# 删除目录树（需要 shutil，类似 rm -rf）
# import shutil
# shutil.rmtree(target_dir)  # 删除整个目录，包括内容

# ============================================================
# 删除文件和目录：os 模块 vs pathlib 模块
# ============================================================

"""
删除操作对比表
================================================================
操作类型           | os 模块（传统）        | pathlib 模块（现代）
================================================================
删除文件           | os.remove(path)       | path.unlink()
删除空目录         | os.rmdir(path)        | path.rmdir()
删除非空目录       | shutil.rmtree(path)   | shutil.rmtree(path) *
删除目录（含内容）  | shutil.rmtree(path)   | shutil.rmtree(path)
================================================================
* 注：pathlib 没有直接删除非空目录的方法，仍需配合 shutil
"""

# ------------------------------------------------------------
# 一、删除文件
# ------------------------------------------------------------

# 创建一个测试文件
test_file = script_dir / "test_file.txt"
test_file.write_text("这是一个测试文件")

# --- os 模块方式 ---
# os.remove(str(test_file))      # 删除文件 需要先通过str，把Path对象转换为路径字符串
# os.unlink(str(test_file))      # 同上，remove 的别名

# --- pathlib 方式（推荐）---
test_file.unlink()  # 删除文件，更直观
print("文件已删除:", test_file)

# 安全删除：先检查是否存在
if test_file.exists():
    test_file.unlink()
    print("文件已删除")
else:
    print("文件不存在，跳过删除")

# 删除不存在的文件会报错 FileNotFoundError
# 可以用 missing_ok=True 避免报错（Python 3.8+）
test_file.unlink(missing_ok=True)  # 文件不存在也不报错

# ------------------------------------------------------------
# 二、删除空目录
# ------------------------------------------------------------

# 创建一个空目录
empty_dir = script_dir / "empty_dir"
empty_dir.mkdir(exist_ok=True)

# --- os 模块方式 ---
# os.rmdir(str(empty_dir))       # 只能删除空目录

# --- pathlib 方式（推荐）---
empty_dir.rmdir()  # 同样只能删除空目录
print("空目录已删除:", empty_dir)

# 如果目录非空，会报 OSError: [Errno 39] Directory not empty
# 需要先清空目录，或者用下面的 shutil.rmtree()

# ------------------------------------------------------------
# 三、删除非空目录（需要 shutil 模块）
# ------------------------------------------------------------


# 创建一个非空目录
non_empty_dir = script_dir / "non_empty_dir"
non_empty_dir.mkdir(exist_ok=True)
(non_empty_dir / "file1.txt").write_text("内容1")
(non_empty_dir / "file2.txt").write_text("内容2")
(non_empty_dir / "subdir").mkdir(exist_ok=True)

# --- os 模块 + shutil ---
# shutil.rmtree(str(non_empty_dir))

# --- pathlib + shutil（推荐）---
# shutil.rmtree() 接受 Path 对象（Python 3.6+）
shutil.rmtree(non_empty_dir)  # 删除整个目录树，包括所有内容
print("非空目录已删除:", non_empty_dir)

# 注意：shutil.rmtree() 是危险操作！
#   - 不会进回收站，直接删除
#   - 无法撤销
#   - 建议先确认或备份重要数据

# ------------------------------------------------------------
# 四、安全的删除模式
# ------------------------------------------------------------


# 模式 1：删除前确认
def safe_delete_dir(path: Path, confirm: bool = False):
    """安全删除目录"""
    if not path.exists():
        print(f"目录不存在: {path}")
        return

    if confirm:
        response = input(f"确认删除 {path}? (y/n): ")
        if response.lower() != "y":
            print("取消删除")
            return

    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    print(f"已删除: {path}")


# 模式 2：移到回收站（需要第三方库）
# pip install send2trash
# from send2trash import send2trash
# send2trash(non_empty_dir)  # 移到回收站，可恢复

# 模式 3：先备份再删除
# backup_dir = script_dir / "backup"
# shutil.copytree(non_empty_dir, backup_dir / non_empty_dir.name)
# shutil.rmtree(non_empty_dir)

# ------------------------------------------------------------
# 五、常用删除操作速查
# ------------------------------------------------------------

"""
场景                          | 推荐代码
------------------------------|--------------------------------
删除单个文件                   | path.unlink(missing_ok=True)
删除空目录                     | path.rmdir()
删除非空目录（危险）            | shutil.rmtree(path)
删除前检查是否存在              | if path.exists(): path.unlink()
删除不报错（文件不存在）        | path.unlink(missing_ok=True)
删除到回收站（安全）            | send2trash(path)
------------------------------|--------------------------------
"""
