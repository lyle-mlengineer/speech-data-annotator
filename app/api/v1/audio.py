from fastapi import APIRouter, Depends, Form, status, BackgroundTasks
from typing import Annotated
from app.api.v1.schema import AudioDetails

from app.db.schema import SessionLocal
from app.models.audio import AudioRead
# from app.models.user import UserCreate, UserRead
# from app.services.user_service import UserService
from app.services.audio_service import AudioService

router = APIRouter(
    tags=["Audio Management"],
)

def get_audio_service():
    return AudioService(session=SessionLocal())   
    
@router.post("/audio", response_model=AudioDetails, status_code=status.HTTP_200_OK)
async def get_audio_details(audio_url: Annotated[str, Form()], service = Depends(get_audio_service)):
    """Dependency to get audio by ID"""
    audio_details = service.get_audio_details(audio_url)
    return audio_details

@router.post("/audio/download", response_model=None, status_code=status.HTTP_201_CREATED)
async def download_audio(
    audio_url: Annotated[str, Form()], 
    service = Depends(get_audio_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
    ):
    """Dependency to download audio file"""
    # audio_details = service.get_audio_details(audio_url)
    # if not audio_details:
    #     return { "message": "Audio details not found" }
    # Initiate the download and slicing tasks
    background_tasks.add_task(service.download_and_slice_audio , audio_url)
    # download_audio_task.delay(audio_url)
    # download_audio_task.apply_async((audio_url,), link=slice_audio_task.s())
    return { "message": "Audio download initiated" }

@router.get("/audio/{audio_id}", response_model=AudioRead, status_code=status.HTTP_200_OK)
async def get_audio(audio_id: str, service = Depends(get_audio_service)):
    """Dependency to get audio by ID"""
    audio = service.get_audio(audio_id)
    if not audio:
        return { "message": "Audio not found" }
    return audio

@router.get("/audio", response_model=list[AudioRead], status_code=status.HTTP_200_OK)
async def list_audio(service = Depends(get_audio_service)):
    """Dependency to list all audio"""
    audio_list = service.list_audio()
    return audio_list