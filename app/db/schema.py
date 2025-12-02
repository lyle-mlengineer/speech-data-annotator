from sqlalchemy import String, create_engine, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime, timezone

from app.core.config import config

engine = create_engine(config.db_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    
    
class Audio(Base):
    __tablename__ = "audios"

    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String, index=True)
    # duration: Mapped[float] = mapped_column(Float)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(primary_key=True)
    audio_id: Mapped[str] = mapped_column(String, ForeignKey("audios.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    status: Mapped[str] = mapped_column(String, index=True)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    # duration: Mapped[float] = mapped_column(Float)
    fileid: Mapped[str] = mapped_column(String, nullable=True)
    
class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[str] = mapped_column(primary_key=True)
    task_id: Mapped[str] = mapped_column(String, ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    transcript: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String, index=True)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))