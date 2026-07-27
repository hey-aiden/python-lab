# 迭代器与生成器

"""
迭代器是一个可以记住遍历位置的对象：
  - 只能向前，不能后退
  - 两个核心方法：iter() 创建迭代器，next() 取下一个元素
  - 字符串、列表、元组等可迭代对象都可用 iter() 转为迭代器
"""

# ── 基本用法 ──────────────────────────────────────────
lst = [1, 2, 3]
it = iter(lst)

print("next(it):", next(it))  # 1
print("next(it):", next(it))  # 2
print("next(it):", next(it))  # 3

# 迭代器已耗尽，再调用 next() 会抛出 StopIteration
try:
    print("next(it):", next(it))
except StopIteration:
    print("StopIteration: 迭代器已耗尽，没有更多元素")


# ── for 循环会自动捕获 StopIteration ─────────────────
# for 循环底层就是不断调用 next()，遇到 StopIteration 时自动停止
it2 = iter([10, 20, 30])
for item in it2:
    print("for item:", item)

# for 循环结束后迭代器同样耗尽
try:
    next(it2)
except StopIteration:
    print("StopIteration: for 循环结束后迭代器也已耗尽")


# ── 用 next() 的默认值避免报错 ────────────────────────
# next(iterator, default) — 耗尽时返回默认值而不抛出异常
it3 = iter([1, 2])
print("next with default:", next(it3, "无更多元素"))  # 1
print("next with default:", next(it3, "无更多元素"))  # 2
print("next with default:", next(it3, "无更多元素"))  # 无更多元素（不报错）


# ── 自定义迭代器 ──────────────────────────────────────
# 实现 __iter__ 和 __next__ 方法即可让类成为迭代器
class CountUp:
    """从 start 计数到 end 的迭代器"""

    def __init__(self, start, end):
        self.current = start
        self.end = end

    def __iter__(self):
        return self  # 迭代器本身就是可迭代对象

    def __next__(self):
        if self.current > self.end:
            raise StopIteration  # 主动抛出表示迭代结束： raise 是 Python 里用来Python主动抛出异常（exception）的语句
        value = self.current
        self.current += 1
        return value


counter = CountUp(1, 4)
for n in counter:
    print("CountUp:", n)  # 1 2 3 4


# ── 生成器：更简洁的迭代器写法 ────────────────────────
# 用 yield 关键字定义，每次调用 next() 从上次 yield 处继续执行
def count_up(start, end):
    while start <= end:
        yield start  # 暂停并返回当前值
        start += 1


gen = count_up(1, 4)
print("生成器类型:", type(gen))  # <class 'generator'>
print("next(gen):", next(gen))  # 1
print("next(gen):", next(gen))  # 2
for n in gen:  # 继续消费剩余的值
    print("gen for:", n)  # 3 4


"""
在 Python 中，使用了 yield 的函数被称为生成器（generator）

yield 是一个关键字，用于定义生成器函数，生成器函数是一种特殊的函数，可以在迭代过程中逐步产生值，而不是一次性返回所有结果

生成器是一个返回迭代器的函数，只能用于迭代操作，更简单点理解生成器就是一个迭代器

当在生成器函数中使用 yield 语句时，函数的执行将会暂停，并将 yield 后面的表达式作为当前迭代的值返回
"""


def countdown(n):
    while n > 0:
        yield n
        n -= 1


generator = countdown(5)  # 创建生成器对象
print(next(generator))  # 5
print(next(generator))  # 4
print(next(generator))  # 3
print(next(generator))  # 2
print(next(generator))  # 1
# print(next(generator))  # StopIteration
