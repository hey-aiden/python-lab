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

#### `uv init` 做了什么？

```
uv init my-project
  │
  ├─ 1. 创建目录 my-project/
  ├─ 2. 检测当前系统的 Python 解释器
  │     which python3 → 找到系统或 pyenv 管理的 Python
  │     记录其版本（如 3.12.4）
  ├─ 3. 生成 pyproject.toml
  │     ├─ name = "my-project"（目录名）
  │     ├─ version = "0.1.0"
  │     ├─ requires-python = ">=3.11"（当前 Python 的 minor 版本）
  │     ├─ dependencies = []（空列表）
  │     └─ [build-system] 使用 hatchling
  ├─ 4. 生成 README.md（模板内容，包含项目名和描述）
  ├─ 5. 生成 hello.py（示例入口文件）
  ├─ 6. 生成 .python-version（记录当前 Python 版本）
  ├─ 7. 生成 .gitignore（如果不存在）
  └─ 8. 不生成 .venv/ 和 uv.lock — 这些在第一次 uv sync / uv add 时才创建
```

**uv init 干了什么、没干什么：**

| 操作 | 做了？ | 说明 |
|------|:------:|------|
| 创建 `pyproject.toml` | ✅ | 项目身份证 |
| 创建 `README.md` | ✅ | 模板内容 |
| 创建 `hello.py` | ✅ | 示例入口 |
| 创建 `.python-version` | ✅ | 锁定 Python 版本 |
| 创建 `.gitignore` | ✅ | 忽略 `.venv/`、`__pycache__/` 等 |
| 创建 `.venv/` | ❌ | 不创建，等到 `uv sync` 或 `uv add` 时才创建 |
| 创建 `uv.lock` | ❌ | 不创建，`uv lock` 或 `uv sync` 时才生成 |
| `git init` | ❌ | 不初始化 Git 仓库 |
| 安装依赖 | ❌ | 不安装任何包 |

> **核心理念**：`uv init` 只做**脚手架生成**，不做**环境搭建**。`.venv/` 和 `uv.lock` 在第一次 `uv sync` 或 `uv add` 时才懒加载创建。

**关键参数：**

| 参数 | 作用 |
|------|------|
| `uv init my-project` | 创建新目录 + 脚手架 |
| `uv init` | 在当前目录生成脚手架 |
| `uv init --name "my-app" .` | 指定项目名（不同目录名） |
| `uv init --lib` | 创建库项目（含 `src/` 布局） |
| `uv init --app` | 创建应用项目（默认） |
| `uv init --force` | 覆盖已有 `pyproject.toml`（危险） |

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

发布前需要三样东西：**正确的 `pyproject.toml`**、**PyPI 账号**、**API Token**。

**① `pyproject.toml` 必填字段：**

```toml
[project]
name = "my-package"              # PyPI 上唯一的名字，先到先得
version = "0.1.0"                # 语义版本，每次发布必须递增
description = "一句话描述"         # PyPI 搜索页展示
readme = "README.md"             # 项目主页渲染 README
requires-python = ">=3.11"       # 支持的 Python 版本范围
license = { text = "MIT" }       # 许可证（PyPI 要求）
authors = [                      # 作者/维护者
    { name = "Your Name", email = "you@example.com" }
]
# 可选但推荐：
classifiers = [                  # PyPI 分类标签，方便用户搜索
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
urls = { Homepage = "https://github.com/you/my-package" }
```

**② 获取 API Token：**

```
1. 注册 https://pypi.org （或测试环境 https://test.pypi.org）
2. Account Settings → API tokens → Add API token
3. 复制 token（只显示一次！）
```

**③ 构建 + 发布：**

```bash
# 构建包（生成 dist/ 目录，含 .tar.gz 和 .whl）
uv build

# 发布到 PyPI（自动从环境变量读取 token）
uv publish --token YOUR_TOKEN_HERE
# 或设置环境变量（推荐，避免 token 留在 shell 历史中）：
export UV_PUBLISH_TOKEN=pypi-xxxxxxxx
uv publish

# 先发布到 TestPyPI 验证：
uv publish --publish-url https://test.pypi.org/legacy/ \
           --token YOUR_TEST_TOKEN
# 然后安装验证：
uv pip install -i https://test.pypi.org/simple/ my-package
```

**④ 完整发布流程：**

```bash
# 1. 更新版本号
#    pyproject.toml: version = "0.1.0" → "0.1.1"

# 2. 构建
uv build                        # → dist/my_package-0.1.1.tar.gz
                                # → dist/my_package-0.1.1-py3-none-any.whl

# 3. 发布（token 从环境变量读取）
export UV_PUBLISH_TOKEN=pypi-xxxxxxxx
uv publish

# 4. 验证
uv pip install my-package       # 从 PyPI 安装
python -c "import my_package"   # 确认能导入
```

**常见坑点：**

| 坑 | 现象 | 解决 |
|----|------|------|
| name 已被占用 | `403 The name 'xxx' is already registered` | 换一个包名 |
| 版本号不递增 | `403 File already exists` | 递增 version 字段 |
| 缺少必填字段 | `400 Missing required field` | 补上 license、authors |
| token 权限不足 | `403 Invalid or non-existent authentication` | 确认 token 没有过期，且勾选了 "Upload packages" |
| 忘记更新 README | PyPI 页面还是旧内容 | 发布前确认 `readme = "README.md"` 存在 |

> **最佳实践**：不要直接发布到 PyPI——先发布到 [TestPyPI](https://test.pypi.org) 验证一切正常，再发布到正式 PyPI。Token 用环境变量而非命令行参数，避免泄漏到 shell 历史。

```toml
# pyproject.toml 中注册 CLI 入口（可选）
[project.scripts]
my-cli = "my_package.cli:main"   # pip install 后直接敲 my-cli 就能用
```
