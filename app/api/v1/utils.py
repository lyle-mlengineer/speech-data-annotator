import json
import os
from fastapi import HTTPException, status

from tubectrl import YouTube
from tubectrl.models import Video

from app.core.config import config as BaseConfig
from app.api.v1.schema import AudioDetails
import yt_dlp
import redis
from redis.exceptions import ConnectionError


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


def parse_video_id(url: str) -> str:
    video_id: str
    try:
        video_id: str = url.split("=")[1].split("&")[0]
    except IndexError:
        video_id = url
    return video_id


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


async def get_audio_details(video_url: str) -> AudioDetails:
    video_id: str = parse_video_id(video_url)
    metadata_path = os.path.join(BaseConfig.DATA_DIR, "metadata", f"{video_id}.json")
    if os.path.exists(metadata_path):
        video_details: AudioDetails = load_video_details(video_id)
    else:
        youtube: YouTube = get_youtube()
        video: Video = find_video(video_id, youtube)
        video_details = parse_video_details(video, video_url)
        save_video_details(video_details)
    return video_details

def schedule_audio_download(audio_url: str) -> str:
    r = redis.Redis(host=BaseConfig.REDIS_HOST, port=BaseConfig.REDIS_PORT, db=BaseConfig.REDIS_DB)
    quota_exceeded: str = r.hget(name="quota", key="quota_exceeded")
    if quota_exceeded is not None and quota_exceeded.decode("utf-8") == "true":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You have exhausted your daily youtube quota",
    )
    video_id: str = parse_video_id(audio_url)
    try:
        data: dict = {"audio_id": video_id, "audio_url": audio_url}
        audio_dir: str = os.path.join(BaseConfig.DATA_DIR, "raw", video_id)
        audio_file_path: str = os.path.join(audio_dir, f"{video_id}.mp3")
        if not os.path.exists(audio_file_path):
            r.lpush(BaseConfig.REDIS_AUDIO_DOWNLOAD_QUEUE, json.dumps(data))
    except ConnectionError as e:
        print(e)