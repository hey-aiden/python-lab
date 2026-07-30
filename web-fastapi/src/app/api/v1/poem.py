"""诗词 API — 模糊搜索接口."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.poem import PoemCreate, PoemResponse
from app.services.errors import NotFoundError
from app.services.poem import get_all_poem, get_poem, insert_poem

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/insert_poem", response_model=PoemResponse)
def insertPoem(body: PoemCreate, db: Session = Depends(get_db)):
    """新增诗词。Pydantic 校验后，拆成原始值传给 service."""
    return insert_poem(db, title=body.title, author=body.author)


@router.get("/get_poem", response_model=list[PoemResponse])
def getPoem(
    title: str = Query(
        ...,  # ... = 必填参数
        min_length=1,  # 至少 1 个字符
        description="诗词标题（支持模糊搜索，匹配 Poem.title 列）",
    ),
    db: Session = Depends(get_db),
):
    """按标题模糊搜索诗词，返回匹配的结果列表."""
    try:
        return get_poem(db, title)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/get_all_poem/{id}", response_model=PoemResponse)
def getAllPoem(
    id: int,  # 路径参数，不需要 Query()
    db: Session = Depends(get_db),
):
    """按主键 ID 查询单条诗词."""
    try:
        return get_all_poem(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
