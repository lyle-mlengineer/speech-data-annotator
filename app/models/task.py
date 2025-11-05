from pydantic import BaseModel
from datetime import datetime

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
    date_created: datetime
    date_updated: datetime
    audio_id: str
    user_id: str | None = None
    
    # def from_orm(self, task: Task) -> TaskRead:
    #     return TaskRead(**task.__dict__)