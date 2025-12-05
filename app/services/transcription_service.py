from sqlalchemy.orm import Session
from app.db.schema import Transcription
from app.models.transcript import TranscriptRead, TranscriptCreate, TranscriptUpdate
from app.core.utils import generate_id
from app.services.task_service import TaskService
from app.models.task import TaskRead
import json
import os
from app.core.config import config
import logging
from app.services.audio_service import AudioService
from app.services.task_service import TaskService
from oryks_google_drive import GoogleDrive
from oryks_google_drive.mime_types import MimeType


class TranscriptionService:
    def __init__(self, session: Session) -> None:
        self._db = session
        self.drive = GoogleDrive()
        self.drive.authenticate_from_credentials(config.GOOGLE_DRIVE_CREDENTIALS)

    def save_transcript_locally(self, transcript: TranscriptCreate):
        transcript_path = os.path.join(config.DATA_DIR, "transcripts", transcript.id + ".json")
        with open(transcript_path, "w") as f:
            data = {
                "task_id": transcript.task_id,
                "transcript": transcript.transcript,
                "language": transcript.language
            }
            json.dump(data, f, indent=4)

    def delete_transcript_locally(self, transcript_id: str):
        logging.info(f"Deleting transcript with id: {transcript_id}")
        transcript_path = os.path.join(config.DATA_DIR, "transcripts", transcript_id + ".json")
        os.remove(transcript_path)
        logging.info(f"Deleted transcript with id: {transcript_id}")

    def upload_transcript_to_drive(self, transcript: TranscriptCreate):
        transcript_path = os.path.join(config.DATA_DIR, "transcripts", transcript.id + ".json")
        try:
            file = self.drive.upload_file(file_path=transcript_path, mime_type=MimeType.APPLICATION_JSON.value)
        except Exception as e:
            raise RuntimeError(f"Failed to upload transcript to Google Drive: {e}")
        return file.get("id", "")
    
    def move_file_in_drive(self, file_id: str, destination_folder_id: str = config.GOOGLE_DRIVE_TRANSCRIPS_FOLDER_ID) -> None:
        """Move a file in Google Drive to a different folder."""
        try:
            self.drive.move_file(file_id, destination_folder_id)
        except Exception as e:
            raise RuntimeError(f"Failed to move file in Google Drive: {e}")
        
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
        return TranscriptRead.from_orm(new_transcript)
    
    def delete_audio(self, task_id: str) -> None:
        logging.info(f"Deleting the task with id: {task_id}. It has been transcribed!")
        task_service = TaskService(session=self._db)
        task = task_service.get_task(task_id=task_id)
        if task:
            audio_id = task.audio_id
            # audio_service = AudioService(session=self._db)
            # audio_service.delete_audio(audio_id)
            logging.info(f"Deleted the audio with id: {audio_id}")
    
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
        
    def update_transcript(self, transcript_id: str, transcript_update: TranscriptUpdate) -> TranscriptRead | None:
        transcript = self._db.query(Transcription).filter(Transcription.id == transcript_id).first()
        if not transcript:
            return None
        if transcript_update.transcript:
            transcript.transcript = transcript_update.transcript
        if transcript_update.fileid:
            transcript.fileid = transcript_update.fileid
        self._db.commit()
        self._db.refresh(transcript)
        return TranscriptRead.from_orm(transcript)
    
    def process_transcript(self, transcript: TranscriptCreate) -> None:
        new_transcript: TranscriptRead = self.create_transcript(transcript)
        self.save_transcript_locally(new_transcript)
        self.delete_audio(new_transcript.task_id)
        file_id: str = self.upload_transcript_to_drive(transcript)
        self.move_file_in_drive(file_id)
        self.delete_transcript_locally(new_transcript.id)
        self.update_transcript(TranscriptUpdate(fileid=file_id))
