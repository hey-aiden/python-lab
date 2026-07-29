# CLAUDE.md

Codebase and user instructions for Claude Code (claude.ai/code).

## Project Overview

FastAPI 学习项目，按生产级分层架构组织：路由（api/）→ services（业务逻辑）→ schemas（数据模型），middleware 单独一层。

## Build/Run Commands

```bash
# 开发服务器（自动 reload + 释放 8000 端口）
uv run dev

# 运行测试
uv run pytest
uv run pytest -v

# 依赖管理
uv sync          # 安装/同步依赖
uv add <pkg>     # 添加运行时依赖
uv add --dev <pkg>  # 添加开发依赖
```

## Architecture

```
请求 → middleware → router → 路由处理 → service → 返回
                  ↑ 依赖注入 deps.py
```

### 各层职责

| 层 | 目录 | 规则 |
|---|------|------|
| **路由** | `api/v1/` | 路由装饰器 + 调用 service，不写业务逻辑 |
| **services** | `services/` | 纯 Python，不 `import fastapi` 任何东西 |
| **schemas** | `schemas/` | Pydantic 模型，定义 API 契约（请求/响应） |
| **middleware** | `core/middleware.py` | 全局中间件（日志、CORS 等） |
| **deps** | `api/deps.py` | FastAPI `Depends()` 依赖注入 |
| **config** | `config.py` | pydantic-settings，环境变量集中管理 |

### Import 规则

- 包内使用**显式相对导入**：`from .services.hello import get_greeting`
- 跨层使用**绝对导入**：`from app.services.hello import get_greeting`
- services 层不依赖 FastAPI，可独立测试

### 测试

- `tests/conftest.py` 提供 `client` fixture（httpx AsyncClient）
- 用 `pytest.mark.anyio` 标记异步测试
- 测试文件命名：`tests/test_<module>.py`

## Environment

- **Python**: >= 3.11
- **包管理器**: [uv](https://docs.astral.sh/uv/)
- **构建后端**: hatchling
- **平台**: macOS
