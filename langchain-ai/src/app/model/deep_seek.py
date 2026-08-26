from langchain_deepseek import ChatDeepSeek

from app.config import settings


def load_model_ds():
    """初始化 DeepSeek 模型。"""
    model = ChatDeepSeek(
        model=settings.model_deepseek,
        temperature=settings.temperature,
        api_key=settings.api_key_deepseek,
    )
    return model
