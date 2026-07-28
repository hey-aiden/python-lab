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

### 4.5 引用外部变量的几种方式

| 场景 | 方式 |
|------|------|
| 同文件内的变量 | 直接使用 |
| 同目录其他文件的变量 | `from module import var` |
| 跨目录变量 | `from package.module import var` |
| 跨项目变量 | 将项目安装为包，再 `from other_project.module import var` |
| 环境变量/配置 | `os.environ` 或 `.env` + `python-dotenv` |

