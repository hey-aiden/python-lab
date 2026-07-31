# Python 模块导入规则与标准库速览

> 📖 哪些 API 不需要 import？哪些需要？标准库有哪些常用模块？本文一次性讲清楚。

---

## 1. 哪些不需要 import？—— builtins

Python 启动时自动加载 `builtins` 模块，以下函数和类型**全局可用，不需要 import**：

| 类别 | 函数/类型 | 说明 |
|------|----------|------|
| 输出 | `print()` | 打印到 stdout |
| 文件 | `open()` | 打开文件（配合 `with` 使用） |
| 类型转换 | `int()` `float()` `str()` `bool()` `list()` `tuple()` `dict()` `set()` | 构造函数 |
| 类型判断 | `type(x)` `isinstance(x, T)` | 对标 `typeof`、`instanceof` |
| 序列操作 | `len()` `range()` `enumerate()` `zip()` `sorted()` `reversed()` | 日常高频 |
| 聚合 | `sum()` `min()` `max()` `any()` `all()` | 对标 JS 的 some/every |
| 迭代 | `iter()` `next()` `map()` `filter()` | 返回迭代器 |
| 数学 | `abs()` `round()` `pow()` `divmod()` | 简单运算 |
| 属性 | `getattr()` `setattr()` `hasattr()` `delattr()` | 对象属性反射 |
| 空值 | `None` `True` `False` | 字面量 |
| 异常 | `Exception` `ValueError` `TypeError` ... | 常见异常类 |
| 调试 | `dir()` `help()` | 探索对象 / 查看文档 |

```python
# 这些都不需要 import
print(len("hello"))            # 5
numbers = [3, 1, 2]
print(sorted(numbers))         # [1, 2, 3]
print(any([False, True]))      # True（对标 JS some）
print(isinstance(42, int))     # True
```

### 1.1 `dir()` — 查看对象有哪些属性和方法

`dir(obj)` 列出对象上所有可用的名字（属性、方法、变量），是探索陌生对象的第一工具。

```python
# 查看当前模块有哪些名字
print(dir())          # ['__builtins__', '__name__', ...]

# 查看某个对象有哪些方法
print(dir("hello"))
# ['capitalize', 'casefold', 'center', 'count', 'encode', 'endswith',
#  'find', 'format', 'index', 'isalnum', 'isalpha', 'islower', 'join',
#  'lower', 'lstrip', 'replace', 'rfind', 'split', 'startswith', 'strip',
#  'upper', 'zfill', ...]

# 只看公开方法名（去掉 __dunder__ 和 _private）
[name for name in dir("hello") if not name.startswith("_")]
# ['capitalize', 'casefold', 'center', 'count', ...]

# 查看标准库模块导出了什么
import json
print([name for name in dir(json) if not name.startswith("_")])
# ['JSONDecodeError', 'JSONDecoder', 'JSONEncoder', 'dump', 'dumps', 'load', 'loads', ...]
```

> 💡 `dir()` 是最高频的探索命令。遇到不认识的类型，先 `dir(obj)` 看有什么方法，再去查文档。

### 1.2 `help()` — 查看文档

`help(obj)` 打印对象的 docstring，比 `dir()` 更进一步：不仅告诉你**有哪些名字**，还告诉你**每个是干什么的、怎么用**。

```python
help(str)      # 查看 str 类的完整文档（很长，按 q 退出）

help(str.upper)       # 只看某个方法
# Help on method_descriptor:
#
# upper(self, /)
#     Return a copy of the string converted to uppercase.

import json
help(json.loads)
# Help on function loads in module json:
#
# loads(s, *, cls=None, object_hook=None, ...)
#     Deserialize s (a str, bytes or bytearray instance containing a JSON document) ...
```

| 工具 | 回答什么问题 | 类比 Node.js |
|------|-------------|-------------|
| `dir(obj)` | 这东西**有哪些**方法/属性？ | `Object.keys(obj)` + `Object.getOwnPropertyNames(proto)` |
| `help(obj)` | 这个方法是**怎么用**的？参数什么意思？ | `node -e "console.log(fs.readFile.toString())"` 然后自己看源码 |
| `type(obj)` | 这东西**是什么类型**？ | `typeof obj` |

> 💡 `dir()` + `help()` 组合拳：先用 `dir()` 快速浏览有哪些方法，再用 `help(obj.method)` 查看具体怎么用。学新库的时候尤其高效——不需要切到浏览器查文档。`help()` 在 `python -i`（交互模式）或 Jupyter 里用 `?` 更方便：
> ```python
> >>> str.upper?
> Signature: str.upper()
> Docstring: Return a copy of the string converted to uppercase.
> ```

---

## 2. 哪些需要 import？—— 标准库速览

以下全部需要 `import`。Python 标准库 = Node.js 的 `fs`/`path`/`os`/`http` 等，只不过 Python 把它拆得更细。

### 2.1 文件与路径

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `pathlib` | `Path()`, `/`, `.read_text()`, `.write_text()`, `.exists()`, `.glob()` | **首选路径处理**，对标 Node.js `path` + `fs` |
| `os` | `os.getcwd()`, `os.chdir()`, `os.listdir()`, `os.environ`, `os.remove()` | 操作系统交互 |
| `shutil` | `shutil.copy()`, `shutil.move()`, `shutil.rmtree()` | 文件/目录的复制移动删除 |
| `tempfile` | `tempfile.mkdtemp()`, `tempfile.NamedTemporaryFile()` | 临时文件/目录 |

```python
from pathlib import Path

# 查找所有 .py 文件
for f in Path("src").glob("**/*.py"):
    print(f.name)

# 批量重命名
for f in Path(".").glob("*.txt"):
    f.rename(f.with_suffix(".md"))
```

### 2.2 数据序列化

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `json` | `json.loads()`, `json.dumps()`, `json.load()`, `json.dump()` | JSON 解析/生成 |
| `csv` | `csv.reader()`, `csv.writer()`, `csv.DictReader()` | CSV 读写 |
| `pickle` | `pickle.dump()`, `pickle.load()` | Python 对象二进制序列化 |
| `tomllib` | `tomllib.load()` | TOML 解析（Python 3.11+） |

```python
import json

# 字符串 ↔ 对象
data = json.loads('{"name": "Alice", "age": 30}')
text = json.dumps(data, indent=2)

# 文件 ↔ 对象
with open("config.json") as f:
    config = json.load(f)
```

### 2.3 日期与时间

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `datetime` | `datetime.now()`, `datetime.strptime()`, `timedelta` | 日期时间运算 |
| `time` | `time.time()`, `time.sleep()`, `time.perf_counter()` | 时间戳、计时、睡眠 |

```python
from datetime import datetime, timedelta

now = datetime.now()                  # 当前时间
dt = datetime.strptime("2026-07-28", "%Y-%m-%d")  # 字符串 → 日期
tomorrow = now + timedelta(days=1)    # 时间运算
print(tomorrow.strftime("%Y-%m-%d"))  # 日期 → 字符串
```

### 2.4 正则与文本

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `re` | `re.search()`, `re.match()`, `re.findall()`, `re.sub()`, `re.compile()` | 正则匹配/替换 |
| `string` | `string.ascii_letters`, `string.digits` | 字符常量 |
| `textwrap` | `textwrap.fill()`, `textwrap.dedent()` | 文本格式化/缩进 |

```python
import re

text = "order: 123, price: $45"
nums = re.findall(r"\d+", text)           # ['123', '45']
result = re.sub(r"\$(\d+)", r"¥\1", text)  # 'order: 123, price: ¥45'
```

### 2.5 数学与随机

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `math` | `math.sqrt()`, `math.ceil()`, `math.pi` | 数学运算 |
| `random` | `random.random()`, `random.choice()`, `random.shuffle()` | 随机数/洗牌 |
| `statistics` | `statistics.mean()`, `statistics.median()` | 统计分析 |
| `decimal` | `Decimal("0.1")` | 精确小数（金融计算） |

```python
import random

items = [1, 2, 3, 4, 5]
random.shuffle(items)              # 原地洗牌
pick = random.choice(items)        # 随机选一个
print(pick)
```

### 2.6 系统与环境

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `sys` | `sys.argv`, `sys.path`, `sys.exit()`, `sys.version` | 命令行参数、解释器状态 |
| `os` | `os.environ`, `os.getenv()`, `os.path` | 环境变量、系统调用 |
| `subprocess` | `subprocess.run()`, `subprocess.check_output()` | 执行外部命令 |
| `argparse` | `argparse.ArgumentParser` | CLI 参数解析（推荐） |

```python
import sys
import subprocess

# 命令行参数
print(sys.argv)                     # ['app.py', 'arg1', 'arg2']

# 执行外部命令
result = subprocess.run(["git", "status"], capture_output=True, text=True)
print(result.stdout)
```

### 2.7 并发与异步

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `asyncio` | `asyncio.run()`, `async/await`, `asyncio.gather()` | 异步 I/O（首选） |
| `threading` | `threading.Thread()`, `threading.Lock()` | 多线程（I/O 密集型） |
| `multiprocessing` | `Process()`, `Pool()` | 多进程（CPU 密集型） |
| `concurrent.futures` | `ThreadPoolExecutor`, `ProcessPoolExecutor` | 线程/进程池（高层 API） |

```python
import asyncio

async def fetch(url):
    # 异步 HTTP 请求示例
    await asyncio.sleep(1)  # 模拟 I/O
    return f"done: {url}"

async def main():
    results = await asyncio.gather(fetch("a"), fetch("b"))
    print(results)

asyncio.run(main())
```

### 2.8 日志与调试

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `logging` | `logging.info()`, `logging.error()`, `logging.basicConfig()` | 结构化日志 |
| `traceback` | `traceback.print_exc()`, `traceback.format_exc()` | 异常堆栈 |
| `pprint` | `pprint.pprint()` | 美化打印嵌套结构 |

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("server started on port 8000")
```

### 2.9 网络

| 模块 | 典型 API | 使用场景 |
|------|---------|----------|
| `urllib.request` | `urllib.request.urlopen()` | 简单 HTTP 请求（内置） |
| `http.server` | `python -m http.server 8000` | 快速启动静态文件服务器 |

> 生产级 HTTP 推荐 `httpx`（异步）或 `requests`（同步），比内置 `urllib` 好用得多。

### 2.10 其他常用

| 模块 | 一句话用途 |
|------|-----------|
| `functools` | `reduce()`, `lru_cache()` 缓存函数结果 |
| `itertools` | `chain()`, `groupby()`, `product()` — 迭代器组合 |
| `collections` | `Counter`, `defaultdict`, `deque` — 增强版容器 |
| `hashlib` | `hashlib.sha256()` — 哈希摘要 |
| `uuid` | `uuid.uuid4()` — 生成 UUID |
| `dataclasses` | `@dataclass` 装饰器 — 自动生成 `__init__` |
| `enum` | `Enum` — 枚举类型 |

---

## 3. Node.js 对照速查表

| 场景 | Node.js | Python |
|------|---------|--------|
| 路径拼接 | `path.join("a", "b")` | `Path("a") / "b"` |
| 读文件 | `fs.readFileSync(p, "utf8")` | `Path(p).read_text()` |
| 写文件 | `fs.writeFileSync(p, s)` | `Path(p).write_text(s)` |
| JSON 解析 | `JSON.parse(s)` | `json.loads(s)` |
| 当前时间 | `new Date()` | `datetime.now()` |
| 时间戳 | `Date.now()` | `time.time()` |
| 休眠 | `await sleep(ms)` | `time.sleep(s)` |
| 正则全匹配 | `str.match(/re/g)` | `re.findall(r"re", str)` |
| 正则替换 | `str.replace(/re/g, x)` | `re.sub(r"re", x, str)` |
| 环境变量 | `process.env.KEY` | `os.environ["KEY"]` |
| 执行命令 | `execSync("cmd")` | `subprocess.run(["cmd"])` |
| 命令行参数 | `process.argv` | `sys.argv` |
| 随机数 0~1 | `Math.random()` | `random.random()` |
| UUID | `crypto.randomUUID()` | `uuid.uuid4()` |
| 日志 | `console.log` | `print()` / `logging.info()` |

---

## 4. 何时用标准库 vs 第三方包

| 场景 | 标准库够了 | 建议用第三方 |
|------|-----------|-------------|
| HTTP 客户端 | `urllib`（API 老旧） | `httpx` 或 `requests` |
| HTTP 服务器 | — | `fastapi` / `flask` |
| 测试 | `unittest` | `pytest`（所有人都用） |
| 模板引擎 | `string.Template` | `jinja2` |
| YAML | — | `pyyaml` |
| ORM | — | `sqlalchemy` |
| CLI 框架 | `argparse` | `click` / `typer` |

> 原则：标准库能解决就用标准库，API 不好用或功能不足再找第三方包。

---

> **总结**：`print`/`len`/`open`/`range`/`True` 等 ~70 个内置名全局可用，其余所有模块（包括 `os`/`sys`/`json`/`pathlib`）都必须 `import`。这和 Node.js 的规则完全一致。
