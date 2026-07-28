# Python 工具链：pyenv、uv、poetry 三种工作模式

> 📖 本章深入对比三种主流 Python 开发工作模式，帮你选择最适合的工具链。如需深入了解 uv 的具体用法，可参考[第 2 章](02-toolchain.md)。

---

## 一句话总结

| 工具 | 定位 | 核心职责 |
|------|------|----------|
| **pyenv** | 解释器版本管理器 | 只管"用哪个 Python"，不管包 |
| **uv** | 一体化项目管理工具 | 管 Python 版本 + 虚拟环境 + 包 + 构建（全家桶） |
| **poetry** | 一体化项目管理工具 | 管 Python 版本 + 虚拟环境 + 包 + 构建（全家桶） |

---

## 三种工作模式详解

### 模式 A：pyenv + venv + pip（经典组合）

> 最传统的方式，三个工具各司其职，适合需要精细控制的场景。

```bash
# 1. pyenv 安装并切换 Python 版本
pyenv install 3.12.4
pyenv local 3.12.4          # 生成 .python-version

# 2. venv 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 3. pip 安装依赖
pip install httpx
pip freeze > requirements.txt   # 手动导出依赖列表
```

**特有文件：**

| 文件 | 来源 | 作用 |
|------|------|------|
| `.python-version` | pyenv | 记录当前目录使用的 Python 版本 |
| `.venv/` | venv | 虚拟环境目录（手动创建） |
| `requirements.txt` | pip | 依赖列表（手动维护） |

**优缺点：**

- ✅ 工具独立，灵活组合
- ✅ 社区最广泛，几乎所有 Python 项目都兼容
- ❌ 没有锁文件，依赖版本不精确（`pip freeze` 列出所有传递依赖，会污染列表）
- ❌ 需要手动管理多个步骤
- ❌ 没有统一的项目配置（`requirements.txt` 不是项目元数据）
- 💡 改进方案：搭配 `pip-tools`（`requirements.in` → `pip-compile` → `requirements.txt`），可生成带精确版本的锁定文件

---

### 模式 B：uv（现代一体化）

> 近年社区主流推荐，由 Astral 团队开发，速度快、功能全。

```bash
# 1. 初始化项目
uv init my-project
cd my-project

# 2. 指定 Python 版本（uv 自带）
uv python pin 3.12.4        # 生成 .python-version

# 3. 添加依赖（自动创建 .venv）
uv add httpx
uv add --dev pytest

# 4. 同步安装所有依赖
uv sync

# 5. 运行脚本（自动使用 .venv）
uv run python -m my_project.main
# src/ 布局下推荐用 -m；单文件项目用 uv run python main.py

# 6. 测试
uv run pytest
```

**特有文件：**

| 文件 | 来源 | 作用 |
|------|------|------|
| `pyproject.toml` | uv | 项目配置（类似 `package.json`） |
| `uv.lock` | uv | 精确锁定的依赖树（类似 `package-lock.json`） |
| `.python-version` | uv / pyenv | 当前目录使用的 Python 版本 |
| `.venv/` | uv 自动创建 | 虚拟环境（不要提交到 Git） |

**优缺点：**

- ✅ 一个工具搞定所有事
- ✅ 速度极快（Rust 实现）
- ✅ 精确锁文件，依赖可复现
- ✅ 兼容 `pip` 生态，可替代 `pip`、`venv`、`pip-tools`
- ❌ 较新（2024 年兴起），部分老项目文档未更新
- ❌ 学习曲线稍陡（功能多）

---

### 模式 C：poetry（成熟一体化）

> 老牌一体化工具，社区大、文档全，适合需要稳定生态的项目。

```bash
# 1. 初始化项目（任选其一）
poetry new my-project      # 创建目录 + 完整脚手架（对标 uv init my-project）
# 或
poetry init                # 只在当前目录交互式创建 pyproject.toml

# 2. 指定 Python 版本（在 pyproject.toml 中）
# [tool.poetry.dependencies]
# python = "^3.11"

# 3. 添加依赖（自动创建 .venv）
poetry add httpx
poetry add --group dev pytest

# 4. 安装所有依赖
poetry install

# 5. 运行脚本（自动使用 .venv）
poetry run python main.py
```

**特有文件：**

| 文件 | 来源 | 作用 |
|------|------|------|
| `pyproject.toml` | poetry | 项目配置（poetry 专用格式） |
| `poetry.lock` | poetry | 精确锁定的依赖树 |
| `.venv/` | poetry 自动创建 | 虚拟环境（poetry 创建，位置可配置） |

**优缺点：**

- ✅ 成熟稳定（2018 年发布）
- ✅ 文档丰富，社区大
- ✅ 依赖解析精确，有锁文件
- ✅ 支持发布到 PyPI（`poetry publish`）
- ❌ 速度较慢（Python 实现）
- ❌ `pyproject.toml` 格式与 `uv` 略有不同（不兼容 `[tool.uv]` 节）
- ❌ 虚拟环境位置默认在系统缓存，不在项目目录（需配置）

---

## 文件对照表

| 文件 | pyenv + venv + pip | uv | poetry |
|------|:----------:|:-------:|:-----------:|
| `.python-version` | ✅ pyenv 生成 | ✅ `uv python pin` | ❌（但可与 pyenv 组合使用） |
| `.venv/` | ✅ 手动创建 | ✅ 自动创建 | ✅ 自动创建（默认不在项目目录） |
| `pyproject.toml` | ❌ 可选 | ✅ 核心配置 | ✅ 核心配置（格式不同） |
| `uv.lock` | ❌ | ✅ | ❌ |
| `poetry.lock` | ❌ | ❌ | ✅ |
| `requirements.txt` | ✅ 手动维护 | ❌ | ❌ |

---

## 如何选择？

| 场景 | 推荐工具 |
|------|----------|
| **新项目，追求速度和现代体验** | uv |
| **老项目，已有 poetry 生态** | poetry |
| **需要和 pip/venv 深度集成** | pyenv + venv + pip |
| **CI/CD 环境，需要快速安装** | uv（速度快） |
| **发布库到 PyPI** | uv 或 poetry（都支持） |
| **团队已有成熟的工作流** | 保持现状 |

### 决策树

```
需要发布到 PyPI？
  ├─ 是 → uv（推荐）或 poetry
  └─ 否 → 继续

团队已有 poetry 项目？
  ├─ 是 → poetry（保持一致）
  └─ 否 → 继续

追求最快体验 + 现代工具？
  ├─ 是 → uv
  └─ 否 → 继续

需要精细控制每个工具？
  ├─ 是 → pyenv + venv + pip
  └─ 否 → uv（默认推荐）
```

---

## 工具组合的可能性

| 组合 | 说明 |
|------|------|
| `pyenv` + `uv` | pyenv 管解释器版本，uv 管包（互补，推荐） |
| `pyenv` + `poetry` | pyenv 管解释器版本，poetry 管包（互补，推荐） |
| `uv` 单独使用 | uv 内置 Python 版本管理（`uv python pin`） |
| `poetry` 单独使用 | poetry 内置 Python 版本管理（在 `pyproject.toml` 中） |

> **关键原则**：解释器版本管理和包管理是两件事。`pyenv` 只做前者，`uv`/`poetry` 做后者。它们可以组合，也可以只用 `uv`/`poetry` 一把梭。

---

## 常见坑点

### 1. `.venv` 位置不同

| 工具 | 默认位置 | 配置方式 |
|------|----------|----------|
| venv | 项目目录 `.venv/` | — |
| uv | 项目目录 `.venv/` | 默认创建在项目目录，无需额外配置 |
| poetry | 系统缓存 `~/.cache/pypoetry/...` | `poetry config virtualenvs.in-project true` |

> **建议**：让 `.venv` 在项目目录内，方便 IDE 识别和调试。

### 2. `pyproject.toml` 格式不兼容

```toml
# uv 格式（标准 PEP 621）
[project]
dependencies = ["httpx"]

# poetry 格式（专有）
[tool.poetry.dependencies]
httpx = "^0.27"
```

> 两者不能混用。切换工具需要迁移配置。

### 3. 锁文件格式

- `uv.lock`：TOML 格式，人类可读
- `poetry.lock`：TOML 格式，人类可读
- `requirements.txt`：纯文本，每行一个包

> 不要手动编辑锁文件，用工具生成。

---

## 一句话速查

| 需求 | 命令 |
|------|------|
| 创建新项目（uv） | `uv init my-project` |
| 创建新项目（poetry） | `poetry new my-project`（或 `poetry init`） |
| 添加依赖（uv） | `uv add httpx` |
| 添加依赖（poetry） | `poetry add httpx` |
| 安装依赖（uv） | `uv sync` |
| 安装依赖（poetry） | `poetry install` |
| 运行脚本（uv） | `uv run python main.py` |
| 运行脚本（poetry） | `poetry run python main.py` |
| 激活虚拟环境（手动） | `source .venv/bin/activate` |

---

> **总结**：uv 是当前推荐的选择（速度快、功能全），poetry 适合已有生态的项目，pyenv + venv + pip 适合需要精细控制的场景。三者可以组合，也可以单独使用。
