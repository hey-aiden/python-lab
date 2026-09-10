"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.endpoints import article_poem, kafka_endpoints, redis_endpoints, score_rank, session
from app.exception_handlers import register_exception_handlers

# from app.services.kafka_service import (
#     KafkaAdminService,
#     KafkaConsumerService,
#     KafkaProducerService,
# )
from app.services.redis_service import RedisService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时创建服务，关闭时释放连接。

    在 lifespan（而非 import 时）创建服务的原因：
    - fork 安全：uvicorn 多 worker 各自在子进程内创建，避免共享 socket
    - 事件循环正确：async 客户端绑定当前运行的 loop
    - 生命周期清晰：关闭时统一释放连接
    """
    app.state.redis = RedisService()
    # app.state.kafka_producer = KafkaProducerService()
    # app.state.kafka_consumer = KafkaConsumerService()
    # app.state.kafka_admin = KafkaAdminService()
    yield
    await app.state.redis.aclose()
    # app.state.kafka_producer.flush()  # 等待未投递消息送达
    # app.state.kafka_consumer.close()


app = FastAPI(
    title="redis-mq",
    description="学习 Redis 与 Kafka 消息队列",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(redis_endpoints.router)
app.include_router(kafka_endpoints.router)
app.include_router(article_poem.router)
app.include_router(session.router)
app.include_router(score_rank.router)


@app.get("/")
async def index() -> dict:
    return {"status": "ok", "app": app.title}


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
