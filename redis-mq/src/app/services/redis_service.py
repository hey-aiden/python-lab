"""Redis 服务层：完整数据结构的操作标记（尚未实现）。

统一约定：
- 使用 `redis.asyncio` 异步客户端（FastAPI 场景下的推荐方式），方法均为 `async`。
- 每个方法对应一条 Redis 命令，签名尽量对齐 redis-py。
- 所有方法当前为桩，`raise NotImplementedError`，后续逐个实现。

实现顺序建议：先 string/hash，再 list/set/zset，最后键管理 / 管道 / 发布订阅。
"""


class RedisService:
    """Redis 操作集合（按数据结构分组）。

    TODO: 实现 — 在 `__init__` 中基于 `app.config.settings` 创建
    `redis.asyncio.Redis` 客户端（可直接用 settings.redis_url）。
    """

    # ---- string 字符串 ----

    async def set(self, key: str, value: str) -> bool:
        """SET：写入字符串键值。TODO: 实现"""
        raise NotImplementedError

    async def get(self, key: str) -> str | None:
        """GET：读取字符串键值。TODO: 实现"""
        raise NotImplementedError

    async def setex(self, key: str, ttl: int, value: str) -> bool:
        """SETEX：写入键值并设置过期秒数。TODO: 实现"""
        raise NotImplementedError

    async def incr(self, key: str) -> int:
        """INCR：键值自增 1（常用于计数）。TODO: 实现"""
        raise NotImplementedError

    async def decr(self, key: str) -> int:
        """DECR：键值自减 1。TODO: 实现"""
        raise NotImplementedError

    async def mset(self, mapping: dict[str, str]) -> bool:
        """MSET：批量写入多个键值。TODO: 实现"""
        raise NotImplementedError

    async def mget(self, keys: list[str]) -> list[str | None]:
        """MGET：批量读取多个键。TODO: 实现"""
        raise NotImplementedError

    async def append(self, key: str, value: str) -> int:
        """APPEND：向字符串末尾追加内容。TODO: 实现"""
        raise NotImplementedError

    # ---- hash 哈希 ----

    async def hset(self, name: str, mapping: dict[str, str]) -> int:
        """HSET：写入哈希字段（对象属性）。TODO: 实现"""
        raise NotImplementedError

    async def hget(self, name: str, field: str) -> str | None:
        """HGET：读取单个字段。TODO: 实现"""
        raise NotImplementedError

    async def hgetall(self, name: str) -> dict[str, str]:
        """HGETALL：读取全部字段。TODO: 实现"""
        raise NotImplementedError

    async def hdel(self, name: str, *fields: str) -> int:
        """HDEL：删除字段。TODO: 实现"""
        raise NotImplementedError

    async def hincrby(self, name: str, field: str, amount: int) -> int:
        """HINCRBY：字段值自增指定数量。TODO: 实现"""
        raise NotImplementedError

    async def hexists(self, name: str, field: str) -> bool:
        """HEXISTS：判断字段是否存在。TODO: 实现"""
        raise NotImplementedError

    async def hkeys(self, name: str) -> list[str]:
        """HKEYS：列出所有字段名。TODO: 实现"""
        raise NotImplementedError

    async def hvals(self, name: str) -> list[str]:
        """HVALS：列出所有字段值。TODO: 实现"""
        raise NotImplementedError

    # ---- list 列表 ----

    async def lpush(self, key: str, *values: str) -> int:
        """LPUSH：左侧插入（头部入队）。TODO: 实现"""
        raise NotImplementedError

    async def rpush(self, key: str, *values: str) -> int:
        """RPUSH：右侧插入（尾部入队）。TODO: 实现"""
        raise NotImplementedError

    async def lrange(self, key: str, start: int, stop: int) -> list[str]:
        """LRANGE：按索引区间读取。TODO: 实现"""
        raise NotImplementedError

    async def lpop(self, key: str) -> str | None:
        """LPOP：左侧弹出。TODO: 实现"""
        raise NotImplementedError

    async def rpop(self, key: str) -> str | None:
        """RPOP：右侧弹出。TODO: 实现"""
        raise NotImplementedError

    async def llen(self, key: str) -> int:
        """LLEN：列表长度。TODO: 实现"""
        raise NotImplementedError

    async def ltrim(self, key: str, start: int, stop: int) -> bool:
        """LTRIM：裁剪列表到指定区间。TODO: 实现"""
        raise NotImplementedError

    # ---- set 集合 ----

    async def sadd(self, key: str, *members: str) -> int:
        """SADD：添加成员（去重）。TODO: 实现"""
        raise NotImplementedError

    async def smembers(self, key: str) -> set[str]:
        """SMEMBERS：读取全部成员。TODO: 实现"""
        raise NotImplementedError

    async def sismember(self, key: str, member: str) -> bool:
        """SISMEMBER：判断成员是否存在。TODO: 实现"""
        raise NotImplementedError

    async def srem(self, key: str, *members: str) -> int:
        """SREM：删除成员。TODO: 实现"""
        raise NotImplementedError

    async def scard(self, key: str) -> int:
        """SCARD：集合大小。TODO: 实现"""
        raise NotImplementedError

    async def sinter(self, *keys: str) -> set[str]:
        """SINTER：多集合交集。TODO: 实现"""
        raise NotImplementedError

    async def sunion(self, *keys: str) -> set[str]:
        """SUNION：多集合并集。TODO: 实现"""
        raise NotImplementedError

    async def sdiff(self, *keys: str) -> set[str]:
        """SDIFF：多集合差集。TODO: 实现"""
        raise NotImplementedError

    # ---- zset 有序集合 ----

    async def zadd(self, key: str, mapping: dict[str, float]) -> int:
        """ZADD：添加成员及其分数。TODO: 实现"""
        raise NotImplementedError

    async def zrange(self, key: str, start: int, stop: int) -> list[str]:
        """ZRANGE：按索引区间读取（升序）。TODO: 实现"""
        raise NotImplementedError

    async def zrangebyscore(self, key: str, min_: float, max_: float) -> list[str]:
        """ZRANGEBYSCORE：按分数区间读取。TODO: 实现"""
        raise NotImplementedError

    async def zrank(self, key: str, member: str) -> int | None:
        """ZRANK：成员排名（升序，从 0 开始）。TODO: 实现"""
        raise NotImplementedError

    async def zscore(self, key: str, member: str) -> float | None:
        """ZSCORE：成员分数。TODO: 实现"""
        raise NotImplementedError

    async def zrem(self, key: str, *members: str) -> int:
        """ZREM：删除成员。TODO: 实现"""
        raise NotImplementedError

    async def zcard(self, key: str) -> int:
        """ZCARD：集合大小。TODO: 实现"""
        raise NotImplementedError

    # ---- 键管理与过期 ----

    async def expire(self, key: str, seconds: int) -> bool:
        """EXPIRE：设置过期时间（秒）。TODO: 实现"""
        raise NotImplementedError

    async def ttl(self, key: str) -> int:
        """TTL：查询剩余过期时间（秒，-1 无过期，-2 不存在）。TODO: 实现"""
        raise NotImplementedError

    async def exists(self, *keys: str) -> int:
        """EXISTS：判断键是否存在（返回存在的个数）。TODO: 实现"""
        raise NotImplementedError

    async def delete(self, *keys: str) -> int:
        """DEL：删除键。TODO: 实现"""
        raise NotImplementedError

    # ---- 管道 ----

    async def pipeline_execute(self, commands: list) -> list:
        """PIPELINE：批量执行多条命令，减少网络往返。TODO: 实现"""
        raise NotImplementedError

    # ---- 发布订阅 ----

    async def publish(self, channel: str, message: str) -> int:
        """PUBLISH：向频道发布消息。TODO: 实现"""
        raise NotImplementedError

    async def subscribe(self, channel: str) -> None:
        """SUBSCRIBE：订阅频道（长连接，通常独立进程运行）。TODO: 实现"""
        raise NotImplementedError
