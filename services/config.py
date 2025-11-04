from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()


class Config(BaseSettings):
    YOUTUBE_CREDENTIALS_PATH: str = os.getenv(
        "YOUTUBE_CREDENTIALS_PATH", "credentials.json"
    )
    CLIENT_SECRET_FILE: str = os.environ.get(
        "CLIENT_SECRET_FILE", "C:/Users/User/Downloads/secrets.json"
    )
    DATA_DIR: str = "C:\\Datasets\\audio\\maongezi"
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)
    REDIS_DB: int = os.environ.get("REDIS_DB", 0)
    REDIS_AUDIO_DOWNLOAD_QUEUE: str = os.environ.get("REDIS_AUDIO_DOWNLOAD_QUEUE", "audio_download")
    REDIS_AUDIO_SLICE_QUEUE: str = os.environ.get("REDIS_AUDIO_SLICE_QUEUE", "audio_slice")
    REDIS_AUDIO_UPLOAD_QUEUE: str = os.environ.get("REDIS_AUDIO_UPLOAD_QUEUE", "audio_upload")

    @property
    def db_url(self):
        return f"sqlite:///./{self.db_name}"


config = Config()
