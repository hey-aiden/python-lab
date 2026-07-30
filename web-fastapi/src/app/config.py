"""应用配置 — 集中管理环境变量和配置项."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "web-fastapi"
    debug: bool = True

    # MySQL 数据库配置
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
