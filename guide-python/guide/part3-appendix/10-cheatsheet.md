# 更多差异速查

> 📖 本章是快速查阅表，覆盖函数、类、模块、异步、编码风格等，适合在需要时翻阅，不必从头读到尾。

### 10.1 函数

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

### 10.2 类与 OOP

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
dog = Dog("Rex")                        # 先创建实例
isinstance(dog, Animal)                 # True
```

### 10.3 模块系统

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

### 10.4 异步编程 — `Promise` vs `async/await`

```python
# JS:
#   async function fetchData() {
#     const res = await fetch(url);
#     return res.json();
#   }

# Python：
import asyncio
import httpx

url = "https://api.example.com/data"

async def fetch_data():
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return res.json()

# 运行入口
asyncio.run(fetch_data())
```

### 10.5 没有的东西（以及替代方案）

| JS 特有的东西 | Python 的替代 |
|---------------|---------------|
| `console.log()` | `print()` |
| `typeof x` | `type(x)` |
| `x instanceof C` | `isinstance(x, C)` |
| `!!x` 双感叹转布尔 | `bool(x)` |
| `x ?? y` 空值合并 | `x if x is not None else y`（严格判断 None）或 `x or y`（假值合并，更简洁） |
| `x?.y?.z` 可选链 | `getattr(x, 'y', None)` 或 try/except |
| 三元 `a ? b : c` | `b if a else c`（注意顺序不同） |
| 模板字面量 `` `hello ${name}` `` | `f"hello {name}"` |
| `switch/case` | `match/case`（Python 3.10+，更强大） |
| `Array.map/filter/reduce` | 列表推导式 / `map()` / `filter()` / `functools.reduce` |
| `{...obj1, ...obj2}` 展开 | `{**d1, **d2}`（Python 3.5+）或 `d1 \| d2`（Python 3.9+，更直观） |
| `[...arr, ...arr2]` 展开 | `[*l1, *l2]` 列表展开（Python 3.5+） |
| `for (let i = 0; i < n; i++)` | `for i in range(n):` |
| `window` / `document` | 不存在，Python 不走浏览器 |

### 10.6 包管理与工具链速览

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

### 10.7 编码风格速记

```python
# PEP 8 — Python 编码风格指南（类似 Airbnb JS Style Guide）
# 但工具会自动处理，知道这几个就行：

# 缩进：4 个空格（不是 2 个，推荐空格，不要混用 Tab 和空格）
# 变量命名：snake_case，不是 camelCase
# 类命名：PascalCase（和 JS 一样）
# 常量命名：UPPER_SNAKE_CASE
# 私有：_leading_underscore（约定，不是语言强制的）

# 类型注解 — 类似 TypeScript，但是可选的，运行时不管
def greet(name: str) -> str:
    return f"Hello, {name}"

# reduce — 对标 JS 的 Array.prototype.reduce()
from functools import reduce
# JS:  [1,2,3].reduce((acc, x) => acc + x, 0)
reduce(lambda acc, x: acc + x, [1, 2, 3], 0)   # 6
# 但更 Pythonic 的写法是直接用 sum()
sum([1, 2, 3])                                  # 6
```

