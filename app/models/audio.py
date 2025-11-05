from pydantic import BaseModel
from datetime import datetime

    
class AudioCreate(BaseModel):
    status: str
    id: str
    duration: float

class AudioRead(BaseModel):
    id: str
    status: str
    date_created: datetime
    date_updated: datetime
    duration: float