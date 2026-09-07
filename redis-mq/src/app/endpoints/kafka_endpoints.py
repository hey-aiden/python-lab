"""Kafka 相关路由（标记桩）。

TODO: 后续暴露 produce / consume 端点，逻辑在 services/kafka_service.py。
以下为代表性示例。
"""

from fastapi import APIRouter

router = APIRouter(prefix="/kafka", tags=["kafka"])


@router.post("/produce")
async def produce(topic: str, message: str):
    """生产一条消息。TODO: 实现 — 调用 KafkaProducerService.produce"""
    raise NotImplementedError


@router.get("/consume")
async def consume():
    """消费一条消息。TODO: 实现 — 调用 KafkaConsumerService.consume"""
    raise NotImplementedError
