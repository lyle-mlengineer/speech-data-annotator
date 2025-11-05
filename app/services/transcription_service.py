from sqlalchemy.orm import Session
from app.db.schema import Transcription
from app.models.transcript import TranscriptRead, TranscriptCreate, TranscriptUpdate
from app.core.utils import generate_id
from app.services.task_service import TaskService
from app.models.task import TaskRead

class TranscriptionService:
    def __init__(self, session: Session) -> None:
        self._db = session
        
    def create_transcript(self, transcript: TranscriptCreate) -> TranscriptRead:
        new_transcript = Transcription(
            id=generate_id(prefix="TRANSCRIPT"),
            task_id=transcript.task_id,
            user_id=transcript.user_id,
            transcript=transcript.transcript,
            language=transcript.language
        )
        self._db.add(new_transcript)
        self._db.commit()
        self._db.refresh(new_transcript)
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
    
    