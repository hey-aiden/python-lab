"""业务异常 — 纯 Python，不依赖 FastAPI."""


class NotFoundError(Exception):
    """资源不存在 → HTTP 404."""


class ForbiddenError(Exception):
    """无权访问 → HTTP 403."""
