CACHE_TIME_TYPE: dict[str, int] = {"short_time": 20, "mid_time": 60, "long_time": 180}

SHORT_SET: set[str] = {"user_name"}
MID_SET: set[str] = {"user_account"}


def get_cache_time(cache_type: str) -> int:
    """根据缓存类型返回 TTL（秒），未匹配时回退到 long_time。"""
    if cache_type in SHORT_SET:
        return CACHE_TIME_TYPE["short_time"]
    if cache_type in MID_SET:
        return CACHE_TIME_TYPE["mid_time"]
    return CACHE_TIME_TYPE["long_time"]
