from fastapi import APIRouter, Depends, HTTPException, Form, Request, status
from typing import Annotated
from fastapi.responses import RedirectResponse

# from app.db.schema import SessionLocal
# from app.models.user import UserCreate, UserRead
# from app.services.user_service import UserService

router = APIRouter()

def get_transcription_service():
    pass
    # return TranscriptionService(session=SessionLocal())   
    
@router.post("/transcribe")
def transcribe_audio(
    audio_id: Annotated[str, Form()], 
    language: Annotated[str, Form()],
    transcription: Annotated[str, Form()],
    request: Request,
    service = Depends(get_transcription_service)):
    """Endpoint to handle audio transcription requests"""
    print(f"Transcribing audio with ID: {audio_id}")
    return RedirectResponse(url=request.url_for("get_speech_to_text_page"), status_code=status.HTTP_303_SEE_OTHER)