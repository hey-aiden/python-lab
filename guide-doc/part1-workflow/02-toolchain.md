# Python 开发方式与工具链

> 📖 本章详细介绍 pyenv / uv / venv 的关系和用法。建议先读第 1 章建立全局观，再回来看本章的细节。

### 2.1 解释器、版本管理与环境管理

Python 是**解释型语言**，运行代码需要一个 Python 解释器（通常是 CPython，也就是你从 `python3` 命令启动的那个程序）。围绕它，有三类工具最容易混淆：

| 层级 | 工具 | 作用 | 对标 JS |
|------|------|------|---------|
| 解释器版本管理 | `pyenv` | 安装/切换不同 Python 版本 | `nvm` |
| 虚拟环境 | `venv` / `virtualenv` | 创建隔离的项目依赖环境 | 类似 `node_modules` + 独立的 `node` |
| 包 + 项目管理 | `uv` | 安装包、管理虚拟环境、锁定依赖、构建、发布 | `npm` / `pnpm` |

#### `pyenv` —— 管理 Python 版本

```bash
# 安装一个 Python 版本
pyenv install 3.12.4

# 设置为当前目录使用的版本（类似 .nvmrc）
pyenv local 3.12.4

# 查看已安装的版本
pyenv versions
```

- `pyenv` 的核心任务只有一个：**让不同的目录使用不同的 Python 解释器版本**。
- 它本身不管理第三方包；它只负责让 `python3` 指向正确的解释器。

#### `venv` / `virtualenv` —— 隔离的 Python 环境

```bash
# 创建一个虚拟环境（在当前目录创建 .venv/）
python3 -m venv .venv

# 激活它
source .venv/bin/activate

# 退出
deactivate
```

- 每个虚拟环境有自己的 `site-packages`，不同项目不会互相污染。
- `.venv/` 类似 JS 的 `node_modules/`，但 Python 的虚拟环境还包含了一份指向解释器的符号链接。

#### `uv` —— 现代的 Python 包与项目管理工具

`uv` 是近年社区主流推荐的工具，由 Astral 团队开发，集成了传统 Python 工作流中多个分散的工具：

| 传统工具 | `uv` 的替代命令 | 作用 |
|----------|----------------|------|
| `pip` | `uv pip install` / `uv add` | 安装包 |
| `venv` | `uv venv` | 创建虚拟环境 |
| `pip-tools` | `uv.lock` | 依赖锁定 |
| `build` / `twine` | `uv build` / `uv publish` | 构建与发布包 |
| `python -m venv` | `uv run` | 自动使用项目虚拟环境运行脚本 |

#### `uv` 与 `pyenv` 的关系

两者是**互补**的，不是替代关系：

- **`pyenv`** 负责**解释器版本**：让不同目录使用 Python 3.9 / 3.10 / 3.12 等。
- **`uv`** 负责**项目依赖与运行环境**：在当前选定的解释器上创建虚拟环境、安装包、锁定版本。

典型协作方式：

```bash
# 1. 用 pyenv 安装并切换 Python 版本
pyenv install 3.12.4
pyenv local 3.12.4       # 生成 .python-version 文件

# 2. 用 uv 初始化项目
uv init my-project

# 3. uv 会自动使用当前 Python 解释器创建 .venv/
uv sync

# 4. 运行脚本
uv run main.py
```

> 简单记忆：`pyenv` 选 "哪个 Python"，`uv` 选 "这个项目用什么包"。

当然，`uv` 本身也能管理 Python 版本：

```bash
# 查看/安装/切换 Python 版本（uv 内置）
uv python list
uv python install 3.12.4
uv python pin 3.12.4      # 生成 .python-version
```

如果你只用 `uv`，可以不需要 `pyenv`；如果你习惯多版本切换或在其他工具链中也需要 Python 版本管理，`pyenv` 仍然是好选择。

### 2.2 推荐的开发工作流

```bash
# 1. 进入项目目录
cd my-project

# 2. 指定 Python 版本（pyenv 或 uv python pin）
pyenv local 3.12.4
# 或
uv python pin 3.12.4

# 3. 初始化/同步依赖
uv sync

# 4. 运行脚本
uv run main.py

# 5. 添加新依赖
uv add httpx
uv add --dev pytest

# 6. 测试
uv run pytest
```

