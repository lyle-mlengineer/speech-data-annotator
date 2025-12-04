from pydantic import BaseModel

class UserOAuth(BaseModel):
    access_token: str