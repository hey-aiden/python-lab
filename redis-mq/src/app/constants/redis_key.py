"""Redis key 命名空间与构造函数 — 统一维护业务 key，避免散落硬编码字符串。

约定：
- 用 `:` 分层命名空间
- 前缀是常量，拼 key 是函数；业务代码只调函数、不拼字符串
- 每个业务域（如 poem）一个命名空间，各域 key 互不干扰
"""

POEM_NS = "poem"
SESSION_NS = "session"
RANK_NS = "rank"
LOCK_NS = "lock"
STOCK_NS = "stock"
SECKILL_NS = "seckill"


def poem_key(poem_id: int | str) -> str:
    """单首诗词本体的 key。"""
    return f"{POEM_NS}:{poem_id}"


def poem_group_key(group: str) -> str:
    """某分组下诗词 ID 集合的 key。"""
    return f"{POEM_NS}:group:{group}"


def session_key(user_id: int | str) -> str:
    """某用户会话的 key：`session:{user_id}`。"""
    return f"{SESSION_NS}:{user_id}"


def score_rank_key() -> str:
    """排行榜 zset 的 key：`rank:score`。"""
    return f"{RANK_NS}:score"


def player_info_key(user_id: str) -> str:
    """某玩家详情 hash 的 key：`rank:player:{user_id}`。"""
    return f"{RANK_NS}:player:{user_id}"


def lock_key(name: str) -> str:
    """某分布式锁的 key：`lock:{name}`（锁名是业务语义，key 加命名空间隔离）。"""
    return f"{LOCK_NS}:{name}"


def stock_key(product_id: int | str) -> str:
    """某商品库存的 key：`stock:{product_id}`（Lua 扣库存示例用）。"""
    return f"{STOCK_NS}:{product_id}"


def seckill_stock_key(activity_id: int | str) -> str:
    """秒杀活动库存 key：`seckill:stock:{activity_id}`（string 存剩余数量）。"""
    return f"{SECKILL_NS}:stock:{activity_id}"


def seckill_order_key(activity_id: int | str, user_id: int | str) -> str:
    """用户限购幂等 key：`seckill:order:{activity_id}:{user_id}`（存在即已抢过）。"""
    return f"{SECKILL_NS}:order:{activity_id}:{user_id}"


def seckill_orders_key(activity_id: int | str) -> str:
    """活动下单名单 zset key：`seckill:orders:{activity_id}`（member=user_id，score=下单时间）。"""
    return f"{SECKILL_NS}:orders:{activity_id}"


def seckill_closed_key(activity_id: int | str) -> str:
    """活动封盘标记 key：`seckill:closed:{activity_id}`。"""
    return f"{SECKILL_NS}:closed:{activity_id}"
