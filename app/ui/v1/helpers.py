from app.models.task import TaskRead
from app.services.utils import get_task_service, TaskService
from fastapi import Depends, Request
from app.core.config import config

def assign_task(user_id: str, request: Request, service: TaskService = Depends(get_task_service)) -> str:
    task: TaskRead = service.get_and_assign_task(user_id=user_id)
    audio_path: str = f"raw/{task.audio_id}/{task.id}.wav"
    audio_url: str = request.url_for("data", path=audio_path).__str__()
    print(audio_url)
    return audio_url