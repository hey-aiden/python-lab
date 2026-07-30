from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Poem(Base):
    __tablename__ = "poem"

    # 主键
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="poem唯一 ID，数据库自增",
    )

    # ── 核心字段（NOT NULL，创建时必须传）──
    title: Mapped[str] = mapped_column(
        String(200),
        comment="诗词标题",
    )

    author: Mapped[str] = mapped_column(
        String(100),
        comment="作者",
    )

    # ── 时间戳（NOT NULL，但由数据库自动填入，创建时不需手动传）──
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 数据库自动填入，字段 NOT NULL
        comment="记录数据入库时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 首次 INSERT 时数据库自动填入
        onupdate=func.now(),  # 每次 UPDATE 时数据库自动刷新
        comment="记录最后更新时间",
    )
