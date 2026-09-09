"""Redis key 命名空间与构造函数 — 统一维护业务 key，避免散落硬编码字符串。

约定：
- 用 `:` 分层命名空间
- 前缀是常量，拼 key 是函数；业务代码只调函数、不拼字符串
- 每个业务域（如 poem）一个命名空间，各域 key 互不干扰
"""

POEM_NS = "poem"


def poem_key(poem_id: int | str) -> str:
    """单首诗词本体的 key。"""
    return f"{POEM_NS}:{poem_id}"


def poem_group_key(group: str) -> str:
    """某分组下诗词 ID 集合的 key。"""
    return f"{POEM_NS}:group:{group}"
