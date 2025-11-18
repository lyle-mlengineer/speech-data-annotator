from app.models.task import TaskRead
from fastapi import Depends, Request
from app.models.transcript import TranscriptCreate, TranscriptRead
from app.services.utils import (
    get_task_service, 
    TaskService,  
    get_transcription_service, 
    TranscriptionService
)

def assign_task(user_id: str, request: Request, service: TaskService = Depends(get_task_service)) -> str:
    task: TaskRead = service.get_and_assign_task(user_id=user_id)
    print(f"Assigned task: {task}") # Debugging line to check the task assignment
    if not task:
        return "", ""
    return parse_task(task=task, request=request)

def parse_task(task: TaskRead, request: Request):
    audio_path: str = f"raw/{task.audio_id}/{task.id}.wav"
    audio_url: str = request.url_for("data", path=audio_path).__str__()
    return audio_url, task.id

def submit_transcript(
    audio_id: str, 
    user_id: str,
    transcript: str, 
    language: str,
    request: Request,
    service: TranscriptionService = Depends(get_transcription_service),
    task_service: TaskService = Depends(get_task_service)
    ) -> TranscriptRead:
    transcript: TranscriptCreate = TranscriptCreate(task_id=audio_id, user_id=user_id, transcript=transcript, language=language)
    transcript = service.create_transcript(transcript=transcript)
    service.update_task(task_id=audio_id, task_service=task_service)
    audio_url, task_id = assign_task(user_id=user_id, request=request, service=task_service)
    return audio_url, task_id