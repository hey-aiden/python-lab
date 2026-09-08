"""Kafka 相关路由 — 只负责路由分发与参数解析，业务逻辑下沉到 services 层。

分层约定（对齐 web-fastapi）：
- 本层：解析参数 → 调用 KafkaService → 封装响应
- services 层：纯 Kafka 操作逻辑，不依赖 FastAPI
"""

from fastapi import APIRouter, Depends

from app.deps import get_kafka_consumer, get_kafka_producer
from app.services.kafka_service import KafkaConsumerService, KafkaProducerService

router = APIRouter(prefix="/kafka", tags=["kafka"])


@router.post("/produce")
async def produce(
    topic: str,
    message: str,
    producer: KafkaProducerService = Depends(get_kafka_producer),
):
    """生产一条消息。"""
    # TODO: confluent-kafka 是同步客户端，实现时用 anyio.to_thread 包装，避免阻塞事件循环
    return producer.produce(topic, message)


@router.get("/consume")
async def consume(consumer: KafkaConsumerService = Depends(get_kafka_consumer)):
    """消费一条消息。"""
    # TODO: confluent-kafka 是同步客户端，实现时用 anyio.to_thread 包装，避免阻塞事件循环
    return consumer.consume()
