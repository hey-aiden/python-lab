"""API 总路由 — 按版本分发."""

from fastapi import APIRouter

from .v1.router import router as v1_router

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")
