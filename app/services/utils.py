from app.db.schema import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.task_service import TaskService
from app.services.audio_service import AudioService
from app.services.transcription_service import TranscriptionService


def get_task_service(session: Session = Depends(get_db)):
    return TaskService(session)

def get_audio_service(session: Session = Depends(get_db)):
    return AudioService(session)

def get_transcription_service(session: Session = Depends(get_db)):
    return TranscriptionService(session)