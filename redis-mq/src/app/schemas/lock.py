"""锁相关请求模型。"""

from pydantic import BaseModel, Field


class LockAcquireRequest(BaseModel):
    """加锁请求：锁名 + 过期时间（秒，防止持锁者宕机后死锁）。"""

    lock_name: str
    ttl: int = Field(default=10, ge=1, description="锁过期时间（秒）")


class LockReleaseRequest(BaseModel):
    """释放锁请求：必须带上加锁时返回的 token，防止误删他人锁。"""

    lock_name: str
    token: str


class LockRenewRequest(BaseModel):
    """续期请求：业务未执行完时延长锁的过期时间。"""

    lock_name: str
    token: str
    ttl: int = Field(default=10, ge=1, description="续期时长（秒）")


class CasRequest(BaseModel):
    """乐观锁（CAS）请求：仅当当前值 == expected 时才写入 new_value。

    key 为任意 string 键；expected 为期望旧值，new_value 为要写入的新值。
    被「乐观锁（WATCH）」与「Lua CAS」两个端点复用。
    """

    key: str
    expected: str
    new_value: str


class DeductStockRequest(BaseModel):
    """扣库存请求（Lua 原子操作示例）。key 由 `stock_key(product_id)` 统一生成。"""

    product_id: int | str
    amount: int = Field(gt=0, description="扣减数量")
