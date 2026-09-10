"""锁 / 并发控制服务：分布式锁、乐观锁、Lua 原子操作。

Redis 提供的并发控制机制不止一把「锁」，本模块先实现最常用的三类（前三条），
其余机制在文末以注释说明概念与适用场景，供后续扩展参考。

================================================================================
一、已实现
================================================================================

1. 分布式锁（互斥锁，跨进程/服务）
   - 原理：`SET key token NX EX ttl` 原子占锁；释放时用 Lua 比对 token 再 `DEL`，
     避免 A 的锁过期后被 B 抢占、A 又误删 B 的锁。
   - 场景：防止重复下单、定时任务只跑一个实例、缓存击穿时只放一个请求回源重建。
   - 要点：必须带过期时间（防宕机死锁）；必须带唯一 token（防误删）；业务过长需续期。

2. 乐观锁（CAS，低冲突场景的读-改-写）
   - 原理：不加锁，读旧值 → 提交前比对值是否仍等于旧值 → 是则写、否则失败重试。
   - 两种实现：
     a. WATCH / MULTI / EXEC 事务（Redis 原生事务机制，冲突抛 WatchError）
     b. Lua CAS（`GET` 比对再 `SET`，一段脚本内原子完成）
   - 场景：余额、库存、文档版本号等「冲突概率低、但可能并发」的字段更新；
     适合读多写少，避免分布式锁的加锁开销。

3. Lua 原子操作（多命令的原子执行）
   - 原理：`EVAL` 把多命令放进一段 Lua，Redis 单线程执行脚本期间不穿插其他命令。
   - 场景：扣库存防超卖（先判断余量再扣）、限流计数窗口、任何「先查后改」需原子化的逻辑。
   - 要点：脚本尽量短、纯函数；生产用 `SCRIPT LOAD` + `EVALSHA` 省带宽。

================================================================================
二、未实现（仅说明，后续可扩展）
================================================================================

4. Redlock（多实例分布式锁）
   - 概念：向 N 个独立 Redis 实例依次 `SET NX` 加锁，多数（N/2+1）成功才算加锁成功。
   - 场景：单实例 Redis 宕机/主从切换时，普通分布式锁可能失效，Redlock 提升可用性。
   - 未实现原因：需要 N 个独立 Redis 端点，当前 config 只有单实例；redis-py 也不内置 Redlock。

5. 信号量（限制并发数）
   - 概念：用 zset 存「时间戳 + 标识」，加锁前先清理过期项，再判断当前数量 < 上限才放行。
   - 场景：限制同一资源最多 N 个并发（如连接池、限流网关），区别于「1 个」的互斥锁。

6. SETNX 幂等防重
   - 概念：`SET key value NX` 只成功一次，天然做「只执行一次」的幂等键。
   - 场景：防重复提交（订单号、请求 ID 去重），与分布式锁同源但语义是「幂等」而非「互斥」。

7. 原子计数限流（INCR + EXPIRE）
   - 概念：`INCR` 原子自增 + 首次设置过期，得到固定窗口计数器。
   - 场景：接口限流、访问量统计、库存扣减（`incr`/`decr` 已在 RedisService 中实现）。
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from redis import asyncio as redis_asyncio

from app.constants.redis_key import lock_key, stock_key
from app.services.redis_service import RedisService

# ---- Lua 脚本（只操作传入的 KEYS/ARGV，保持纯函数、短小）--------------------
#
# 为什么释放锁要写 Lua？「读 token → 判断 → DEL」是三步，若分三次发命令，
# 判断与删除之间可能被插入其他客户端的命令，导致误删他人锁；放进一段 Lua
# 由 Redis 原子执行即可避免。

# 在脚本执行期间，其他 Redis 命令不能插入到这个脚本中间； 所以 Lua = 把多个 Redis 操作组合成一个原子操作

# 高并发情况下，不能让“检查”和“修改”之间出现竞争条件；
# Redis 的命令处理本身主要是单线程串行执行的，所以利用 Redis 单线程执行模型 + Lua 脚本的原子执行特性，避免竞态条件
# 那么redis可能会涉及[读取-操作]两个步骤；在高并发场景下，这个时间差就足以产生新的请求；

# Redis 的命令处理本身主要是单线程串行执行的，因此单条 Redis 命令本身具有原子性。
# 但是，如果一个业务操作需要拆成多个 Redis 命令，例如「读取 → 判断 → 修改」，那么这些命令之间存在时间间隔。在高并发场景下，其他请求可能在这个间隔内执行，从而产生竞态条件。
# 如果将「读取 → 判断 → 修改」这些操作放到 Lua 脚本中执行，Redis 会将整个 Lua 脚本作为一个整体执行。脚本执行期间不会执行其他客户端命令，直到脚本完整执行结束后，Redis 才会继续处理其他请求。
# 因此，可以保证「检查 → 修改」这一整套操作的原子性，避免高并发场景下产生竞态条件。

# Redis 单条命令是原子的，但多个命令组合起来不一定是原子的；Lua 脚本可以把多个 Redis 操作封装成一个原子执行单元，从而避免“检查-修改”之间的竞态条件

_RELEASE_LOCK_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""

# 续期：比对 token 一致才 EXPIRE（只能续自己持有的锁）
_RENEW_LOCK_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('expire', KEYS[1], ARGV[2])
else
    return 0
end
"""

# 乐观锁 CAS：当前值 == 期望值才写新值，否则返回 0
_CAS_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    redis.call('set', KEYS[1], ARGV[2])
    return 1
else
    return 0
end
"""

# 扣库存：判断余量足够才扣，返回剩余库存；不足返回 -1（防超卖） redis.call('get', KEYS[1]): 类似执行redis读取keys[1]参数命令
_DEDUCT_STOCK_SCRIPT = """
local stock = tonumber(redis.call('get', KEYS[1]) or '0')
local amount = tonumber(ARGV[1])
if stock >= amount then
    redis.call('decrby', KEYS[1], amount) # 数值递减
    return stock - amount
else
    return -1
end
"""


class LockService:
    """锁 / 并发控制服务（依赖 RedisService，不直接持有客户端）。

    方法返回业务结果（bool / int / token），不抛 HTTP 相关异常；底层 Redis
    异常已由 RedisService 的 `_translate_errors` 统一转成领域异常。
    """

    def __init__(self, redis: RedisService) -> None:
        self._redis = redis

    # ---- 分布式锁 ----

    async def acquire(self, lock_name: str, ttl: int) -> str | None:
        """加锁：`SET lock:{name} token NX EX ttl`。成功返回 token，失败返回 None。

        token 由 uuid4 生成，作为「这把锁是我加的」的凭证，释放/续期时回传比对。
        """
        token = uuid4().hex
        ok = await self._redis.set_nx(lock_key(lock_name), token, ttl)
        return token if ok else None

    async def release(self, lock_name: str, token: str) -> bool:
        """释放锁：Lua 比对 token 一致才 DEL。仅删除自己持有的锁，返回是否成功。"""
        result = await self._redis.eval(
            _RELEASE_LOCK_SCRIPT, 1, lock_key(lock_name), token
        )
        return result == 1

    async def renew(self, lock_name: str, token: str, ttl: int) -> bool:
        """续期：业务未跑完时延长过期时间。比对 token 一致才生效，返回是否成功。"""
        result = await self._redis.eval(
            _RENEW_LOCK_SCRIPT, 1, lock_key(lock_name), token, str(ttl)
        )
        return result == 1

    @asynccontextmanager
    async def distributed_lock(self, lock_name: str, ttl: int):
        """分布式锁的异步上下文管理器：`async with` 内为临界区，退出自动释放。

        yield 的是 token（未抢到时为 None），调用方据此决定是否进入临界区：

            async with svc.distributed_lock("order", 10) as token:
                if token is None:
                    return "busy"
                ...

        适用场景：单进程内的后台任务 / 定时任务互斥（HTTP 请求分属不同进程，
        应改用 acquire / release 接口，在两次请求间手动传递 token）。
        """
        token = await self.acquire(lock_name, ttl)
        try:
            yield token
        finally:
            if token is not None:
                await self.release(lock_name, token)

    # ---- 乐观锁 ----

    async def optimistic_update(self, key: str, expected: str, new_value: str) -> bool:
        """乐观锁（WATCH / MULTI / EXEC 事务）：仅当 key 当前值 == expected 才写入。

        流程：WATCH 监测 key → GET 读旧值 → 不符则放弃；相符则 MULTI..EXEC 提交。
        提交瞬间若 key 被他人改动，EXEC 抛 WatchError（即乐观锁冲突），返回 False。
        """
        pipe = self._redis.pipeline()
        try:
            await pipe.watch(key)
            current = await pipe.get(key)
            if current != expected:
                await pipe.reset()
                return False
            pipe.multi()
            pipe.set(key, new_value)
            await pipe.execute()
            return True
        except redis_asyncio.WatchError:
            # key 在 watch 后被他人修改 → 事务冲突，交由调用方重试或放弃
            return False

    async def compare_and_set(self, key: str, expected: str, new_value: str) -> bool:
        """乐观锁（Lua CAS）：一段 Lua 内原子完成「比对 + 写」，等价但更简洁。

        相比 WATCH 事务：不依赖连接上的 WATCH 状态，更不容易用错；推荐优先使用。
        """
        result = await self._redis.eval(_CAS_SCRIPT, 1, key, expected, new_value)
        return result == 1

    # ---- Lua 原子操作 ----

    async def deduct_stock(self, product_id: int | str, amount: int) -> int:
        """扣库存（Lua 原子操作）：判断余量足够才扣，返回剩余库存，-1 表示不足。

        「读余量 → 判断 → 扣减」若分步执行会超卖（并发同时读到 1、都扣到 0）；
        放进 Lua 原子执行即可杜绝。

        通过 eval 执行 Lua 脚本时，script 后面的参数， 对应的就是 KEYS 的参数，比如keys[0]=1; keys[1]=stock_key(product_id)
        """
        result = await self._redis.eval(
            _DEDUCT_STOCK_SCRIPT, 1, stock_key(product_id), str(amount)
        )
        return int(result)
