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
└── utils.py             # 小工具模块
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
│       └── cli.py
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

