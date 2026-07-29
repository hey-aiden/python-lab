# 如何阅读一个 Python 项目

> 面对一个新的 Python 代码仓库，从哪里开始看？本章总结一套快速上手的阅读路径。

## 6.1 阅读路线图

按这个顺序看，5 分钟就能理解项目骨架：

```
pyproject.toml  →  找入口点  →  追踪 import 链  →  看测试  →  深入细节
   (第 1 步)        (第 2 步)      (第 3 步)        (第 4 步)    (第 5 步)
```

### 第 1 步：读 `pyproject.toml` — 了解基本信息

这是 Python 项目的"身份证"，和 `package.json` 一样是第一个该看的文件。

```toml
[project]
name = "web-fastapi"              # 项目名
requires-python = ">=3.11"        # Python 版本要求
dependencies = [                   # 运行时依赖
    "fastapi>=0.140.13",
    "uvicorn>=0.51.0",
]

[project.scripts]
dev = "app.main:dev"              # ← 入口点！从这里开始看
```

关注三样东西：
- `dependencies` — 用了哪些第三方库，决定了项目的技术栈
- `[project.scripts]` — 定义了哪些可执行命令，每个都是入口点
- `requires-python` — 需要什么 Python 版本

> Node.js 对照：`pyproject.toml` ≈ `package.json`，`[project.scripts]` ≈ `"scripts"`（但有本质区别——scripts 必须是 `模块:函数` 引用，不能是任意 shell 命令）

### 第 2 步：从入口点开始追踪

`[project.scripts]` 里的 `app.main:dev` 意思是：**模块 `app.main` 里的 `dev` 函数**。

```bash
app.main:dev
  │    │
  │    └── dev() 函数
  └── src/app/main.py 文件
```

拿到入口文件后，打开 `src/app/main.py`：

```python
from fastapi import FastAPI
from app.api.v1.router import api_router    # ← 继续追踪
from app.core.middleware import setup_middleware

app = FastAPI(title="web-fastapi", version="0.1.0")
setup_middleware(app)
app.include_router(api_router, prefix="/api/v1")
```

顺着每个 `import` 往下读，就能画出项目的组件依赖图。

### 第 3 步：看目录结构 — 理解分层

```
src/app/
├── main.py              ← 入口：app 创建 + 组装
├── api/
│   └── v1/
│       ├── router.py    ← 路由聚合
│       └── endpoints/   ← API 端点（每个文件 = 一组接口）
├── core/
│   └── middleware.py    ← 中间件
├── schemas/             ← 请求/响应的数据模型
└── services/            ← 业务逻辑
```

常见模式速查：

| 目录名 | 里面放什么 |
|--------|-----------|
| `api/` `routes/` `endpoints/` | HTTP 路由定义 |
| `models/` `schemas/` | 数据模型（Pydantic / SQLAlchemy） |
| `services/` | 业务逻辑，不依赖 Web 框架 |
| `core/` `config/` | 配置、中间件、全局设置 |
| `utils/` `helpers/` | 工具函数 |
| `tests/` | 测试代码 |

### 第 4 步：读测试 — 最快理解用法的文档

`tests/` 目录是最好的"使用说明书"。每个测试文件就是一段完整的使用示例：

```python
# tests/test_hello.py
async def test_hello(client):
    response = await client.get("/api/v1/")   # 请求什么路径
    assert response.status_code == 200         # 期望什么状态
    assert response.json() == {"message": "Hello FastAPI"}  # 返回什么
```

3 行代码就能看出：
- 接口路径是 `/api/v1/`
- 返回 200 和 JSON
- 响应格式是 `{"message": "..."}`

### 第 5 步：用 `dir()` + `help()` 探索模块

进入 Python 交互模式，直接探索不熟悉的模块：

```python
>>> import some_module
>>> dir(some_module)              # 导出什么了？
>>> help(some_module.SomeClass)   # 这个类是干嘛的？
>>> some_module.SomeClass?        # Jupyter/IPython 中用 ? 更快
```

> 详见 [第 11 章：标准库速览 — `dir()` 与 `help()`](../part2-language/11-standard-library.md)

## 6.2 真实案例：web-fastapi 阅读演练

以本仓库的 `web-fastapi` 为例，完整走一遍：

```
1. pyproject.toml
   → 依赖: fastapi, uvicorn, pydantic-settings
   → 入口: dev = "app.main:dev"
   → 结论: FastAPI Web 项目，uv run dev 启动

2. src/app/main.py
   → app = FastAPI()
   → 注册了中间件 setup_middleware(app)
   → 挂载了 api_router 到 /api/v1
   → dev() 启动 uvicorn

3. src/app/api/v1/router.py
   → 聚合了 hello 端点
   → 结论: 目前只有一个模块

4. src/app/api/v1/endpoints/hello.py
   → GET /   返回 {"message": "Hello FastAPI"}
   → 调用了 services.hello.get_greeting()

5. src/app/core/middleware.py
   → 请求耗时日志中间件

6. tests/test_hello.py
   → 确认接口行为和预期一致
```

5 分钟，6 个文件，项目骨架一目了然。

## 6.3 工具辅助

| 工具 | 用法 | 效果 |
|------|------|------|
| `tree src/` | 终端 | 一眼看目录结构 |
| `rg "def " src/` | ripgrep | 列出所有函数定义 |
| `rg "^from\|^import" src/` | ripgrep | 列出所有 import 关系 |
| `uv run pytest --tb=short` | 测试 | 看测试覆盖了什么 |
| `python -c "import app; dir(app)"` | 交互 | 探索模块导出 |

## 6.4 不同项目类型的入手重点

| 项目类型 | 第一眼看 | 第二眼看 |
|----------|---------|---------|
| Web API（FastAPI/Flask） | `[project.scripts]` 入口 + router 文件 | middleware + schemas |
| CLI 工具（click/typer） | `[project.scripts]` 入口 → argparse 或 click 命令 | 参数定义 |
| 库/包（library） | `__init__.py` 里 `__all__` 导出了什么 | 公开 API 的函数签名 |
| 数据处理脚本 | 主脚本 `main.py` 或顶层 `.py` 文件 | `dependencies` 里用了什么库 |
| 测试项目 | `tests/` + `conftest.py` 的 fixtures | 测试覆盖了哪些边界情况 |

---

> **总结**：阅读路径 = pyproject.toml → 入口点 → import 链 → 测试 → dir()/help() 探索。不认识的对象用 `dir()` 看有什么方法，再用 `help()` 看怎么用。
