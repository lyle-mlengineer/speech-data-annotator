from sqlalchemy import String, create_engine, DateTime, ForeignKey, Float, Text, Integer
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
    # assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[str] = mapped_column(primary_key=True)
    task_id: Mapped[str] = mapped_column(String, ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    transcript: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String, index=True)
    gender: Mapped[str] = mapped_column(String, index=True)
    speaker: Mapped[str] = mapped_column(String, index=True)
    keep: Mapped[str] = mapped_column(String, index=True)
    fileid: Mapped[str] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class Speaker(Base):
    __tablename__ = "speakers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    dialect: Mapped[str] = mapped_column(String, index=True)
    use: Mapped[str] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Language(Base):
    __tablename__ = "languages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    abbreviation: Mapped[str] = mapped_column(String, index=True)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))