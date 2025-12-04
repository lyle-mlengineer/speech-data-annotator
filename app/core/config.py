from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()


class Config(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    app_name: str = "SautiFlow Labs"
    debug: bool = False

    TEMPLATES_DIR: str = "app/ui/v1/templates"
    STATIC_DIR: str = "app/ui/v1/static"
    
    YOUTUBE_CREDENTIALS_PATH: str = os.getenv(
        "YOUTUBE_CREDENTIALS_PATH", "credentials.json"
    )
    CLIENT_SECRET_FILE: str = os.environ.get(
        "CLIENT_SECRET_FILE", "/home/lyle/Downloads/secrets.json"
    )
    
    # DATA_DIR: str = "/home/lyle/datasets/audio/maongezi"
    DATA_DIR: str = "app/api/v1/data" 

    GOOGLE_DRIVE_FOLDER_ID: str = "161MWUwPv6O0wpmCB3Il6wasQ4L0dStOF"
    GOOGLE_DRIVE_CREDENTIALS: str = "/home/lyle/.drive/credentials.json"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "0.0.0.0")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT", 5432)
    
    MAX_AUDIO_DURATION_SECONDS: int = 30  # 15 minutes
    MIN_AUDIO_DURATION_SECONDS: int = 10  # 5 seconds

    @property
    def db_url(self):
        if self.ENV == "development":
            return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@localhost:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        elif self.ENV == "production":
            return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@ep-still-forest-aho47jlh-pooler.c-3.us-east-1.aws.neon.tech/{self.POSTGRES_DB}?sslmode=require&channel_binding=require'


config = Config()
