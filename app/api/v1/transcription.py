from fastapi import APIRouter, Depends, HTTPException, Form, Request, status
from typing import Annotated
from app.services.transcription_service import TranscriptionService
from app.api.v1.utils import get_transcription_service, submit_transcript
import logging
from app.models.transcript import TranscriptCreate, TranscriptRead

router = APIRouter(
    tags=["Transcription Management"],
)
   
    
@router.post("/transcribe", response_model=TranscriptRead, status_code=status.HTTP_201_CREATED)
def transcribe_audio(
    transcript: TranscriptCreate,
    service: TranscriptionService = Depends(get_transcription_service)):
    """Endpoint to handle audio transcription requests"""
    transcript = submit_transcript(
        task_id=transcript.task_id, 
        user_id=transcript.user_id, 
        transcript=transcript.transcript, 
        language=transcript.language, 
        service=service
    )
    return transcript

@router.get("/transcript/{transcript_id}", response_model=TranscriptRead, status_code=status.HTTP_200_OK)
def get_transcript(transcript_id: str, service: TranscriptionService = Depends(get_transcription_service)):
    transcript = service.get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    return transcript

@router.delete("/transcript/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcript(transcript_id: str, service: TranscriptionService = Depends(get_transcription_service)):
    service.delete_transcript(transcript_id)
    return None

@router.put("/transcript/{transcript_id}", response_model=TranscriptRead, status_code=status.HTTP_200_OK)
def update_transcript(transcript_id: str, transcript: TranscriptCreate, service: TranscriptionService = Depends(get_transcription_service)):
    return service.update_transcript(transcript_id, transcript)

@router.get("/transcripts", response_model=list[TranscriptRead], status_code=status.HTTP_200_OK)
def list_transcripts(service: TranscriptionService = Depends(get_transcription_service)):
    return service.list_transcripts()