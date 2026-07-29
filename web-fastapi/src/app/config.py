"""应用配置 — 集中管理环境变量和配置项."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "web-fastapi"
    debug: bool = True

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
