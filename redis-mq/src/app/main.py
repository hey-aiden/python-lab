"""FastAPI 应用入口。"""

from fastapi import FastAPI

from app.config import settings
from app.endpoints import kafka_endpoints, redis_endpoints

app = FastAPI(title="redis-mq", description="学习 Redis 与 Kafka 消息队列")

app.include_router(redis_endpoints.router)
app.include_router(kafka_endpoints.router)


@app.get("/health")
async def health() -> dict:
    """健康检查：确认服务可启动、配置已加载。"""
    return {
        "status": "ok",
        "app": app.title,
        "redis_host": settings.redis_host,
        "kafka_bootstrap_servers": settings.kafka_bootstrap_servers,
    }


def run() -> None:
    """开发服务器入口：`uv run dev`。"""
    import uvicorn  # uvicorn 是一个 Python 的 ASGI Web 服务器

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
