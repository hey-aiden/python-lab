# 项目初始化与部署

> 📖 本章涵盖项目初始化、依赖管理、部署与发布。

### 5.1 工具对照

| 任务 | JavaScript (Node) | Python |
|------|-------------------|--------|
| 运行时代理 | Node.js | CPython (python3) |
| 包管理器 | npm / pnpm / yarn | uv / pip |
| 项目配置 | `package.json` | `pyproject.toml` |
| 锁文件 | `package-lock.json` | `uv.lock` |
| 依赖目录 | `node_modules/` | `.venv/lib/.../site-packages/` |
| 版本声明 | `.nvmrc` | `.python-version` |
| 运行脚本 | `npx` / `npm run` | `uv run` |
| 全局安装 | `npm install -g` | `pip install`（不推荐全局装） |
| 发布平台 | npm registry | PyPI (pypi.org) |

### 5.2 初始化项目

```bash
# JS:  npm init; npm install express
# Python:

# 1. 创建项目
uv init my-project
cd my-project

# 2. 添加依赖
uv add httpx           # 运行时依赖
uv add --dev pytest    # 开发依赖

# 3. 同步安装所有依赖
uv sync
```

生成的项目结构：

```
my-project/
├── pyproject.toml      # 类似 package.json
├── uv.lock             # 类似 package-lock.json
├── .python-version     # 类似 .nvmrc
├── .venv/              # 类似 node_modules/，但全局共享一个解释器
├── README.md
└── hello.py
```

#### `pyproject.toml` 字段详解

> 类似 `package.json`，但字段更多、更结构化。以下是逐段拆解。

```toml
# ═══════════════════════════════════════════════
# [build-system] — 构建工具声明
# ═══════════════════════════════════════════════
[build-system]
requires = ["hatchling"]        # 构建时需要的工具包
build-backend = "hatchling.build"
# 相当于 npm 的 "用什么打包"。常见选项：
#   hatchling  — 轻量，uv init 默认，推荐
#   setuptools — 老牌，兼容性最好
#   flit       — 极简，只做纯 Python 包
#   不写这节 → uv sync 会报错（src/ 布局需要构建）

# ═══════════════════════════════════════════════
# [project] — 项目元信息（必填）
# ═══════════════════════════════════════════════
[project]
name = "basic-python"           # PyPI 上的包名（可用连字符）
version = "0.1.0"               # 语义版本
description = "..."             # 一句话描述（PyPI 展示用）
readme = "README.md"            # 长说明文件（PyPI 展示用）
requires-python = ">=3.11"      # 要求 Python ≥ 3.11
dependencies = [                # 运行时依赖（用户装这个包时自动安装）
    "httpx>=0.27",
    "click>=8",
]
# 最佳实践：dependencies 只放运行时必需的最小集合

# ═══════════════════════════════════════════════
# [dependency-groups] — 按场景分组的可选依赖
# ═══════════════════════════════════════════════
[dependency-groups]
dev = [                         # uv sync 默认安装
    "pytest>=9.1.1",            # 测试框架
    "ruff>=0.5",                # lint + 格式化
]
# 其他常见分组：
#   test  — uv sync --group test 或 CI 专用
#   docs  — uv sync --group docs 文档构建用
#   dev   — 默认安装（等价于 npm devDependencies）

# ═══════════════════════════════════════════════
# [tool.hatch.build.targets.wheel] — 包发现
# ═══════════════════════════════════════════════
[tool.hatch.build.targets.wheel]
packages = ["src/app"]          # 告诉 hatchling 去哪里找包
# 如果不写，hatchling 默认从根目录找包，可能漏掉 src/

# ═══════════════════════════════════════════════
# [project.scripts] — CLI 入口（可选，发布工具时写）
# ═══════════════════════════════════════════════
# [project.scripts]
# my-cli = "app.cli:main"       # pip install 后直接敲 my-cli 就能用
# 类似 npm 的 "bin" 字段
```

**字段对照速查：**

| `pyproject.toml` | `package.json` | 说明 |
|---|---|---|
| `[project] name` | `"name"` | 包名 |
| `[project] version` | `"version"` | 版本 |
| `[project] dependencies` | `"dependencies"` | 运行时依赖 |
| `[dependency-groups] dev` | `"devDependencies"` | 开发依赖 |
| `[project.scripts]` | `"bin"` | CLI 入口 |
| `[build-system]` | `—`（Node 隐式用 npm） | 构建工具 |
| `requires-python` | `"engines": {"node": ">=18"}` | 运行时版本 |
| `uv.lock` | `package-lock.json` | 锁文件 |

> **一句话**：`[project]` 描述你是谁，`[build-system]` 说怎么打包，`[dependency-groups]` 管理依赖分组，`[tool.*]` 是各工具的私人配置区。

#### 在已有目录中初始化

`uv init` 支持对已有内容的目录进行初始化：

```bash
# 方式 1：cd 进去执行
cd existing-folder
uv init

# 方式 2：指定路径
uv init existing-folder

# 指定项目名
uv init --name "my-project" .
```

**已存在文件的行为：**

| 文件 | 已存在时 | 不存在时 |
|------|----------|----------|
| `pyproject.toml` | ❌ 报错退出，不覆盖 | 自动创建 |
| `README.md` | 保留不动 | 自动生成模板 |
| `hello.py` | 跳过不建 | 自动创建示例 |

```bash
# 如果已有 pyproject.toml 但仍想重新初始化
uv init --force          # 强制执行（谨慎，会覆盖 pyproject.toml）
```

**最佳安全实践** — 只想补一个 `pyproject.toml` 而不影响其他文件：

```bash
# 在临时目录生成，复制过来
uv init /tmp/temp-project
cp /tmp/temp-project/pyproject.toml ./
# 然后手动编辑 pyproject.toml 改成实际项目信息
```

**适用场景：** 已有代码目录想接入 `uv` 生态时，直接 `uv init` 即可，已有的 `.py` 文件不会受任何影响。

### 5.3 入口文件与 `if __name__ == "__main__"`

> 关于运行方式（`python file.py` vs `python -m` vs `uv run`），详见[第 1 章](01-quickstart.md)。

```python
# hello.py

def main():
    print("Hello, World!")

# JS 没有这个模式，Python 需要显式判断
# 当 python hello.py 直接运行：True，执行 main()
# 当 import hello 导入：       False，不执行
if __name__ == "__main__":
    main()
```

### 5.4 部署方式

#### 脚本/工具 → 直接运行

```bash
# 目标机器安装 uv，然后：
uv sync
uv run main.py
```

#### Web 服务 → Docker

```dockerfile
# 简化示例
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
COPY src/ ./src/
CMD ["uv", "run", "gunicorn", "src.app:app"]
```

#### 发布到 PyPI

```bash
uv build                    # 构建 wheel 包
uv publish                  # 发布到 PyPI（类似 npm publish）
```

```toml
# pyproject.toml 中需要额外配置
[project.scripts]
my-cli = "my_package.cli:main"   # 注册 CLI 入口（类似 npm bin）
```
