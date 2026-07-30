from fastapi import APIRouter, Depends

from app.api.deps import verify_cookie

from . import hello, poem, stream, user

# dependencies → 整个 v1 路由都需要 cookie 鉴权
# 如果某个端点不需要鉴权，用 @router.get("/path", dependencies=[]) 覆盖
router = APIRouter(dependencies=[Depends(verify_cookie)])
router.include_router(hello.router, tags=["hello"])
router.include_router(poem.router, tags=["poem"])
router.include_router(stream.router, tags=["stream"])
router.include_router(user.router, tags=["user"])
