from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()


class Config(BaseSettings):
    app_name: str = "SautiFlow Labs"
    debug: bool = False
    db_user: str = ""
    db_password: str = ""
    db_name: str = "test.db"

    templates_dir: str = "app/ui/v1/templates"
    static_dir: str = "app/ui/v1/static"
    
    YOUTUBE_CREDENTIALS_PATH: str = os.getenv(
        "YOUTUBE_CREDENTIALS_PATH", "credentials.json"
    )
    CLIENT_SECRET_FILE: str = os.environ.get(
        "CLIENT_SECRET_FILE", "C:/Users/User/Downloads/secrets.json"
    )
    DATA_DIR: str = "C:\\Datasets\\audio\\maongezi"
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")            # NEW
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")
    MAX_AUDIO_DURATION_SECONDS: int = 30  # 15 minutes
    MIN_AUDIO_DURATION_SECONDS: int = 10  # 5 seconds

    @property
    def db_url(self):
        return f"sqlite:///./{self.db_name}"


config = Config()
