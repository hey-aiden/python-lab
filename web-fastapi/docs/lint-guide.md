# Python 代码质量工具（Lint & Format）

> 对应 JS 生态的 ESLint + Prettier，Python 用 Ruff 一个工具全搞定。

---

## 1. 工具对比

| 功能 | JS 生态 | Python 生态 | 说明 |
|------|---------|------------|------|
| 代码检查 | ESLint | **Ruff** | 未使用变量、import 排序、可简化写法 |
| 代码格式化 | Prettier | **Ruff format**（或 Black） | 统一缩进、引号、换行 |
| 类型检查 | TypeScript | **mypy** | 检查类型不匹配 |

Ruff 已经同时覆盖了 ESLint + Prettier 的功能，用 Rust 写成，速度极快。

---

## 2. 安装与配置

### 安装

```bash
uv add --dev ruff
```

### 配置

`pyproject.toml`：

```toml
[tool.ruff]
line-length = 100           # 每行最大长度
target-version = "py311"    # 目标 Python 版本

[tool.ruff.lint]
select = [
    "F",      # Pyflakes — 未使用的 import、未定义变量、语法错误
    "I",      # isort — import 顺序（标准库 → 第三方 → 本地）
    "SIM",    # flake8-simplify — 可简化的写法（如 if x == True → if x）
]

[tool.ruff.lint.isort]
known-first-party = ["app"]   # 标记 app 为本项目包，排在第三方之后

[tool.ruff.format]
quote-style = "double"        # 统一用双引号
```

### 常用规则集

| 规则码 | 来源 | 检查内容 | 示例 |
|--------|------|---------|------|
| `F` | Pyflakes | 未使用 import、重复定义、语法错误 | `F401`: imported but unused |
| `I` | isort | import 顺序不正确 | 自动排序 |
| `SIM` | flake8-simplify | 多余的写法 | `if x == True` → `if x` |
| `E` / `W` | pycodestyle | 空白、缩进等风格问题 | 行尾空格 |
| `N` | pep8-naming | 命名规范 | 类必须用 PascalCase |
| `UP` | pyupgrade | 新版本 Python 语法 | `Optional[int]` → `int \| None` |
| `B` | flake8-bugbear | 常见 bug | 可变默认参数 |

按需加到 `select` 即可。

---

## 3. 日常使用

```bash
# 检查所有问题
uv run ruff check src/

# 自动修复（import 排序、删未使用变量等）
uv run ruff check --fix src/

# 格式化代码
uv run ruff format src/

# 一条命令：修复 + 格式化
uv run ruff check --fix src/ && uv run ruff format src/
```

---

## 4. 常见检查场景

### 4.1 import 顺序不对

```python
# ❌ ruff 报 I001: Import block is un-sorted
from pydantic import BaseModel
from datetime import datetime       # ← 标准库应排在最前面

# ✅ 修复后
from datetime import datetime       # ← 标准库

from pydantic import BaseModel      # ← 第三方
```

排序规则：**标准库 → 第三方 → 本地项目**，每组内部按字母序。

### 4.2 import 了但没用过

```python
# ❌ ruff 报 F401: imported but unused
from app.models.user import User

# ✅ 方案一：通过 __all__ 声明为公开导出
from app.models.user import User
__all__ = ["User"]

# ✅ 方案二：给 linter 标记（如果确实只需要副作用）
from app.models.user import User  # noqa: F401
```

### 4.3 可以简化的写法

```python
# ❌ ruff 报 SIM210: Use `bool(x)` instead of `True if x else False`
result = True if x > 0 else False

# ✅ 简化后
result = bool(x > 0)

# ❌ ruff 报 SIM103: Return the condition directly
if x > 0:
    return True
return False

# ✅ 简化后
return x > 0
```

---

## 5. CI 集成

在 CI workflow 中加入检查步骤（见 `github-runner-cicd.md`）：

```yaml
# .github/workflows/ci.yml
jobs:
  lint:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run ruff check src/
      - run: uv run ruff format --check src/    # 只检查不改
```

---

## 6. 速查

```bash
uv add --dev ruff                                # 安装
uv run ruff check src/                           # 检查
uv run ruff check --fix src/                     # 自动修复
uv run ruff format src/                          # 格式化
uv run ruff check --fix src/ && uv run ruff format src/   # 一键全修
```
