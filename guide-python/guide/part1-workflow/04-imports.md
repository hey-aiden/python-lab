# 跨目录/跨文件/跨项目引用

> 📖 本章涉及 pyproject.toml 和 uv pip install -e 等概念，这些在[第 5 章](05-init-deploy.md)有详细介绍。建议两章一起读。

### 4.1 同目录引用

```
my-project/
├── main.py
└── utils.py
```

```python
# main.py
from utils import greet

print(greet("world"))
```

```python
# utils.py
def greet(name):
    return f"Hello, {name}"
```

> 同目录下直接 `import 文件名`（不加 `.py`）即可。

#### ⚠️ 隐式 vs 显式相对导入

上面的写法 `from utils import greet` 是**隐式相对导入**——在 `python main.py` 直接运行时能工作，因为 Python 把脚本所在目录临时加入了 `sys.path`。

但如果 `main.py` 被当成**包的一部分**来导入（例如 `from my_project.main import ...`），隐式写法就会炸：

```python
# main.py — 被其他模块 import 时，隐式写法会报错
from utils import greet   # ❌ ModuleNotFoundError: No module named 'utils'
from .utils import greet  # ✅ 显式相对导入：从当前包（my_project）里找 utils
```

**规则：只要文件可能被 `import`（即作为包成员加载），就用显式写法 `.`**

| 写法 | 查找逻辑 | 何时可靠 |
|------|----------|----------|
| `from utils import greet` | 去 `sys.path` 顶层搜 `utils` | 只在直接运行脚本时 |
| `from .utils import greet` | 从**当前包**里搜 `utils` | 始终可靠 |

### 4.2 跨目录引用（同一项目内）

```
my-project/
├── main.py
└── helpers/
    ├── __init__.py
    └── string_utils.py
```

```python
# helpers/string_utils.py
def slugify(text):
    return text.lower().replace(" ", "-")
```

```python
# main.py
from helpers.string_utils import slugify

print(slugify("Hello World"))  # "hello-world"
```

> 关键：`helpers/` 目录下必须有 `__init__.py` 文件，Python 才会把它识别为"包"。
> Python 3.3 之后即使不写 `__init__.py` 也能导入（隐式命名空间包），但显式写上是好习惯。

#### `__init__.py` 里面放什么？

按用途从简到繁：

```python
# 1️⃣ 空文件 — 最常见的做法，只标记"这是包"
```

```python
# 2️⃣ 控制 from package import * 的范围
__all__ = ["core", "main"]
```

```python
# 3️⃣ 包级初始化 — import 时自动执行一次
import logging
logging.getLogger(__name__).info("my_project loaded")
```

```python
# 4️⃣ 扁平化 API — 从子模块重新导出（最实用）
from .core import Config, Database
from .api import router

# 用户可以直接写：
#   from my_project import Config, Database
# 而不需要：
#   from my_project.core import Config, Database
#   from my_project.api import router
```

### 4.3 `sys.path` 与 `PYTHONPATH`

如果项目结构比较复杂，可以用 `sys.path` 临时添加查找路径：

```python
# main.py
import sys
from pathlib import Path

# 把项目根目录加入 sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from another_package import module
```

更推荐的方式是设置环境变量 `PYTHONPATH`：

```bash
# 在终端中运行
PYTHONPATH=/path/to/project/src uv run main.py
```

> 建议：优先用标准的包结构（`src/` 布局）和 `uv run`，少手动改 `sys.path`。

### 4.4 跨项目引用

如果两个项目都想共享同一份代码，常见做法有：

#### 方案 A：做成可安装包（推荐）

在 `pyproject.toml` 中配置：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-shared-lib"
version = "0.1.0"
```

然后在另一个项目中安装：

```bash
# 本地可编辑安装
uv pip install -e /path/to/my-shared-lib

# 或在 pyproject.toml 中加入
# dependencies = ["my-shared-lib @ file:///path/to/my-shared-lib"]
```

> 可编辑安装 `-e` 意味着你对源码的修改会立即生效，不需要重新安装。

#### 方案 B：使用 `PYTHONPATH`

```bash
export PYTHONPATH="/path/to/shared/lib:$PYTHONPATH"
uv run main.py
```

#### 方案 C：发布到私有/公开 PyPI

如果多个项目长期共享，最好把公共代码打包发布到 PyPI 或私有仓库，然后在 `pyproject.toml` 中正常声明依赖。

### 4.5 跨模块引用变量

Python 的模块本质上就是一个**命名空间**，模块级定义的任何东西（变量、函数、类）都能被其他模块 import。

```python
# config.py
DEBUG = True
MAX_RETRY = 3
API_URL = "https://api.example.com"
```

```python
# main.py
from config import DEBUG, MAX_RETRY

if DEBUG:
    print(f"重试次数: {MAX_RETRY}")
```

#### 导入变量 vs 导入模块

```python
# 方式 1：直接导入变量 — 拿到的是值的"快照"
from config import DEBUG
print(DEBUG)         # True
DEBUG = False        # ⚠️ 只改了本模块的名字绑定，config.DEBUG 不变

# 方式 2：导入模块，通过模块访问 — 拿到的是"引用"
import config
print(config.DEBUG)  # True
config.DEBUG = False # 🔥 所有 import config 的模块都能看到这个变化
                     #    一般不推荐这样做，但有时在测试 mock 中有用
```

#### 常见坑

| 问题 | 说明 |
|------|------|
| **循环导入** | A `import` B，B 又 `import` A → 启动时其中一个拿到的变量是 `None`。解决：把 import 放到函数内部（延迟导入），或抽出一个共享模块打破循环 |
| **可变对象共享** | 跨模块共享同一个 `list` / `dict`，多个模块同时修改 → 难以追踪的 bug。尽量导出不可变对象或用深拷贝 |
| **模块级代码被执行** | `from xxx import y` 会执行 `xxx.py` 的**全部顶层代码**，不是只执行 `y` 那一个定义。不要在模块顶层做耗时操作或副作用 |

#### 汇总

| 场景 | 方式 |
|------|------|
| 同文件内的变量 | 直接使用 |
| 同目录其他文件的变量 | `from .module import var`（包内推荐 `.`） |
| 跨目录变量 | `from package.module import var` |
| 跨项目变量 | 将项目安装为包，再 `from other_project.module import var` |
| 环境变量/配置 | `os.environ` 或 `.env` + `python-dotenv` |

