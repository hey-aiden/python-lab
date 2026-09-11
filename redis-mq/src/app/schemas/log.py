"""日志埋点相关请求模型。"""

from typing import Any

from pydantic import BaseModel, Field


class TrackEventRequest(BaseModel):
    """用户行为埋点事件。

    - event：事件名（如 page_view / click / add_to_cart）
    - user_id：用户标识，同时作为 Kafka 消息 key，保证同一用户事件分区内有序
    - payload：附加信息（页面、元素、耗时等），无固定结构故用 dict
    - timestamp：客户端可选携带（如离线补报时的真实发生时间）；缺省由服务端补齐
    """

    event: str
    user_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: float | None = None
