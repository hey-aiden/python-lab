# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python 学习实验仓库，包含两个代码目录：

- **`old-version/`** — 原始 Python 示例与实验脚本（MySQL、GUI、HTTPX、文件 IO、正则等），`uv` 管理依赖
- **`basic-python/`** — 最新的 Python 基础学习代码

## Build/Run Commands

```bash
# 运行脚本（在 old-version/ 目录下）
uv run <script.py>

# 或通过 Makefile
make run          # 运行 mysql_demo.py
make demo         # 同上
make gui          # 运行 gui_code.py

# 依赖管理
uv sync           # 安装/同步依赖
uv add <pkg>      # 添加新依赖
uv pip list       # 查看已安装的包
```

## Environment

- **Python**: >= 3.9（macOS 系统自带 3.9.6）
- **包管理器**: [uv](https://docs.astral.sh/uv/) v0.10.12+
- **依赖**: `httpx`, `mysql-connector-python`
- **平台**: macOS（部分脚本涉及 macOS 特有问题，如 tkinter GUI 版本兼容）

## Architecture Notes

- 仓库为**学习用途**，各 `.py` 文件之间无模块依赖关系，每个脚本独立运行
- `pyproject.toml` 位于 `old-version/` 下，新代码在 `basic-python/` 下
- 使用 `uv run` 而非直接 `python` 执行脚本——`uv` 管理虚拟环境和 Python 版本
- `uv python pin` 只在 `uv run` 下生效，直接 `python` 命令用的是系统 PATH 中的版本
- 避免使用 `mysql.py`、`email.py`、`json.py` 等与标准库/第三方包同名的文件名，会导致导入冲突
