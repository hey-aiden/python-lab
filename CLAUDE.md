# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python 学习实验仓库，包含以下子项目：

| 目录 | 用途 | 包管理器 |
|------|------|----------|
| **`old-version/`** | 原始 Python 示例与实验脚本（MySQL、GUI、HTTPX、文件 IO、正则等） | `uv` |
| **`basic-python/`** | 最新的 Python 基础学习代码 | — |
| **`guide-python/`** | Python 学习指南 + 代码示例（标准库、文件 IO、导入规则等） | `uv` |
| **`web-fastapi/`** | FastAPI 生产级目录结构实验（router/service/middleware 分层） | `uv` |

## Build/Run Commands

### old-version/

```bash
cd old-version
uv run <script.py>           # 运行脚本
make run                      # 运行 mysql_demo.py
make gui                      # 运行 gui_code.py
```

### guide-python/

```bash
cd guide-python
uv run app                    # 运行入口程序
uv run pytest                 # 运行测试
```

### web-fastapi/

```bash
cd web-fastapi
uv run dev                    # 开发服务器（自动 reload + 释放 8000 端口）
uv run pytest                 # 运行测试
```

### 通用

```bash
uv sync                       # 安装/同步依赖
uv add <pkg>                  # 添加依赖
uv add --dev <pkg>            # 添加开发依赖
```

## Environment

- **Python**: >= 3.11（推荐通过 pyenv 管理）
- **包管理器**: [uv](https://docs.astral.sh/uv/)
- **平台**: macOS

## Architecture Notes

### guide-python

- `src/` 布局：`app/`（入口）、`base_use/`（基础用法示例）、`type_use/`（类型使用）
- 包内推荐**显式相对导入** `from .module import xxx`
- `pyproject.toml` 的 `[project.scripts]` 只能放 `模块:函数` 引用，不能放 shell 命令

### web-fastapi

- 分层架构：`endpoints → services → schemas`，middleware 独立一层
- services 层不依赖 FastAPI，纯 Python 可独立测试
- `dev()` 函数启动前自动释放 8000 端口
- 测试用 `pytest` + `httpx.AsyncClient`，`tests/conftest.py` 提供 client fixture

### 通用规则

- 使用 `uv run` 而非直接 `python`——`uv` 管理虚拟环境和 Python 版本
- `uv python pin` 只在 `uv run` 下生效，直接 `python` 用的是系统 PATH 中的版本
- 避免使用 `mysql.py`、`email.py`、`json.py` 等与标准库/第三方包同名的文件名
