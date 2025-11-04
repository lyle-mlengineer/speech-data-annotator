from pydantic import BaseModel

class TaskCreate(BaseModel):
    id: str
    status: str
    audio_id: str
    
    
class TaskUpdate(BaseModel):
    status: str = None
    user_id: str = None
    
    
class TaskRead(BaseModel):
    id: str
    status: str
    date_created: str
    date_updated: str
    audio_id: str
    user_id: str = None