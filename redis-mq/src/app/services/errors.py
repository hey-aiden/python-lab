"""领域异常 — 服务层抛出，端点层捕获后映射为 HTTP 状态码。

约定：
- 所有领域异常继承 `RedisMqError`，端点层可 catch 基类统一兜底。
- 每个具体异常对应一类可预期故障，docstring 标注建议的 HTTP 状态码。
- 意外错误（bug）不在这里定义，直接交给框架默认 500。
"""


class RedisMqError(Exception):
    """redis-mq 领域异常基类。"""


class RedisUnavailableError(RedisMqError):
    """Redis 连接失败 / 不可用 → 建议 503 Service Unavailable。"""


class RedisResponseError(RedisMqError):
    """Redis 命令执行出错（如 WRONGTYPE 类型不匹配）→ 建议 400 Bad Request。"""
