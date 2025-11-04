from fastapi import APIRouter, Depends, HTTPException, Form, Request, status
from typing import Annotated
from fastapi.responses import RedirectResponse
from app.api.v1.schema import AudioDetails
from app.api.v1.utils import get_audio_details
from app.core.worker import download_audio_task, slice_audio_task

# from app.db.schema import SessionLocal
# from app.models.user import UserCreate, UserRead
# from app.services.user_service import UserService

router = APIRouter(
    tags=["Audio Management"],
)

def get_audio_service():
    pass
    # return AudioService(session=SessionLocal())   
    
@router.post("/audio", response_model=AudioDetails, status_code=status.HTTP_200_OK)
async def get_audio(audio_url: Annotated[str, Form()], service = Depends(get_audio_service)):
    """Dependency to get audio by ID"""
    audio_details = await get_audio_details(audio_url)
    return audio_details

@router.post("/audio/download", response_model=None, status_code=status.HTTP_201_CREATED)
async def download_audio(audio_url: Annotated[str, Form()], service = Depends(get_audio_service)):
    """Dependency to download audio file"""
    audio_details = await get_audio_details(audio_url)
    # download_audio_task.delay(audio_url)
    download_audio_task.apply_async((audio_url,), link=slice_audio_task.s())
    return { "message": "Audio download initiated", "details": audio_details }
