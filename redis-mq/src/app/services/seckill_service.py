"""秒杀抢购服务：一个完整业务场景，串起三种并发控制机制。

================================================================================
业务规则与机制映射
================================================================================

规则：
- 一个秒杀活动（activity_id）有固定库存；
- 每个用户限抢一次；
- 库存不能超卖；
- 封盘后不能再下单；
- 多实例部署下，「封盘结算」只能执行一次。

用到「锁 / 并发控制」的机制（对应 `lock_service.py` 已实现的能力）：

1. 下单 order  —— Lua 原子操作：一个脚本完成「封盘校验 + 限购校验 + 扣库存 + 记订单」。
   「读库存 → 判断 → 扣减 → 记订单」若分步执行，并发下会超卖或重复下单；
   放进一段 Lua 由 Redis 原子执行即可杜绝。这是秒杀的正解——**不加锁**，靠原子脚本。

2. 退款 refund —— Lua 原子操作：一个脚本完成「删幂等键 + 回补库存 + 删订单」。

3. 初始化 init —— SETNX 幂等防重：`SET NX` 只成功一次，活动已初始化则拒绝重复初始化。

4. 封盘 close —— 分布式锁：多实例并发收到「结算」请求时，用 `SET NX` 抢锁，
   只有一个实例拿到锁真正执行结算，其余拿到 None 直接返回「已被处理」。
   这是分布式锁的经典场景——**保证一段逻辑只被执行一次**，而非「原子读改写」。
   结算时写入封盘标记，下单脚本据此拒绝封盘后的新订单（返回 -3）。
"""

from __future__ import annotations

import json
import time

from app.config import settings
from app.constants.redis_key import (
    seckill_closed_key,
    seckill_order_key,
    seckill_orders_key,
    seckill_stock_key,
)
from app.services.kafka_service import KafkaProducerService
from app.services.lock_service import LockService
from app.services.redis_service import RedisService

# ---- Lua 脚本（多 key：一个脚本内原子完成多步，避免竞态）--------------------

# 下单：KEYS[1]=库存 KEYS[2]=用户幂等键 KEYS[3]=订单zset KEYS[4]=封盘标记
#       ARGV[1]=user_id ARGV[2]=下单时间戳(秒)
# 返回：>=0 剩余库存；-1 售罄；-2 该用户已抢过；-3 活动已封盘
_SECKILL_ORDER_SCRIPT = """
if redis.call('exists', KEYS[4]) == 1 then
    return -3
end
if redis.call('exists', KEYS[2]) == 1 then
    return -2
end
local stock = tonumber(redis.call('get', KEYS[1]) or '0')
if stock < 1 then
    return -1
end
redis.call('decrby', KEYS[1], 1)
redis.call('set', KEYS[2], '1')
redis.call('zadd', KEYS[3], ARGV[2], ARGV[1])
return stock - 1
"""

# 退款：KEYS[1]=幂等键 KEYS[2]=库存 KEYS[3]=订单zset；ARGV[1]=user_id
# 返回：1 退款成功；0 未下单无需退款
_SECKILL_REFUND_SCRIPT = """
if redis.call('exists', KEYS[1]) == 0 then
    return 0
end
redis.call('del', KEYS[1])
redis.call('incrby', KEYS[2], 1)
redis.call('zrem', KEYS[3], ARGV[1])
return 1
"""


class SeckillService:
    """秒杀业务服务：依赖 RedisService（命令原语）+ LockService（分布式锁）。"""

    def __init__(
        self, redis: RedisService, lock: LockService, kafka_producer: KafkaProducerService
    ) -> None:
        self._redis = redis
        self._lock = lock
        self._kafka = kafka_producer

    # ---- 初始化（SETNX 幂等防重）----

    async def init(self, activity_id: str, stock: int) -> bool:
        """初始化活动库存：`SET seckill:stock:{id} NX`，已存在则拒绝重复初始化。"""
        return await self._redis.set_nx(seckill_stock_key(activity_id), str(stock))

    # ---- 下单（Lua 原子操作）----

    async def order(self, activity_id: str, user_id: str) -> int:
        """抢购下单：返回剩余库存（>=0）；-1 售罄；-2 已抢过；-3 活动已封盘。

        下单成功后发布一条 `order_created` 事件到 Kafka（业务事件模式）——
        库存、积分、通知、风控等下游各自订阅同一主题，与下单方解耦。
        """
        result = await self._redis.eval(
            _SECKILL_ORDER_SCRIPT,
            4,
            seckill_stock_key(activity_id),
            seckill_order_key(activity_id, user_id),
            seckill_orders_key(activity_id),
            seckill_closed_key(activity_id),
            user_id,
            str(int(time.time())),
        )
        result = int(result)
        if result >= 0:  # 下单成功才发事件
            self._publish_order_created(activity_id, user_id)
        return result

    def _publish_order_created(self, activity_id: str, user_id: str) -> None:
        """发布 order_created 事件到 Kafka（非阻塞、at-least-once，下游需幂等）。

        produce 只是把消息写入本地缓冲队列、由后台线程异步发送，故在 async 方法里
        直接调用不阻塞事件循环；送达结果见 kafka_service._delivery_report。
        注：若要求「下单成功」与「事件发布」严格一致，生产应改事务性 outbox，
        本示例演示最常见的事件发布形态（fire-and-forget）。
        """
        event = json.dumps(
            {
                "event": "order_created",
                "activity_id": activity_id,
                "user_id": user_id,
                "timestamp": time.time(),
            },
            ensure_ascii=False,
        )
        self._kafka.produce(settings.kafka_order_topic, event, key=user_id)

    # ---- 退款（Lua 原子操作）----

    async def refund(self, activity_id: str, user_id: str) -> bool:
        """退款：回补库存并清除下单记录。仅已下单用户可退。"""
        result = await self._redis.eval(
            _SECKILL_REFUND_SCRIPT,
            3,
            seckill_order_key(activity_id, user_id),
            seckill_stock_key(activity_id),
            seckill_orders_key(activity_id),
            user_id,
        )
        return result == 1

    # ---- 封盘结算（分布式锁）----

    async def close(self, activity_id: str) -> dict:
        """封盘结算：分布式锁保证多实例下只有一次真正执行。

        锁名 `seckill:close:{activity_id}`；抢不到锁说明已有实例在结算，直接返回。
        """
        async with self._lock.distributed_lock(f"seckill:close:{activity_id}", ttl=10) as token:
            if token is None:
                return {"settled": False, "reason": "另一个实例正在结算"}
            order_count = await self._redis.zcard(seckill_orders_key(activity_id))
            remaining = await self._redis.get(seckill_stock_key(activity_id))
            await self._redis.set(seckill_closed_key(activity_id), "1")
            return {
                "settled": True,
                "order_count": order_count,
                "remaining": int(remaining) if remaining is not None else 0,
            }

    # ---- 查询 ----

    async def stock(self, activity_id: str) -> int | None:
        """查询剩余库存；活动未初始化返回 None。"""
        value = await self._redis.get(seckill_stock_key(activity_id))
        return int(value) if value is not None else None

    async def result(self, activity_id: str, user_id: str) -> bool:
        """查询该用户是否抢到（幂等键是否存在）。"""
        return await self._redis.get(seckill_order_key(activity_id, user_id)) is not None
