from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.poem import Poem
from app.services.errors import NotFoundError


def insert_poem(db: Session, title: str, author: str) -> Poem:
    """新增诗词，返回创建后的 Poem 对象（含自增 id）."""
    poem = Poem(title=title, author=author)
    db.add(poem)
    db.commit()
    db.refresh(poem)
    return poem


def get_all_poem(db: Session, id: int) -> Poem:
    """按主键 ID 查询单条诗词，不存在抛 NotFoundError.

    db.get() 是 SQLAlchemy 按主键查询的最快方式，直接走主键索引。
    """
    poem = db.get(Poem, id)
    if not poem:
        raise NotFoundError(f"未找到 ID 为 {id} 的诗词")
    return poem


def get_poem(db: Session, title: str) -> list[Poem]:
    """按诗词标题模糊搜索，返回匹配的结果列表."""
    results = list(db.execute(select(Poem).where(Poem.title.like(f"%{title}%"))).scalars().all())
    if not results:
        raise NotFoundError(f"未找到标题包含 '{title}' 的诗词")
    return results
