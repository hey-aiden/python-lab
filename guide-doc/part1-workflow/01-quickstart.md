# 完整开发路径：从 0 到运行

> 📖 本章是全文的总览图，建议快速通读建立全局印象。文中出现的工具（`uv`、`pyenv`）会在第 2 章详解，项目结构见第 3 章，跨项目引用见第 4 章——先看整体，再读细节。

从一个空目录到一个可发布的项目，以下是完整的 Python 开发工作路径：

```bash
# 1. 安装/确认工具
#    - Python 解释器（系统自带或 pyenv 安装）
#    - uv 包管理器

# 2. 创建项目目录
cd ~/projects
uv init my-project
cd my-project

# 3. 指定 Python 版本
uv python pin 3.12.4
# 或 pyenv local 3.12.4

# 4. 设计目录结构（src/ 布局）
# ⚠️ 注意：目录用 my-project（连字符），Python 包用 my_project（下划线）
#     Python 模块名不允许连字符，会被解析为减号！
mkdir -p src/my_project tests

# 5. 编写源码
#    src/my_project/__init__.py
#    src/my_project/core.py
#    src/my_project/main.py

# 6. 添加依赖并同步
uv add httpx
uv add --dev pytest hatchling
uv sync

# 7. 运行和测试
uv run python -m my_project.main
uv run pytest

# 8. 跨项目共享时
#    - 把公共代码整理成 src/my_shared_lib/
#    - 在 pyproject.toml 中配置打包信息
#    - uv build
#    - uv publish  # 或本地 -e 安装
```

### `uv init` 详解：新项目 vs 已有目录

`uv init` 不仅可以在**新目录**中创建项目，还能在**已有代码目录**中补充项目配置。

#### ① 在空白新目录中创建（最常用）

```bash
uv init my-project
# 生成：
#   my-project/
#   ├── pyproject.toml      # 项目元数据 + 构建配置
#   ├── README.md
#   ├── .python-version     # 锁定的 Python 版本
#   └── src/
#       └── my_project/     # 🆕 自动创建包目录
#           └── __init__.py
```

默认 `uv init` 等价于 `uv init --package`，会创建 `src/` 布局和一个初始包。如果你只是写个单文件脚本，用：

```bash
uv init my-project --app     # 应用模式：不创建 src/ 包，适合扁平结构
uv init --bare               # 极简：只生成 pyproject.toml，其他什么都不创建
```

#### ② 在已有代码目录中初始化（最关键）

当你**已经有一堆 `.py` 文件**，想用 `uv` 管理依赖时，不需要重建项目——直接在目录里执行 `uv init`：

```bash
# 场景：你有一个已存在的代码目录
cd ~/projects/existing-code
ls
# main.py   utils.py   data_loader.py   # 手写的 .py 文件

# 直接在当前目录初始化
uv init . --app --no-readme --name my-data-tool

# 生成：
#   pyproject.toml         # 新建，包含 [project] 元数据
#   .python-version        # 新建（或自动检测当前 Python 版本）

# 你的原有文件不受影响：
# main.py   utils.py   data_loader.py    # 全部保留！
```

**关键选项说明：**

| 选项 | 作用 | 适用场景 |
|------|------|----------|
| `--app` | 项目作为**应用**，不创建 `src/` 包 | 已有扁平目录、单文件项目、脚本集合 |
| `--lib` | 项目作为**库**，创建 `src/` 布局 + `__init__.py` | 需要被其他项目依赖/安装 |
| `--package` | 同 `--lib`（默认行为） | 标准 Python 包 |
| `--bare` | 只生成 `pyproject.toml`，不创建任何目录 | 已有完整结构，只需要补充配置 |
| `--name <name>` | 指定包名（否则自动从目录名推断） | 目录名为连字符时很有用 |
| `--no-readme` | 不创建 `README.md` | 已有 README，不想覆盖 |
| `--build-backend <backend>` | 选择构建后端 | `hatch`、`setuptools`、`flit` 等 |
| `--no-pin-python` | 不创建 `.python-version` | 用 `pyenv` 管理 Python 版本 |
| `--vcs none` | 不初始化 git | 已有 git 仓库或非 git 项目 |

#### ③ 已有目录 → 完整 src/ 布局的迁移

假设你有一个 flat 结构的项目，想迁移到规范的 `src/` 布局：

```bash
# 原始状态（flat 结构）
# my-app/
# ├── main.py
# ├── core.py
# └── utils.py

# 步骤 1：确定包名（项目名叫 my-app，包名用 my_app）
# 步骤 2：用 --app 先初始化（不创建 src/，避免冲突）
cd my-app
uv init . --app

# 步骤 3：手动创建 src/ 结构
mkdir -p src/my_app
mv *.py src/my_app/
touch src/my_app/__init__.py

# 步骤 4：更新 pyproject.toml，确保 [tool.hatch.build.targets.wheel]
#         包含 packages = ["src/my_app"]
```

> 💡 实际上，如果目录下已经有代码文件，更推荐**先 `uv init . --app`** 生成最小配置，然后按需手动调整目录结构，而不是让 `uv init` 自动创建你可能不需要的 `src/` 包。

#### ④ 仓库中的实际示例

本仓库中有三个项目，分别展示了不同的 `uv init` 使用方式：

**`guide-python/` — 标准的 `--package`（默认）模式**

```
guide-python/
├── pyproject.toml          # [build-system] hatchling + [project.scripts]
├── .python-version          # 3.11
└── src/
    ├── app/                 # 入口包
    │   └── main.py
    └── base_use/            # 基础示例包
        └── io_use.py
```

pyproject.toml 关键配置：
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "guide-python"
requires-python = ">=3.11"

[project.scripts]
app = "app.main:main"                    # ← uv run app 即可运行

[tool.hatch.build.targets.wheel]
packages = ["src/app", "src/base_use"]   # ← 手动声明要打包的子包
```

**`web-fastapi/` — 带丰富依赖的 `--package` 模式**

```
web-fastapi/
├── pyproject.toml          # [build-system] hatchling + 大量依赖 + ruff 配置
├── .python-version          # 3.11
└── src/
    └── app/                 # FastAPI 应用（router/service/middleware 分层）
```

**`old-version/` — flat 结构（无 `src/`），无 build-system**

```
old-version/
├── pyproject.toml           # 只有 [project]，没有 [build-system]
├── mysql_demo.py            # .py 文件直接放在根目录
├── gui_code.py
└── ...
```

这是 `uv init --app` 或手动编写的典型产物——不需要构建分发，只管理依赖。

> 📌 **选型建议**：如果项目需要被别人 `pip install` 或 `uv add` 引用，用 `--package`/`--lib` 模式 + `src/` 布局；如果只是自己运行的脚本集合，用 `--app` 模式就够了。

### 如何运行 Python 代码

Python 有三种运行方式，按场景选择：

#### ① 运行单个 `.py` 文件

```bash
# 最简单：直接给 python 一个文件路径
python hello.py                # 用系统 Python
uv run python hello.py         # 用项目 .venv 里的 Python（推荐）

# 文件放在任何位置都可以
uv run python src/my_project/main.py
uv run python /path/to/any/script.py
```

#### ② 以模块方式运行（`-m`）

```bash
# python -m 包.模块，用 . 号分隔路径
uv run python -m my_project.main
#                     ↑           ↑
#                   包名      模块名（不加 .py）

# 等价关系：
#   python -m my_project.main   ≈  python src/my_project/main.py
#   -m 会把 my_project 当成包来导入，__init__.py 也会执行
```

#### ③ 直接执行（加 shebang）

```python
#!/usr/bin/env python3
# 文件第一行加 shebang(就是#!符号)，然后 chmod +x script.py，就能 ./script.py 运行
```

#### `uv run` 做了什么？

```
uv run python hello.py
  │
  ├─ 1. 向上遍历目录，找到项目根目录（有 pyproject.toml / .python-version / uv.lock 的地方）
  ├─ 2. 读取 .python-version（或 pyproject.toml 中的 requires-python），确认需要哪个 Python
  ├─ 3. 检查 .venv/ 存在且 Python 版本一致？
  │     ├─ 是 → 跳过
  │     └─ 否 → uv 自动创建/重建 .venv/（等价 uv venv）
  ├─ 4. 将 .venv/bin 注入到 PATH 的最前面
  │     不需要 source .venv/bin/activate，命令执行期间自动生效
  ├─ 5. 设置环境变量：
  │     VIRTUAL_ENV=.venv
  │     PATH=.venv/bin:$PATH
  │     以及其他 Python 需要的环境变量
  ├─ 6. 以子进程方式执行 hello.py
  │     uv 本身不执行，而是 fork 出一个子进程跑真正的命令
  └─ 7. 命令退出后，环境恢复原样（没有"激活"副作用）
```

**核心：uv run 不是 shell 包装器**

| | `source .venv/bin/activate` | `uv run` |
|---|---|---|
| 生效范围 | 当前 shell 会话（全局污染） | 只影响被执行的命令 |
| 退出方式 | `deactivate` | 命令结束自动恢复 |
| 能否执行非 Python 命令 | 可以 | 可以（`uv run ruff check` 等） |
| 是否需要记忆激活 | 容易忘记（常见坑） | 不需要 |

> `uv run pytest` 本质上等价于 `.venv/bin/pytest`，但省去了你先激活环境的步骤。任何安装在 `.venv/bin/` 下的命令都可以通过 `uv run <命令>` 直接调用。

**`uv run` 适用场景**

| 场景 | 命令 |
|------|------|
| 运行 Python 脚本 | `uv run python hello.py` |
| 运行模块（src 布局） | `uv run python -m app.main` |
| 运行测试 | `uv run pytest` |
| 运行 linter | `uv run ruff check .` |
| 运行类型检查 | `uv run mypy src/` |
| 构建包 | `uv build`（直接 uv build，不需要 uv run） |
| 安装新包 | `uv add httpx`（直接 uv add，不需要 uv run） |

#### 场景速查

| 场景 | 命令 |
|------|------|
| 临时测试一个脚本 | `uv run python test.py` |
| 运行 src/ 布局的项目入口 | `uv run python -m app.main` |
| 运行项目根目录的单文件 | `uv run python main.py` |
| 直接执行 .py 文件 | `./script.py`（需要 shebang + chmod +x） |
| 不用 uv，直接用系统 Python | `python3 hello.py`（不推荐，可能缺依赖） |

> **核心区别**：`python file.py` 把文件当脚本执行，`python -m package.module` 把模块当包的成员导入后执行。后者会正确设置 `sys.path`，src/ 布局下必须用 `-m`。

简言之：

> **`pyenv` 管解释器版本 → `uv` 管依赖与虚拟环境 → 按 `src/` 布局组织代码 → 用包机制解决跨目录/跨项目引用 → 用 `uv build`/`uv publish` 分发。**

