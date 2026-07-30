import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.router import api_router
from app.core.db import engine
from app.core.middleware import setup_middleware
from app.models import Base  # 导入 Base，确保所有模型已注册到 metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时自动建表（开发阶段用），停止时关闭连接池."""
    # 启动：自动创建 ORM 模型中定义的所有表（已存在的表不会被重复创建）
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # 开发阶段数据库没启动或连不上时，不阻塞服务启动
        logging.getLogger(__name__).warning(
            "数据库建表失败（服务仍可启动，API 不依赖数据库时不受影响）: %s", e
        )
    yield
    # 停止：释放连接池
    engine.dispose()


# 日志配置必须在 app 创建之前，且只有入口处能调 basicConfig
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOG_DIR / "app.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    force=True,  # 覆盖 uvicorn 已有的配置
)

app = FastAPI(title="web-fastapi", version="0.1.0", lifespan=lifespan)

setup_middleware(app)
app.include_router(api_router, prefix="/api")


def start():
    """开发服务器入口，启动前自动释放 8000 端口."""
    import os
    import signal
    import subprocess

    result = subprocess.run(
        ["lsof", "-ti:8000"], capture_output=True, text=True, check=False
    )
    for pid in result.stdout.strip().split():
        try:
            os.kill(int(pid), signal.SIGKILL)
            print(f"[dev] killed old process on port 8000 (pid={pid})")
        except ProcessLookupError:
            pass  # 进程已不存在

    import uvicorn

    uvicorn.run("app.main:app", reload=True)


def run():
    """生产服务器入口."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",   # 绑定所有网卡，容器外才能访问
        port=8000,
        workers=4,         # 4 个 worker 进程
        log_level="info",
    )
