# web-fastapi

FastAPI 学习项目，按生产级目录结构组织：router / service / middleware / schema 分层。

## 技术栈

- **Python** >= 3.11
- **FastAPI** — Web 框架
- **Uvicorn** — ASGI 服务器
- **pydantic-settings** — 配置管理
- **pytest + httpx** — 测试

## 项目结构

```
src/app/
├── main.py              # FastAPI app 创建 + dev() 入口
├── config.py            # pydantic-settings 配置
├── api/
│   ├── deps.py          # 依赖注入
│   └── v1/
│       ├── router.py    # v1 路由聚合
│       └── hello.py     # GET /api/v1/
├── core/
│   └── middleware.py    # 全局中间件
├── schemas/             # Pydantic 请求/响应模型
└── services/            # 业务逻辑（纯 Python，不依赖 FastAPI）
```

## 常用命令

```bash
# 开发服务器（自动 reload + 释放 8000 端口）
uv run dev

# 运行测试
uv run pytest

# 依赖管理
uv sync          # 安装/同步依赖
uv add <pkg>     # 添加新依赖
```
