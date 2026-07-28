# 项目常见目录结构

> 📖 本章介绍两种项目布局（平铺 vs src 布局）及关键文件说明。

### 3.1 小型脚本项目

```
my-script/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .venv/
├── README.md
├── main.py              # 入口脚本
├── utils.py             # 小工具模块
└── __pycache__/         # Python 自动生成的字节码缓存
```

### 3.2 中大型库/应用项目（推荐 src 布局）

```
my-project/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .venv/
├── README.md
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── core.py
│       ├── api.py
│       ├── cli.py
│       └── __pycache__/     # 自动生成，不要提交
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_api.py
└── scripts/
    └── setup_dev.sh
```

> 推荐 `src/` 布局：`import my_project` 时会从 `src/` 下找包，不容易和当前目录下的文件混淆。

### 3.3 关键文件说明

| 文件/目录 | 作用 |
|-----------|------|
| `pyproject.toml` | 项目配置：包名、版本、依赖、Python 版本要求、入口脚本 |
| `uv.lock` | 精确锁定每个依赖的版本，保证可复现 |
| `.python-version` | 当前目录使用的 Python 版本 |
| `.venv/` | 虚拟环境，不要提交到 Git |
| `src/<package>/` | 项目源码包 |
| `tests/` | 测试代码 |
| `__pycache__/` | Python 自动生成的字节码缓存，不要提交到 Git |

### 3.4 `__pycache__/`：字节码缓存

每次 `import` 一个 `.py` 文件时，Python 会：

```
import utils.py
  │
  ├─ 1. 把 utils.py 编译成字节码（.pyc 文件）
  ├─ 2. 把编译结果缓存到 __pycache__/utils.cpython-312.pyc
  └─ 3. 下次 import 时直接读 .pyc，跳过编译 → 加载更快
```

**你需要知道的三件事：**

| 问题 | 答案 |
|------|------|
| 谁创建的？ | Python 自动创建，不需要手动操作 |
| 要提交到 Git 吗？ | ❌ 不要，`.gitignore` 中加上 `__pycache__/` |
| 可以删除吗？ | ✅ 可以，下次 import 时自动重建（不影响运行） |
| 删除后会影响性能吗？ | 下次 import 稍慢一点（重新编译），之后又恢复 |
| 不同 Python 版本兼容吗？ | 不兼容，文件名中的 `cpython-312` 标记了 Python 版本 |

> `uv init` 生成的 `.gitignore` 已经包含了 `__pycache__/`。只要不去掉，Git 就不会追踪这些文件。

