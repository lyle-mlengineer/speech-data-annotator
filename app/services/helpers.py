from tubectrl import YouTube
from tubectrl.models import Video
import json
import os
from app.core.config import config as BaseConfig
from app.api.v1.schema import AudioDetails


def get_youtube(
    client_secret_file: str = BaseConfig.CLIENT_SECRET_FILE,
    credentials_path: str = None,
) -> YouTube:
    youtube: YouTube = None
    if credentials_path:
        print("youtube from credentails")
        youtube = YouTube()
        youtube.authenticate_from_credentials(credentials_path=credentials_path)
    else:
        print("youtube from path")
        youtube = YouTube(client_secret_file=client_secret_file)
        youtube.authenticate(client_secret_file)
    return youtube

def find_video(video_id: str, youtube: YouTube) -> Video:
    video: Video = youtube.find_video_by_id(video_id=video_id)
    return video


def parse_video_details(video: Video, video_url: str) -> AudioDetails:
    video_details: AudioDetails = AudioDetails(
        id=video.id,
        url=video_url,
        title=video.snippet.title,
        # duration_seconds=video.duration_seconds,
        # uploaded_at=video.uploaded_at,
    )
    return video_details


def load_video_details(video_id: str) -> AudioDetails:
    with open(os.path.join(BaseConfig.DATA_DIR, "metadata", f"{video_id}.json"), "r") as f:
        video_details: AudioDetails = json.load(f)
    return video_details


def save_video_details(video_details: AudioDetails) -> None:
    metadata_path = os.path.join(BaseConfig.DATA_DIR, "metadata", f"{video_details.id}.json")
    with open(
        metadata_path, "w"
    ) as f:
        json.dump(video_details.model_dump(), f, indent=4)