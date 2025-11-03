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
    DATA_DIR: str = "app/api/v1/data"

    @property
    def db_url(self):
        return f"sqlite:///./{self.db_name}"


config = Config()
