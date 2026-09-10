from pydantic import BaseModel


class SessionRequest(BaseModel):
    user_id: str
    user_name: str

class UserInfoRequest(BaseModel):
    session_id: str
    user_id: str