from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DATABASE_URL = "sqlite:///./keyword_stats.db"

engine = create_engine(DATABASE_URL, echo=False, future=True)


class Base(DeclarativeBase):
    pass


class KeywordEvent(Base):
    __tablename__ = "keyword_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    count: Mapped[int] = mapped_column(Integer, default=1)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


Base.metadata.create_all(engine)

app = FastAPI(title="AI关键词搜索次数采集服务", version="0.1.0")

SupportedPlatform = Literal[
    "chatgpt",
    "claude",
    "gemini",
    "perplexity",
    "grok",
    "kimi",
    "qwen",
]


class RecordRequest(BaseModel):
    platform: SupportedPlatform
    keyword: str = Field(min_length=1, max_length=255)
    count: int = Field(default=1, ge=1, le=1_000_000)


class QueryResponse(BaseModel):
    platform: str
    keyword: str
    total_count: int


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/events")
def record_event(payload: RecordRequest) -> dict[str, str | int]:
    keyword = payload.keyword.strip().lower()
    if not keyword:
        raise HTTPException(status_code=400, detail="keyword 不能为空")

    with Session(engine) as session:
        event = KeywordEvent(
            platform=payload.platform,
            keyword=keyword,
            count=payload.count,
        )
        session.add(event)
        session.commit()

    return {"message": "记录成功", "count": payload.count}


@app.get("/stats", response_model=list[QueryResponse])
def list_stats(platform: SupportedPlatform | None = None) -> list[QueryResponse]:
    with Session(engine) as session:
        stmt = (
            select(
                KeywordEvent.platform,
                KeywordEvent.keyword,
                func.sum(KeywordEvent.count).label("total_count"),
            )
            .group_by(KeywordEvent.platform, KeywordEvent.keyword)
            .order_by(func.sum(KeywordEvent.count).desc())
        )

        if platform:
            stmt = stmt.where(KeywordEvent.platform == platform)

        rows = session.execute(stmt).all()

    return [
        QueryResponse(platform=row.platform, keyword=row.keyword, total_count=row.total_count)
        for row in rows
    ]
