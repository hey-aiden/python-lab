# Python 基础语法示例
# 本文件演示 Python 的核心语法特性，适合初学者参考

import sys  # 标准库导入应放在文件顶部

# print函数的end参数用于指定打印结束后的字符，默认是换行符\n，可以通过end参数指定为其他字符或空字符串
print("0", end=" ")
print("1", end="")
print("3", end="ab")
print("2")
# 输出： 0 13ab2


# ── 注释 ──────────────────────────────────────────────
# 单行注释用 # 开头

"""
多行注释（文档字符串）可以用三引号包裹。
三单引号 ''' 和三双引号 \"\"\" 效果相同。
"""


# ── 缩进规则 ──────────────────────────────────────────
"""
Python 用缩进表示代码块，不使用大括号 {}。
同一代码块内的缩进必须一致，否则会报 IndentationError。
"""

# 正确示例：
if True:
    print("True")
else:
    print("False")  # 两个分支缩进一致


# ── 多行语句 ──────────────────────────────────────────
# 用反斜杠 \ 将一条语句拆成多行书写
item_one = 1
item_two = 2
item_three = 3
total = item_one + item_two + item_three
print("总和:", total)  # 输出: 总和: 6


# ── 数字类型 ──────────────────────────────────────────
"""
Python 3 中数字有四种类型：
  int     整数（无长度限制）
  float   浮点数
  bool    布尔值，True / False（本质是 int 的子类）
  complex 复数，形如 a + bj，例如 1+2j
"""
num_int = 10  # 整数
num_float = 3.14  # 浮点数
num_bool = True  # 布尔值
num_complex = 1 + 2j  # 复数
print(num_int, num_float, num_bool, num_complex)


# ── 字符串类型 ────────────────────────────────────────
"""
字符串要点：
1. 单引号 ' 和双引号 " 完全等价
2. 三引号支持多行字符串
3. 索引：从左 0 开始，从右 -1 开始
4. 字符串不可变，修改需借助切片或方法
5. 切片语法：str[start:end:step]，end 不包含
6. 没有单独的字符类型，单个字符就是长度为 1 的字符串
7. 前缀 r 表示原始字符串，反斜杠不转义
"""
text = "123456789"

print(text)  # 输出完整字符串: 123456789
print(text[0:-1])  # 第一个到倒数第二个: 12345678
print(text[0])  # 第一个字符: 1
print(text[2:5])  # 索引 2~4（不含5）: 345
print(text[2:])  # 从索引 2 到末尾: 3456789
print(text[1:5:2])  # 索引 1~4，步长 2: 24
print(text * 2)  # 重复两次: 123456789123456789
print(text + " 你好")  # 字符串拼接: 123456789 你好

print("-" * 30)

# 转义字符 vs 原始字符串
print("hello\nrunoob")  # \n 被解释为换行
print(r"hello\nrunoob")  # r 前缀：\n 原样输出，不换行


# ── 空行 ──────────────────────────────────────────────
# 函数/类之间用空行分隔，表示一段新代码的开始。
# 空行不是语法要求，但能提升可读性。


# ── 同一行多条语句 ────────────────────────────────────
# 用分号 ; 分隔，但不推荐，会降低可读性
# x = "runoob"; sys.stdout.write(x + "\n")  # 原写法（不推荐）
x = "runoob"
sys.stdout.write(x + "\n")  # 推荐：每条语句单独一行


# ── 等待用户输入 ──────────────────────────────────────
def main() -> None:
    """程序入口：演示 input() 的用法。"""
    print("Hello, World!")
    input("\n按下 Enter 键退出。")


if __name__ == "__main__":
    # 只有直接运行此文件时才执行 main()
    # 作为模块被导入时不会执行
    main()


# ── 多个语句构成代码块（组） ──────────────────────────
# 代码块由缩进相同的多条语句组成，常见于 if/for/while/def/class 中

# 示例1：if-elif-else 代码块
score = 85
if score >= 90:
    grade = "A"
    print("优秀")
elif score >= 60:
    grade = "B"
    print("及格")
else:
    grade = "C"
    print("不及格")

# 示例2：for 循环代码块
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print("水果:", fruit)  # 循环体内可以有多条语句
    print("---")


# 示例3：函数定义代码块
def add(a, b):
    result = a + b  # 多条语句共同构成函数体
    return result


print("1 + 2 =", add(1, 2))


