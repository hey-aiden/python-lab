"""秒杀抢购相关请求模型。"""

from pydantic import BaseModel, Field


class SeckillInitRequest(BaseModel):
    """初始化秒杀活动：活动 ID + 初始库存。"""

    activity_id: str
    stock: int = Field(gt=0, description="初始库存")


class SeckillOrderRequest(BaseModel):
    """抢购下单：活动 ID + 用户 ID（每个用户限抢一次）。"""

    activity_id: str
    user_id: str


class SeckillRefundRequest(BaseModel):
    """退款 / 取消订单：回补库存。"""

    activity_id: str
    user_id: str


class SeckillCloseRequest(BaseModel):
    """封盘结算：活动 ID。"""

    activity_id: str
