import logging
from pathlib import Path

from fastapi import FastAPI

from app.api.router import api_router
from app.core.middleware import setup_middleware

# 日志配置必须在 app 创建之前，且只有入口处能调 basicConfig
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOG_DIR / "app.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    force=True,  # 覆盖 uvicorn 已有的配置
)

app = FastAPI(title="web-fastapi", version="0.1.0")

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
