"""秒杀抢购路由 — 一个串起「Lua 原子 / SETNX 幂等 / 分布式锁」的业务场景。

各端点用到的机制见 docstring；完整机制映射见 `app/services/seckill_service.py`。
"""

from typing import Annotated

import anyio
from fastapi import APIRouter, Depends

from app.config import settings
from app.deps import get_kafka_consumer, get_seckill
from app.schemas.seckill import (
    SeckillCloseRequest,
    SeckillInitRequest,
    SeckillOrderRequest,
    SeckillRefundRequest,
)
from app.services.kafka_service import KafkaConsumerService
from app.services.seckill_service import SeckillService

router = APIRouter(prefix="/seckill", tags=["seckill"])


@router.post("/init")
async def init_seckill(
    body: SeckillInitRequest, seckill: Annotated[SeckillService, Depends(get_seckill)]
):
    """初始化秒杀活动（SETNX 幂等防重）：已初始化则拒绝，防重复覆盖库存。"""
    initialized = await seckill.init(body.activity_id, body.stock)
    return {
        "code": 0,
        "initialized": initialized,
        "message": None if initialized else "活动已初始化",
    }


@router.post("/order")
async def order(
    body: SeckillOrderRequest, seckill: Annotated[SeckillService, Depends(get_seckill)]
):
    """抢购下单（Lua 原子操作）：限购校验 + 扣库存 + 记订单一步原子完成，防超卖/防重复。"""
    result = await seckill.order(body.activity_id, body.user_id)
    if result == -1:
        return {"code": 0, "success": False, "message": "已抢光"}
    if result == -2:
        return {"code": 0, "success": False, "message": "已抢过"}
    if result == -3:
        return {"code": 0, "success": False, "message": "活动已结束"}
    return {"code": 0, "success": True, "remaining": result}


@router.post("/refund")
async def refund(
    body: SeckillRefundRequest, seckill: Annotated[SeckillService, Depends(get_seckill)]
):
    """退款 / 取消订单（Lua 原子操作）：删幂等键 + 回补库存 + 删订单一步完成。"""
    refunded = await seckill.refund(body.activity_id, body.user_id)
    return {"code": 0, "refunded": refunded}


@router.post("/close")
async def close(
    body: SeckillCloseRequest, seckill: Annotated[SeckillService, Depends(get_seckill)]
):
    """封盘结算（分布式锁）：多实例并发调用时只有一个真正执行，其余返回「已被处理」。"""
    return {"code": 0, **await seckill.close(body.activity_id)}


@router.get("/stock")
async def get_stock(
    activity_id: str, seckill: Annotated[SeckillService, Depends(get_seckill)]
):
    """查询剩余库存。"""
    remaining = await seckill.stock(activity_id)
    return {"code": 0, "remaining": remaining}


@router.get("/result")
async def get_result(
    activity_id: str,
    user_id: str,
    seckill: Annotated[SeckillService, Depends(get_seckill)],
):
    """查询某用户是否抢到。"""
    grabbed = await seckill.result(activity_id, user_id)
    return {"code": 0, "grabbed": grabbed}


@router.get("/events")
async def events(
    consumer: Annotated[KafkaConsumerService, Depends(get_kafka_consumer)],
    n: int = 10,
):
    """模拟下游服务消费 order_created 事件（演示业务事件的解耦）。

    下单方（SeckillService.order）发布事件后，这里作为「积分/通知/风控」等下游，
    订阅同一主题拉取最近的事件。poll 阻塞，用 anyio.to_thread 包装避免阻塞事件循环。
    """
    consumer.subscribe([settings.kafka_order_topic])
    messages = []
    for _ in range(n):
        msg = await anyio.to_thread.run_sync(consumer.consume, 1.0)
        if msg is None:
            break
        messages.append(msg)
    return {"code": 0, "count": len(messages), "data": messages}
