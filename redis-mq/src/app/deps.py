"""依赖注入 — 从 app.state 取出共享的服务实例（由 lifespan 创建）。"""

from fastapi import Request

from app.services.kafka_service import (
    KafkaAdminService,
    KafkaConsumerService,
    KafkaProducerService,
)
from app.services.redis_service import RedisService


def get_redis(request: Request) -> RedisService:
    """返回 RedisService 实例（app.state.redis）。"""
    return request.app.state.redis


def get_kafka_producer(request: Request) -> KafkaProducerService:
    """返回 KafkaProducerService 实例（app.state.kafka_producer）。"""
    return request.app.state.kafka_producer


def get_kafka_consumer(request: Request) -> KafkaConsumerService:
    """返回 KafkaConsumerService 实例（app.state.kafka_consumer）。"""
    return request.app.state.kafka_consumer


def get_kafka_admin(request: Request) -> KafkaAdminService:
    """返回 KafkaAdminService 实例（app.state.kafka_admin）。"""
    return request.app.state.kafka_admin
