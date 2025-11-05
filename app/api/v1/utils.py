from app.models.transcript import TranscriptCreate, TranscriptRead, TranscriptUpdate
from app.models.task import TaskRead, TaskUpdate
from app.services.utils import (
    get_task_service, 
    TaskService, 
    get_audio_service, 
    AudioService, 
    get_transcription_service, 
    TranscriptionService
)
from fastapi import Depends, Request
from app.core.config import config

def assign_task(user_id: str, request: Request, service: TaskService = Depends(get_task_service)) -> str:
    task: TaskRead = service.get_and_assign_task(user_id=user_id)
    audio_path: str = f"raw/{task.audio_id}/{task.id}.wav"
    audio_url: str = request.url_for("data", path=audio_path).__str__()
    return audio_url

def submit_transcript(
    task_id: str, 
    user_id: str,
    transcript: str, 
    language: str,
    service: TranscriptionService = Depends(get_transcription_service)
    ) -> TranscriptRead:
    transcript: TranscriptCreate = TranscriptCreate(task_id=task_id, user_id=user_id, transcript=transcript, language=language)
    return service.create_transcript(transcript)