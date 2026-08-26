from app.model import load_model_ds


def load_model(model_type: str):
    """按类型返回对应的模型实例。"""
    if model_type == "deep_seek":
        return load_model_ds()
    raise ValueError(f"不支持的模型类型: {model_type}")


def init() -> None:
    """初始化 DeepSeek 模型并调用一次。"""
    model = load_model("deep_seek")

    response = model.invoke("你好，你是谁？")
    print(response.content)
