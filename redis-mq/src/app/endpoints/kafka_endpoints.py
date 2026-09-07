"""Kafka 相关路由 — 只负责路由分发与参数解析，业务逻辑下沉到 services 层。

分层约定（对齐 web-fastapi）：
- 本层：解析参数 → 调用 KafkaService → 封装响应
- services 层：纯 Kafka 操作逻辑，不依赖 FastAPI
- 注意：confluent-kafka 是同步客户端，正式实现时用 anyio.to_thread 包装，避免阻塞事件循环
"""

from fastapi import APIRouter

from app.services.kafka_service import consumer_service, producer_service

router = APIRouter(prefix="/kafka", tags=["kafka"])


@router.post("/produce")
async def produce(topic: str, message: str):
    """生产一条消息。"""
    return producer_service.produce(topic, message)


@router.get("/consume")
async def consume():
    """消费一条消息。"""
    return consumer_service.consume()
