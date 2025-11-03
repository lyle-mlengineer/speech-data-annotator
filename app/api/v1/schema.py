from pydantic import BaseModel, Field


class AudioDetails(BaseModel):
    id: str = Field(..., description="Unique identifier for the video")
    url: str = Field(..., description="URL of the video")
    title: str = Field(..., description="Title of the video")
    # duration_seconds: int = Field(..., description="Duration of the video in seconds")
    # uploaded_at: str = Field(..., description="Upload timestamp of the video")