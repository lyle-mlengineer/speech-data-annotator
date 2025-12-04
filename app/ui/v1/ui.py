from fastapi import status
from fastapi import APIRouter, Depends, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.config import config
from app.ui.v1.helpers import (
    assign_task, 
    submit_transcript, 
    get_task_service, 
    get_transcription_service, 
    TaskService, 
    TranscriptionService,
    get_current_user
)
from app.services.utils import get_audio_service, AudioService
from typing import Annotated
import logging

templates = Jinja2Templates(directory=config.TEMPLATES_DIR)
   

router = APIRouter(
    tags=["User Interface"],)

USER_ID: str = "USER-cbba65c0-beb4-4fc0-8041-0f8640b1c444"

@router.get('/', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_landing_page(request: Request):
    """Load the home page"""
    return templates.TemplateResponse(
        "landing_page.html", 
        {
            "request": request,
        }
    )

@router.get('/audio', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_audio_page(request: Request):
    """Load the audio page"""
    return templates.TemplateResponse(
        "audio.html", 
        {
            "request": request,
            "title": "SautiFlow Audio",
            "current_page": "audio" 
        }
    )

@router.post('/audio', status_code=status.HTTP_201_CREATED, response_class=HTMLResponse)
async def download_audio(
    audio_url: Annotated[str, Form()], 
    request: Request,
    service: AudioService = Depends(get_audio_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
    ):
    """Load the audio page"""
    background_tasks.add_task(service.process_audio, audio_url)
    return templates.TemplateResponse(
        "audio.html", 
        {
            "request": request,
            "title": "SautiFlow Audio",
            "current_page": "audio",
        }
    )

@router.get('/speech_to_text', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_speech_to_text_page(
    request: Request,
    user_id: Annotated[str, Depends(get_current_user)],
    service: TaskService = Depends(get_task_service),
    ):
    """Load the speech to text page"""
    logging.info("Transcribing audio")
    audio_url, task_id = assign_task(user_id=user_id, service=service, request=request)
    return templates.TemplateResponse(
        "speech_to_text.html", 
        {
            "request": request,
            "title": "SautiFlow STT",
            "current_page": "stt",
            "audio_id": task_id,
            "audio_src": audio_url,
        }
    )
    
@router.post('/speech_to_text', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def transcribe_audio(
    audio_id: Annotated[str, Form()], 
    language: Annotated[str, Form()],
    transcription: Annotated[str, Form()],
    gender: Annotated[str, Form()],
    speaker: Annotated[str, Form()],
    request: Request,
    keep: Annotated[str, Form()],
    user_id: Annotated[str, Depends(get_current_user)],
    task_service: TaskService = Depends(get_task_service),
    transcription_service: TranscriptionService = Depends(get_transcription_service)
    ):
    """Load the speech to text page"""
    print(f"Audio ID: {audio_id}, Language: {language}, Transcription: {transcription}, Gender: {gender}, Speaker: {speaker}, Keep: {keep}")
    logging.info("Submitting transcription")
    audio_url, task_id = submit_transcript(
        audio_id=audio_id, 
        user_id=user_id, 
        transcript=transcription, 
        language=language, 
        gender=gender,
        speaker=speaker,
        keep=keep,
        service=transcription_service,
        task_service=task_service,
        request=request
    )
    return templates.TemplateResponse(
        "speech_to_text.html", 
        {
            "request": request,
            "title": "SautiFlow STT",
            "current_page": "stt",
            "audio_id": task_id,
            "audio_src": audio_url,
        }
    )

@router.get('/notifications', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_notifications_page(request: Request):
    """Load the text to notifications page"""
    return templates.TemplateResponse(
        "notifications.html", 
        {
            "request": request,
            "title": "SautiFlow notifications",
            "current_page": "notifications"
        }
    )


@router.get('/payment', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_payments_page(request: Request):
    """Load the payments page"""
    return templates.TemplateResponse(
        "payment.html", 
        {
            "request": request,
            "title": "SautiFlow Payment",
            "current_page": "payment"
        }
    )

@router.get('/profile', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_profile_page(request: Request):
    """Load the profile page"""
    return templates.TemplateResponse(
        "profile.html", 
        {
            "request": request,
            "title": "SautiFlow User Profile",
            "current_page": "profile"
        }
    )

@router.get('/dashboard', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_dashboard_page(request: Request):
    """Load the dashboard page"""
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "title": "SautiFlow User dashboard",
            "current_page": "dashboard"
        }
    )


@router.get('/register_form', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_registration_page(request: Request):
    """Load the registration page"""
    return templates.TemplateResponse(
        "register.html", 
        {
            "request": request,
        }
    )

@router.get('/login_form', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_login_page(request: Request):
    """Load the login page"""
    return templates.TemplateResponse(
        "login.html", 
        {
            "request": request,
        }
    )

@router.get('/password_reset_request_form', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def password_reset_request_form(request: Request):
    """Load the password reset request form page"""
    return templates.TemplateResponse(
        "password_reset_request.html", 
        {
            "request": request,
        }
    )

@router.get('/password_reset_form', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def password_reset_form(request: Request):
    """Load the password reset form page"""
    return templates.TemplateResponse(
        "password_reset_form.html", 
        {
            "request": request,
        }
    )