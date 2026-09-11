"""日志埋点收集路由 — 演示 Kafka「日志收集 / 用户埋点」场景。

场景：
- 客户端上报用户行为事件（页面浏览、点击等），统一写入 Kafka 主题；
- 下游（离线分析 / 实时大屏 / 审计）各自订阅同一主题独立消费，与上报方解耦。
- 体现 Kafka 特性：异步高吞吐写入、消息持久化可回放、按 key 分区有序。

分层约定（对齐 web-fastapi）：
- 本层：解析参数 → 序列化 → 调用 KafkaService → 封装响应
- services 层：纯 Kafka 操作逻辑，不依赖 FastAPI
"""

import json
import time
from typing import Annotated

import anyio
from fastapi import APIRouter, Depends

from app.config import settings
from app.deps import get_kafka_consumer, get_kafka_producer
from app.schemas.log import TrackEventRequest
from app.services.kafka_service import KafkaConsumerService, KafkaProducerService

router = APIRouter(prefix="/log", tags=["log"])


@router.post("/track")
async def track(
    body: TrackEventRequest,
    producer: Annotated[KafkaProducerService, Depends(get_kafka_producer)],
):
    """上报一条埋点事件：序列化为 JSON 写入 Kafka，key=user_id 保证同用户有序。

    produce 是非阻塞异步投递，这里直接调用；消息是否真正送达由 service 层
    投递回调确认（见 kafka_service._delivery_report 日志）。
    """
    event = {
        "event": body.event,
        "user_id": body.user_id,
        "payload": body.payload,
        # 缺省补服务端时间；客户端可携带（如离线补报时的真实发生时间）
        "timestamp": body.timestamp if body.timestamp is not None else time.time(),
    }
    producer.produce(
        settings.kafka_topic,
        json.dumps(event, ensure_ascii=False),
        key=body.user_id,
    )
    return {"code": 0, "status": "accepted", "event": body.event}


@router.get("/recent")
async def recent(
    consumer: Annotated[KafkaConsumerService, Depends(get_kafka_consumer)],
    n: int = 10,
):
    """拉取最近 n 条埋点日志（演示消费侧）。

    poll 是阻塞调用，用 anyio.to_thread 丢到线程池，避免阻塞事件循环；
    无新消息时 consume 返回 None，提前结束拉取。
    """
    consumer.subscribe([settings.kafka_topic])
    messages = []
    for _ in range(n):
        msg = await anyio.to_thread.run_sync(consumer.consume, 1.0)
        if msg is None:
            break
        messages.append(msg)
    return {"code": 0, "count": len(messages), "data": messages}
