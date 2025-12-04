from sqlalchemy.orm import Session
from app.db.schema import Transcription
from app.models.transcript import TranscriptRead, TranscriptCreate, TranscriptUpdate
from app.core.utils import generate_id
from app.services.task_service import TaskService
from app.models.task import TaskRead
import json
import os
from app.core.config import config

class TranscriptionService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def save_transcript_locally(self, transcript: TranscriptCreate):
        transcript_path = os.path.join(config.DATA_DIR, "transcripts", transcript.id + ".json")
        with open(transcript_path, "w") as f:
            data = {
                "task_id": transcript.task_id,
                "transcript": transcript.transcript,
                "language": transcript.language
            }
            json.dump(data, f, indent=4)
        
    def create_transcript(self, transcript: TranscriptCreate) -> TranscriptRead:
        new_transcript = Transcription(
            id=generate_id(prefix="TRANSCRIPT"),
            task_id=transcript.task_id,
            user_id=transcript.user_id,
            transcript=transcript.transcript,
            language=transcript.language,
            gender=transcript.gender,
            speaker=transcript.speaker,
            keep=transcript.keep
        )
        self._db.add(new_transcript)
        self._db.commit()
        self._db.refresh(new_transcript)
        self.save_transcript_locally(new_transcript)
        return TranscriptRead.from_orm(new_transcript)
    
    def update_task(self, task_id: str, task_service: TaskService) -> TaskRead | None:
        task = task_service.update_task(task_id, "COMPLETED")
        return task
    
    def get_transcript(self, transcript_id: str) -> TranscriptRead | None:
        transcript = self._db.query(Transcription).filter(Transcription.id == transcript_id).first()
        if not transcript:
            return None
        return TranscriptRead.from_orm(transcript)
    
    def get_transcript_by_task_id(self, task_id: str) -> TranscriptRead | None:
        transcript = self._db.query(Transcription).filter(Transcription.task_id == task_id).first()
        if not transcript:
            return None
        return TranscriptRead.from_orm(transcript)
    
    def get_transcripts_by_user_id(self, user_id: str, offset: int = 0, limit: int = 10) -> list[TranscriptRead | None]:
        transcripts = self._db.query(Transcription).filter(Transcription.user_id == user_id).offset(offset).limit(limit).all()
        if not transcripts:
            return []
        return [TranscriptRead.from_orm(transcript) for transcript in transcripts]
    
    def list_transcripts(self, offset: int = 0, limit: int = 10) -> list[TranscriptRead | None]:
        transcripts = self._db.query(Transcription).offset(offset).limit(limit).all()
        if not transcripts:
            return []
        return [TranscriptRead.from_orm(transcript) for transcript in transcripts]
    
    def delete_transcript(self, transcript_id: str) -> TranscriptRead | None:
        transcript = self._db.query(Transcription).filter(Transcription.id == transcript_id).first()
        if not transcript:
            return None
        self._db.delete(transcript)
        self._db.commit()
        return TranscriptRead.from_orm(transcript)
        
    def update_transcript(self, transcript_id: str, transcript: TranscriptUpdate) -> TranscriptRead | None:
        transcript = self._db.query(Transcription).filter(Transcription.id == transcript_id).first()
        if not transcript:
            return None
        transcript.transcript = transcript.transcript
        self._db.commit()
        self._db.refresh(transcript)
        return TranscriptRead.from_orm(transcript)
    
    