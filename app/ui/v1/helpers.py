from app.models.task import TaskRead
from fastapi import Depends, Request
from app.models.transcript import TranscriptCreate, TranscriptRead
from app.services.utils import (
    get_task_service, 
    TaskService,  
    get_transcription_service, 
    TranscriptionService
)
from fastapi import BackgroundTasks
import os
from app.core.config import config

def assign_task(
        user_id: str, 
        request: Request, 
        service: TaskService = Depends(get_task_service)
        ) -> str:
    task: TaskRead = service.get_and_assign_task(user_id=user_id)
    print(f"Assigned task: {task}") # Debugging line to check the task assignment
    if not task:
        return "", ""
    return parse_task(task=task, request=request, service=service)

def parse_task(
        task: TaskRead, 
        request: Request, 
        service: TaskService,
        background_tasks: BackgroundTasks = BackgroundTasks()):
    audio_path: str = os.path.join("audio", task.audio_id, f"{task.id}.wav")
    # if not os.path.exists(audio_path):
    #     # background_tasks.add_task(service.download_audio, (task.fileid, task.audio_id, task.id))
    #     service.download_audio(file_id=task.fileid, audio_id=task.audio_id, task_id=task.id)
    audio_url: str = request.url_for("data", path=audio_path).__str__()
    return audio_url, task.id

def submit_transcript(
    audio_id: str, 
    user_id: str,
    transcript: str, 
    language: str,
    gender: str,
    speaker: str,
    keep: str,
    request: Request,
    service: TranscriptionService = Depends(get_transcription_service),
    task_service: TaskService = Depends(get_task_service)
    ) -> TranscriptRead:
    transcript: TranscriptCreate = TranscriptCreate(
        task_id=audio_id, 
        user_id=user_id, 
        transcript=transcript, 
        language=language,
        gender=gender,
        speaker=speaker,
        keep=keep
    )
    transcript = service.create_transcript(transcript=transcript)
    service.update_task(task_id=audio_id, task_service=task_service)
    audio_url, task_id = assign_task(user_id=user_id, request=request, service=task_service)
    return audio_url, task_id

def get_current_user() -> str:
    return "USER-2d5cecd0-b021-438f-a458-61087673b56a"