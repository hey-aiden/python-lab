from pydantic import BaseModel


class StreamDataModel(BaseModel):
    content: str
