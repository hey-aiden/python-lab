# uv 常用命令速查

> uv 是 Astral 开发的极速 Python 包管理器，用 Rust 编写，比 pip 快 10-100 倍。

## 安装

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew
brew install uv
```

---

## 项目管理

```bash
# 初始化新项目（创建 pyproject.toml）
uv init myproject
cd myproject

# 初始化已有目录
uv init
```

---

## 虚拟环境

```bash
# 创建虚拟环境（默认 .venv）
uv venv

# 指定 Python 版本
uv venv --python 3.11
uv venv --python 3.12

# 指定环境目录名
uv venv .env
```

---

## 依赖管理

```bash
# 添加依赖
uv add requests
uv add "flask>=2.0"
uv add pytest --dev          # 开发依赖

# 添加 Git 依赖
uv add git+https://github.com/user/repo

# 移除依赖
uv remove requests

# 安装所有依赖（从 pyproject.toml）
uv sync

# 安装依赖（不锁定，类似 pip install）
uv pip install -r requirements.txt
```

---

## 运行代码

```bash
# 在虚拟环境中运行脚本
uv run python main.py

# 运行模块
uv run python -m pytest

# 运行入口点（如果配置了）
uv run myapp

# 一次性运行（临时安装依赖）
uv run --with requests python script.py
```

---

## 包安装（pip 兼容模式）

```bash
# 安装包
uv pip install requests

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 卸载
uv pip uninstall requests

# 列出已安装
uv pip list

# 显示包信息
uv pip show requests

# 冻结依赖
uv pip freeze > requirements.txt
```

---

## Python 版本管理

```bash
# 列出可用 Python 版本
uv python list

# 安装 Python 版本
uv python install 3.12
uv python install 3.11 3.12

# 查找 Python 解释器
uv python find 3.11

# 固定项目 Python 版本
uv python pin 3.11
```

---

## 工具安装（全局命令）

```bash
# 安装全局工具
uv tool install ruff
uv tool install black
uv tool install httpie

# 运行工具（不安装）
uvx ruff check .

# 列出已安装工具
uv tool list

# 更新工具
uv tool upgrade ruff

# 卸载工具
uv tool uninstall ruff
```

---

## 发布包

```bash
# 构建分发包
uv build

# 发布到 PyPI
uv publish

# 发布到测试 PyPI
uv publish --index-url https://test.pypi.org/simple/
```

---

## 常用组合

```bash
# 快速启动新项目
uv init myapp && cd myapp
uv add flask
uv run python -m flask run

# 从 requirements.txt 迁移
uv init
uv add $(cat requirements.txt | tr '\n' ' ')

# 数据科学项目
uv init ml-project
uv add numpy pandas scikit-learn jupyter
uv run jupyter lab
```

---

## 配置文件

uv 读取以下配置：
- `pyproject.toml` - 项目依赖
- `uv.toml` - uv 专用配置（可选）
- `.python-version` - 固定 Python 版本

---

## 对比 pip

| pip | uv |
|-----|-----|
| `pip install requests` | `uv add requests` 或 `uv pip install requests` |
| `pip install -r req.txt` | `uv pip install -r req.txt` |
| `pip freeze > req.txt` | `uv pip freeze > req.txt` |
| `python -m venv .venv` | `uv venv` |
| 无 | `uv run python main.py` |

---

## 官方文档

https://docs.astral.sh/uv/
