# 可迭代对象与枚举

> 📖 本章覆盖 for 循环、推导式、生成器，是日常编码最常用的模式。建议在第 6-7 章之后阅读。

### 8.1 哪些数据是可迭代的

```python
# JS 里：Array, String, Map, Set, NodeList, arguments 等都可用 for...of
# Python 里，以下都可被 for...in 遍历：

可迭代类型 = [list, tuple, str, dict, set, range,
            "文件对象", "生成器", "dict.keys()", "dict.values()", "dict.items()"]
```

### 8.2 遍历方式对照

```python
items = [1, 2, 3]

# ─── 基础遍历 ───
# JS:  for (const x of items)
for x in items:
    print(x)

# JS:  arr.forEach((x, i) => {...})
for i, x in enumerate(items):
    print(i, x)                              # 0 1, 1 2, 2 3

# ─── 字典遍历 ───
d = {"a": 1, "b": 2}
for k in d:           # 同 Object.keys()
    pass
for v in d.values():  # 同 Object.values()
    pass
for k, v in d.items(): # 同 Object.entries()
    pass

# ─── 同时遍历两个列表 ───
# JS 没有内置等价物
for a, b in zip([1,2], ["a","b"]):
    print(a, b)        # (1, "a"), (2, "b")
```

### 8.3 列表推导式 — JS `.map()` / `.filter()` 的 Python 写法

这是前端转 Python **最需要内化的写法**：

```python
numbers = [1, 2, 3, 4, 5]

# JS:  numbers.map(x => x * 2)
[x * 2 for x in numbers]                     # [2, 4, 6, 8, 10]

# JS:  numbers.filter(x => x > 2)
[x for x in numbers if x > 2]                # [3, 4, 5]

# JS:  numbers.filter(x => x > 2).map(x => x * 2)
[x * 2 for x in numbers if x > 2]            # [6, 8, 10]

# 字典推导式
{x: x * 2 for x in range(3)}                 # {0: 0, 1: 2, 2: 4}

# 集合推导式
{x % 3 for x in range(9)}                    # {0, 1, 2}

# ✅ Python 3 的推导式有独立作用域，循环变量 x 不会泄漏
for i in range(3):        # 但普通 for 循环会泄漏变量 i 到外部
    pass
print(i)                  # 2 — i 仍然存在（和 JS 的 let 块级作用域不同）
```

### 8.4 生成器 — 惰性序列（类似 JS 的生成器）

```python
# JS:  function* gen() { yield 1; yield 2; }
def gen():
    yield 1
    yield 2
    yield 3

for value in gen():
    print(value)

# 生成器推导式 — 用小括号
squares = (x * x for x in range(1_000_000))  # 不占内存，用到时才计算

# range — 也是惰性的
r = range(1_000_000)        # 不创建 100 万个元素的列表
list(r)                     # 需要时才物化
```

### 8.5 枚举与 In 运算符

```python
# in 运算符 — 检查成员，适用于所有可迭代对象
"a" in "abc"             # True  — 子串检查
3 in [1, 2, 3]           # True  — 列表成员
"key" in {"key": 1}      # True  — 字典的 key
3 in (1, 2, 3)           # True  — 元组成员

# 排序和分组
sorted([3, 1, 2])                  # [1, 2, 3]  — 返回新列表
sorted([3, 1, 2], reverse=True)    # [3, 2, 1]

users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 20}]
sorted(users, key=lambda u: u["age"])  # 按 age 排序（类似 JS 的 .sort((a,b) => a.age - b.age)）

# 实用内置函数
any([False, True, False])          # True  — 同 JS some
all([True, True, True])            # True  — 同 JS every
sum([1, 2, 3])                     # 6
min([3, 1, 2])                     # 1
max([3, 1, 2])                     # 3
len([1, 2, 3])                     # 3  — 同 JS .length
```

