"""Hello 业务逻辑 — 纯 Python，不依赖 FastAPI."""

from app.services.errors import ForbiddenError, NotFoundError


def get_greeting(item_id: str) -> dict:
    if item_id == "0":
        raise NotFoundError(f"item_id={item_id} 不存在")
    if item_id == "admin":
        raise ForbiddenError("无权访问 admin")
    return {"message": f"Hello FastAPI, item_id={item_id}"}


def say_hi(msg: str) -> dict:
    return {"msg": f"how are you ? from {msg}"}


def get_form(data: dict) -> dict:
    return {"user_name": data.get("user_name", "")}
