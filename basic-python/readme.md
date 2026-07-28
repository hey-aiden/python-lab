# Python 速通：写给 JavaScript 开发者

> 以你熟悉的 JS/TS 概念为锚点，对照学习 Python。

---

## 1. 数据类型对照

### 1.1 整体映射

| JavaScript | Python | 关键差异 |
|------------|--------|----------|
| `number` | `int` / `float` | JS 统一为 64-bit 浮点；Python 区分整数和浮点 |
| `bigint` | `int` | Python 的 `int` 天生支持任意精度，无需 BigInt |
| `string` | `str` | 都是不可变 Unicode 字符串 |
| `boolean` | `bool` | Python 写作 `True` / `False`（首字母大写），且是 `int` 的子类 |
| `undefined` | ❌ 不存在 | Python 用 `None`，但 `None` 更接近 JS 的 `null` |
| `null` | `None` | 唯一的空值，只有一个实例 |
| `Symbol` | ❌ 不存在 | Python 通常用字符串常量替代 |
| `Array` | `list` | 可变、有序；Python 没有 `.map()`/`.filter()` 方法，用推导式代替 |
| `Object` | `dict` | 键必须是可哈希类型（字符串、数字、元组等），不支持 `.` 点号访问 |
| `Map` | `dict` | Python 的 `dict` 本质就是哈希表，直接用即可 |
| `Set` | `set` | 都表示无序不重复集合 |

### 1.2 各类型详解

#### 数值 — `number` → `int` / `float`

```python
# JS: let n = 42;  let f = 3.14;
n = 42           # int — 不限精度，随便多大
f = 3.14         # float — 64-bit 双精度，和 JS number 相同

1_000_000        # 可以用 _ 分隔数字，纯视觉辅助

# 浮点精度问题 — 和 JS 一模一样
0.1 + 0.2        # 0.30000000000000004
```

#### 布尔 — `boolean` → `bool`

```python
True              # 首字母大写！！
False

# bool 是 int 子类（JS 里可没这种关系）
True + 1          # 2（True 即 1）
True is 1         # False，类型不同但值等价

# 假值判断（和 JS 差别很大，这是最大坑之一）
# Python 中以下为 False：
bool(False)       # False
bool(None)        # False
bool(0)           # False
bool(0.0)         # False
bool("")          # False  — 空字符串
bool([])          # False  — 空列表
bool({})          # False  — 空字典
bool(())          # False  — 空元组
# 其他全是 True（跟 JS 的 truthy/falsy 规则不同）
```

#### 字符串 — `string` → `str`

```python
# 单引号和双引号无区别，和 JS 一样
"hello" == 'hello'   # True

# 模板字符串 = f-string（JS 的 `` 反引号）
name = "world"
f"hello {name}"           # "hello world"
f"1 + 1 = {1 + 1}"        # "1 + 1 = 2"

# 常用操作
"a,b,c".split(",")         # ["a", "b", "c"]  — 同 JS
",".join(["a", "b"])       # "a,b"  — 注意是 str 的方法，不是 Array 的
" hello ".strip()          # "hello"  — 同 trim()
"hello".upper()            # "HELLO"  — 注意是 upper 不是 toUpperCase
```

#### 列表 — `Array` → `list`

```python
# 创建和访问
items = [1, 2, 3]
items[0]            # 1
items[-1]           # 3  — 负数索引从尾部取，JS 没有
items[1:3]          # [2, 3]  — 切片（slice），比 JS 更强大

# 增删改
items.append(4)     # [1,2,3,4]  — 同 push
items.pop()         # 4，弹出最后一个 — 同 pop
items.insert(0, 0)  # [0,1,2,3]  — 指定位置插入

# ⚠️ JS 开发者最容易犯错：list 的 + 是拼接，不是合并
[1, 2] + [3, 4]     # [1, 2, 3, 4]  — 同 JS 的 .concat()

# ⚠️ 第二个坑：Python 没有 .map() / .filter() 方法！
# JS:  arr.map(x => x * 2)
# Python：用推导式（下一节详讲）
[x * 2 for x in items]                   # [2, 4, 6]
[x for x in items if x > 1]              # [2, 3]
```

#### 元组 — `Tuple`（JS 无对应物）

```python
coords = (10, 20)    # 不可变的列表
coords[0]            # 10
coords[0] = 5        # ❌ TypeError: tuple 不支持修改

# 解包赋值 — 同 JS 解构
x, y = (10, 20)      # x=10, y=20
x, y = y, x          # 一行交换，无需临时变量

# 单元素元组的坑 — 逗号是灵魂，括号只是外壳
t = (1)              # ❌ 这是 int 1，不是 tuple
t = (1,)             # ✅ 这才是元组
```

#### 字典 — `Object` → `dict`

```python
user = {"name": "Alice", "age": 30}

# 访问
user["name"]          # "Alice"
user.get("email", "") # ""  — 安全访问，不存在则返回默认值（推荐）

# ⚠️ 不能点号访问！
user.name             # ❌ AttributeError（除非是类实例属性）

# 增删
user["email"] = "a@b.com"
del user["email"]          # 删除键
user.pop("email", None)    # 安全删除

# 遍历
for key in user:               # 同 Object.keys()
    pass
for key, value in user.items(): # 同 Object.entries()
    pass

# ⚠️ 键类型限制：只能是可哈希类型
#   合法：str, int, float, tuple
#   非法：list, dict, set（这些东西不能做 key）
```

#### 集合 — `Set` → `set`

```python
tags = {"python", "js"}
tags.add("rust")
"rust" in tags       # True  — O(1) 成员判断

# 集合运算
a = {1, 2, 3}
b = {2, 3, 4}
a & b                # {2, 3}    — 交集
a | b                # {1,2,3,4} — 并集
a - b                # {1}       — 差集
```

#### 空值与字节 — `null`/`Buffer` → `None`/`bytes`

```python
# None — 唯一的空值（同时扮演 JS 的 null 和 undefined）
result = None
if result is None:        # 用 is，不要用 ==（约定俗成）
    pass

# 可选链 ?. 的替代写法
value = obj.get("key")                    # dict 的 get
from functools import reduce
value = getattr(obj, 'key', 'default')    # 对象属性

# bytes — 二进制数据，类似 JS 的 Uint8Array 或 Buffer
data = b"hello"
data = "你好".encode("utf-8")    # str → bytes
text = data.decode("utf-8")      # bytes → str
```

---

## 2. 变量、赋值与可变性

### 2.1 变量定义 — 无声明关键字

```python
# JS:  let name = "Alice";   const MAX = 100;
# Python：直接赋值，没有 let/const/var
name = "Alice"
MAX = 100          # 全大写只是约定，没有真正的常量
```

Python **没有常量关键字**。全大写命名（`MAX_SIZE`）是社区约定，告诉别人"别改它"，但语言层面不阻止。

### 2.2 可变性 — 核心概念

```python
# JS 里：const arr = [1,2]; arr.push(3); // 合法，const 只锁引用不锁内容
# Python 同理，但分类更清晰：

# 不可变类型（immutable）：
#   int, float, str, bool, tuple, frozenset, bytes, None
#   创建后内容不可修改，任何"修改"操作都产生新对象

s = "hello"
s = s + " world"    # 看起来像修改，实际创建了新字符串，原 "hello" 未变
id(s)                # 查看对象在内存中的唯一标识（类似 JS 的 === 指针比较）

# 可变类型（mutable）：
#   list, dict, set, bytearray
#   内容可原地修改

a = [1, 2, 3]
b = a               # b 和 a 指向同一列表
b.append(4)
print(a)            # [1, 2, 3, 4]  — a 也变了！

# 想复制一份独立列表？
b = a.copy()        # 浅拷贝
b = a[:]            # 同上，切片拷贝
import copy
b = copy.deepcopy(a) # 深拷贝
```

### 2.3 值与引用（赋值即绑定）

```python
# Python 的赋值 = 给对象贴名字标签，不复制数据

# 不可变类型的行为 — 看起来像"值传递"
x = 1
y = x               # y 和 x 指向同一个 int 对象 1
y = 2               # y 现在指向新的 int 对象 2，x 还是 1

# 可变类型的行为 — 看起来像"引用传递"
a = [1, 2]
b = a               # a 和 b 都指向同一个列表
b[0] = 99
print(a[0])         # 99，两个名字指向同一个东西
```

### 2.4 `==` vs `is`

```python
# ==  比较值是否相等（同 JS 的 ===，但 Python 的 == 会做类型转换？不会）
# is  比较是否同一个对象（同 JS Object.is 或指针比较）

a = [1, 2]
b = [1, 2]
c = a

a == b              # True  — 值相等
a is b              # False — 不同对象
a is c              # True  — 同一个对象

# 对 None 永远用 is
if x is None:       # ✅ 正确
if x == None:       # 可以但不符合惯例
```

---

## 3. 可迭代对象与枚举

### 3.1 哪些数据是可迭代的

```python
# JS 里：Array, String, Map, Set, NodeList, arguments 等都可用 for...of
# Python 里，以下都可被 for...in 遍历：

可迭代类型 = [list, tuple, str, dict, set, range,
            "文件对象", "生成器", "dict.keys()", "dict.values()", "dict.items()"]
```

### 3.2 遍历方式对照

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

### 3.3 列表推导式 — JS `.map()` / `.filter()` 的 Python 写法

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

# ⚠️ 推导式不会创建新的作用域
# 循环变量 x 会"泄漏"到外部（Python 3 列表中也是）
```

### 3.4 生成器 — 惰性序列（类似 JS 的生成器）

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

### 3.5 枚举与 In 运算符

```python
# in 运算符 — 检查成员，适用于所有可迭代对象
"a" in "abc"             # True  — 子串检查
3 in [1, 2, 3]           # True  — 列表成员
"key" in {"key": 1}      # True  — 字典的 key
3 in (1, 2, 3)           # True  — 元组成员

# 排序和分组
sorted([3, 1, 2])                  # [1, 2, 3]  — 返回新列表
sorted([3, 1, 2], reverse=True)    # [3, 2, 1]
sorted(users, key=lambda u: u.age) # 按 age 排序

# 实用内置函数
any([False, True, False])          # True  — 同 JS some
all([True, True, True])            # True  — 同 JS every
sum([1, 2, 3])                     # 6
min([3, 1, 2])                     # 1
max([3, 1, 2])                     # 3
len([1, 2, 3])                     # 3  — 同 JS .length
```

---

## 4. 错误捕获

### 4.1 语法对照

```python
# JS:
#   try { ... } catch (error) { ... } finally { ... }
#   throw new Error("msg")

# Python:
try:
    result = 1 / 0
except ZeroDivisionError as e:
    # 捕获特定异常
    print(f"出错了: {e}")
except (TypeError, ValueError) as e:
    # 同时捕获多种
    pass
except Exception as e:
    # 捕获所有（类似 JS 的 catch(error)）
    pass
else:
    # try 块无异常时执行（JS 没有这个）
    print("一切正常")
finally:
    # 无论如何都执行
    print("清理")
```

### 4.2 关键差异

```python
# Python 鼓励捕获具体异常类型，而不是一把抓
try:
    data = json.loads(raw)
except json.JSONDecodeError:      # ✅ 精确捕获
    data = {}

# raise — 类似 throw
raise ValueError("无效参数")
raise   # 单独使用 = 重新抛出当前异常（在 except 块内）

# 自定义异常
class MyError(Exception):
    pass

# 常见内置异常
# TypeError      — 类型不对（传了 str 给期望 int 的参数）
# ValueError     — 类型对但值不对（int("abc")）
# KeyError       — 字典 key 不存在（类似访问对象不存在的属性）
# IndexError     — 列表索引越界
# AttributeError — 对象没有该属性
# ImportError    — 模块导入失败
# FileNotFoundError — 文件不存在
```

### 4.3 资源管理 — `with` 替代 try-finally

```python
# JS 没有直接对应的，类似 C# using 或 Java try-with-resources

# 文件读写 — 自动关闭，无需 finally
with open("file.txt", "r") as f:
    content = f.read()
# 这里文件已自动关闭，不需要 f.close()

# 等价于：
f = open("file.txt", "r")
try:
    content = f.read()
finally:
    f.close()   # 手动保证关闭
```

---

## 5. 项目初始化与部署

### 5.1 工具对照

| 任务 | JavaScript (Node) | Python |
|------|-------------------|--------|
| 运行时代理 | Node.js | CPython (python3) |
| 包管理器 | npm / pnpm / yarn | uv / pip |
| 项目配置 | `package.json` | `pyproject.toml` |
| 锁文件 | `package-lock.json` | `uv.lock` |
| 依赖目录 | `node_modules/` | `.venv/lib/.../site-packages/` |
| 版本声明 | `.nvmrc` | `.python-version` |
| 运行脚本 | `npx` / `npm run` | `uv run` |
| 全局安装 | `npm install -g` | `pip install`（不推荐全局装） |
| 发布平台 | npm registry | PyPI (pypi.org) |

### 5.2 初始化项目

```bash
# JS:  npm init; npm install express
# Python:

# 1. 创建项目
uv init my-project
cd my-project

# 2. 添加依赖
uv add httpx           # 运行时依赖
uv add --dev pytest    # 开发依赖

# 3. 同步安装所有依赖
uv sync
```

生成的项目结构：

```
my-project/
├── pyproject.toml      # 类似 package.json
├── uv.lock             # 类似 package-lock.json
├── .python-version     # 类似 .nvmrc
├── .venv/              # 类似 node_modules/，但全局共享一个解释器
├── README.md
└── hello.py
```

#### 在已有目录中初始化

`uv init` 支持对已有内容的目录进行初始化：

```bash
# 方式 1：cd 进去执行
cd existing-folder
uv init

# 方式 2：指定路径
uv init existing-folder

# 指定项目名
uv init --name "my-project" .
```

**已存在文件的行为：**

| 文件 | 已存在时 | 不存在时 |
|------|----------|----------|
| `pyproject.toml` | ❌ 报错退出，不覆盖 | 自动创建 |
| `README.md` | 保留不动 | 自动生成模板 |
| `hello.py` | 跳过不建 | 自动创建示例 |

```bash
# 如果已有 pyproject.toml 但仍想重新初始化
uv init --force          # 强制执行（谨慎，会覆盖 pyproject.toml）
```

**最佳安全实践** — 只想补一个 `pyproject.toml` 而不影响其他文件：

```bash
# 在临时目录生成，复制过来
uv init /tmp/temp-project
cp /tmp/temp-project/pyproject.toml ./
# 然后手动编辑 pyproject.toml 改成实际项目信息
```

**适用场景：** 已有代码目录想接入 `uv` 生态时，直接 `uv init` 即可，已有的 `.py` 文件不会受任何影响。

### 5.3 入口文件与 `if __name__ == "__main__"`

```python
# hello.py

def main():
    print("Hello, World!")

# JS 没有这个模式，Python 需要显式判断
# 当 python hello.py 直接运行：True，执行 main()
# 当 import hello 导入：       False，不执行
if __name__ == "__main__":
    main()
```

### 5.4 部署方式

#### 脚本/工具 → 直接运行

```bash
# 目标机器安装 uv，然后：
uv sync
uv run main.py
```

#### Web 服务 → Docker

```dockerfile
# 简化示例
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
COPY src/ ./src/
CMD ["uv", "run", "gunicorn", "src.app:app"]
```

#### 发布到 PyPI

```bash
uv build                    # 构建 wheel 包
uv publish                  # 发布到 PyPI（类似 npm publish）
```

```toml
# pyproject.toml 中需要额外配置
[project.scripts]
my-cli = "my_package.cli:main"   # 注册 CLI 入口（类似 npm bin）
```

---

## 6. 更多差异速查

### 6.1 函数

```python
# JS:  function add(a, b=0) { return a + b; }
#      const add = (a, b=0) => a + b;
def add(a, b=0):
    return a + b

# ⚠️ 默认参数陷阱 — 可变默认值只创建一次！
def append_to(item, target=[]):     # ❌ 每次调用共享同一个默认列表
    target.append(item)
    return target

def append_to(item, target=None):   # ✅ 正确做法
    if target is None:
        target = []
    target.append(item)
    return target

# 不定参数
def log(*args):           # *args — 同 JS 的 ...args（位置参数）
    print(args)           # tuple

def config(**kwargs):     # **kwargs — 同 JS 的 {...obj} 展开（关键字参数）
    print(kwargs)         # dict

# 解包调用
params = [1, 2]
add(*params)              # 同 JS 的 add(...params)
```

### 6.2 类与 OOP

```python
class Animal:
    species = "Unknown"                 # 类属性（类似 JS static 字段）

    def __init__(self, name):           # 构造函数（类似 JS constructor）
        self.name = name                # self ≈ JS 的 this，但必须显式写出

    def speak(self):                    # 实例方法
        return f"{self.name} says hi"

class Dog(Animal):                      # 继承 — 同 extends
    def speak(self):
        return f"{self.name} says woof"

# 多继承 — JS 不支持（JS 只能单继承 + mixin）
class Bat(A, B):                        # 同时继承 A 和 B
    pass

# isinstance — 类似 instanceof
isinstance(dog, Animal)                 # True
```

### 6.3 模块系统

```python
# JS:  import React from 'react'
#      import { useState } from 'react'
#      export default App
#      export { helper }

# Python:
import os                              # 导入整个模块
from os import path                    # 导入特定名称
from os import path as p               # 导入并重命名
import numpy as np                     # 导入并取别名（常见约定）

# 导出：Python 没有 export 关键字
# 文件中所有顶层名称默认都是"公开的"
# _下划线开头表示"私有"（仅约定，类似 JS 社区 _internal）
__all__ = ["public_api", "another_fn"] # 控制 from module import * 的行为
```

### 6.4 异步编程 — `Promise` vs `async/await`

```python
# JS:
#   async function fetchData() {
#     const res = await fetch(url);
#     return res.json();
#   }

# Python：
import asyncio
import httpx

async def fetch_data():
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return res.json()

# 运行入口
asyncio.run(fetch_data())
```

### 6.5 没有的东西（以及替代方案）

| JS 特有的东西 | Python 的替代 |
|---------------|---------------|
| `console.log()` | `print()` |
| `typeof x` | `type(x)` |
| `x instanceof C` | `isinstance(x, C)` |
| `!!x` 双感叹转布尔 | `bool(x)` |
| `x ?? y` 空值合并 | `x if x is not None else y`（Python 3.10 尚无 `??`） |
| `x?.y?.z` 可选链 | `getattr(x, 'y', None)` 或 try/except |
| 三元 `a ? b : c` | `b if a else c`（注意顺序不同） |
| 模板字面量 `` `hello ${name}` `` | `f"hello {name}"` |
| `switch/case` | `match/case`（Python 3.10+，更强大） |
| `Array.map/filter/reduce` | 列表推导式 / `map()` / `filter()` 内置函数 |
| `{...obj1, ...obj2}` 展开 | `{**d1, **d2}` 字典合并运算符（Python 3.5+） |
| `[...arr, ...arr2]` 展开 | `[*l1, *l2]` 列表展开（Python 3.5+） |
| `for (let i = 0; i < n; i++)` | `for i in range(n):` |
| `window` / `document` | 不存在，Python 不走浏览器 |

### 6.6 包管理与工具链速览

| 类别 | 推荐工具 | 对标 JS |
|------|----------|---------|
| 包管理 + 运行 | `uv` | npm + npx |
| 代码格式化 | `ruff format` | Prettier |
| Lint / 排序导入 | `ruff check` | ESLint + import 排序 |
| 类型检查 | `mypy` | TypeScript |
| 测试 | `pytest` | Jest / Vitest |
| 构建/打包 | `uv build` | esbuild / rollup |
| 发布 | `uv publish` | npm publish |
| 环境变量 | `.env` + `python-dotenv` | dotenv |

### 6.7 编码风格速记

```python
# PEP 8 — Python 编码风格指南（类似 Airbnb JS Style Guide）
# 但工具会自动处理，知道这几个就行：

# 缩进：4 个空格（不是 2 个，绝对不能 Tab）
# 变量命名：snake_case，不是 camelCase
# 类命名：PascalCase（和 JS 一样）
# 常量命名：UPPER_SNAKE_CASE
# 私有：_leading_underscore（约定，不是语言强制的）

# 类型注解 — 类似 TypeScript，但是可选的，运行时不管
def greet(name: str) -> str:
    return f"Hello, {name}"
```
