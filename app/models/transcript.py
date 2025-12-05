from pydantic import BaseModel
from datetime import datetime


class Transcript(BaseModel):
    id: str | None = None
    task_id: str
    user_id: str
    language: str
    
    @staticmethod
    def from_orm(transcript):
        return Transcript(
            id=transcript.id, 
            task_id=transcript.task_id, 
            user_id=transcript.user_id,
            language=transcript.language
            )


class TranscriptCreate(Transcript):
    transcript: str
    gender: str
    speaker: str
    keep: str
    
    @staticmethod
    def from_orm(transcript):
        return TranscriptCreate(
            id=transcript.id, 
            task_id=transcript.task_id, 
            user_id=transcript.user_id,
            transcript=transcript.transcript,
            language=transcript.language,
            gender=transcript.gender,
            speaker=transcript.speaker,
            keep=transcript.keep
            )

class TranscriptRead(Transcript):
    date_created: datetime
    date_updated: datetime
    
    @staticmethod
    def from_orm(transcript):
        return TranscriptRead(
            id=transcript.id, 
            task_id=transcript.task_id, 
            user_id=transcript.user_id,
            date_created=transcript.date_created,
            date_updated=transcript.date_updated,
            language=transcript.language,
            gender=transcript.gender,
            speaker=transcript.speaker,
            keep=transcript.keep
            )
        
class TranscriptUpdate(Transcript):
    transcript: str | None = None
    fileid: str | None = None