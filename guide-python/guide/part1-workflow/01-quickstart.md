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
# 文件第一行加 shebang，然后 chmod +x script.py，就能 ./script.py 运行
```

#### `uv run` 做了什么？

```
uv run python hello.py
  │
  ├─ 1. 找到项目根目录（有 pyproject.toml 的地方）
  ├─ 2. 确认 .venv/ 存在，没有则自动创建
  ├─ 3. 用 .venv/bin/python3 执行 hello.py
  └─ 结果：用的永远是项目自己的 Python + 依赖，不污染系统环境
```

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

