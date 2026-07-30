"""依赖注入 — 数据库会话、认证等共享依赖."""

from fastapi import HTTPException, Request

from app.core.db import get_db  # noqa: F401  # 重导出，方便统一从 deps 导入


def verify_cookie(request: Request) -> dict:
    """从 cookie 中读取 session 字段，验证是否有效.

    如果 cookie 里没有 session，返回 401.
    """
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(status_code=401, detail="未登录，缺少 session cookie")
    # TODO: 在这里解析 JWT 或查询 Redis/DB 验证 session
    user_id = session  # 目前把 cookie 原始值当 user_id 返回
    return {"user_id": user_id}


def get_common_deps() -> dict:
    """示例：返回通用依赖数据，后续可替换为数据库会话等."""
    return {"version": "0.1.0"}
