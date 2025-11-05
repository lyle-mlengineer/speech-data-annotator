from fastapi import Security, HTTPException, status
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.config import config
from app.ui.v1.helpers import assign_task
from app.services.utils import get_task_service, TaskService

templates = Jinja2Templates(directory=config.templates_dir)
   

router = APIRouter(
    tags=["User Interface"],)

@router.get('/', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_landing_page(request: Request):
    """Load the home page"""
    return templates.TemplateResponse(
        "landing_page.html", 
        {
            "request": request,
        }
    )

@router.get('/speech_to_text', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_speech_to_text_page(
    request: Request,
    service: TaskService = Depends(get_task_service)
    ):
    """Load the speech to text page"""
    user_id: str = "USER-7a595130-cd88-4cba-a1a8-5d8908e07974"
    audio_url: str = assign_task(user_id=user_id, service=service, request=request)
    print()
    return templates.TemplateResponse(
        "speech_to_text.html", 
        {
            "request": request,
            "title": "SautiFlow STT",
            "current_page": "stt",
            "audio_id": "tts-audio",
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