import json
import os
import re

from tubectrl import YouTube
from tubectrl.models import Video

from app.core.config import config as BaseConfig
from app.api.v1.schema import AudioDetails
import yt_dlp


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
    with open(os.path.join(BaseConfig.DATA_DIR, video_id, f"{video_id}.json"), "r") as f:
        video_details: AudioDetails = json.load(f)
    return video_details


def save_video_details(video_details: AudioDetails) -> None:
    video_path = os.path.join(BaseConfig.DATA_DIR, video_details.id)
    if not os.path.exists(video_path):
        os.makedirs(video_path)
    with open(
        os.path.join(video_path, f"{video_details.id}.json"), "w"
    ) as f:
        json.dump(video_details.dict(), f, indent=4)
        
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
    if os.path.exists(os.path.join(BaseConfig.DATA_DIR, video_id)):
        video_details: AudioDetails = load_video_details(video_id)
    else:
        youtube: YouTube = get_youtube()
        video: Video = find_video(video_id, youtube)
        video_details = parse_video_details(video, video_url)
        save_video_details(video_details)
    return video_details

def download_youtube_audio(audio_url: str, output_path: str):
    """
    Downloads the audio from a YouTube video.

    Args:
        url (str): The URL of the YouTube video.
        output_path (str): The directory where the audio file will be saved.
    """
    
    video_id: str = parse_video_id(audio_url)
    print(f"Downloading audio for video ID: {video_id}")
    
    ydl_opts = {
        'format': 'bestaudio/best',  # Selects the best audio format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Converts to MP3
            'preferredquality': '192', # Audio quality
        }],
        'outtmpl': f'{output_path}/{video_id}.%(ext)s', # Output file name template
        'noplaylist': True, # Download only the specified video, not a playlist
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([audio_url])
        print(f"Audio downloaded successfully from: {audio_url}")
    except Exception as e:
        print(f"Error downloading audio: {e}")
        
async def download_video_audio(audio_url: str) -> None:
    audio_id: str = parse_video_id(audio_url)
    audio_dir: str = os.path.join(BaseConfig.DATA_DIR, audio_id)
    audio_file_path: str = os.path.join(audio_dir, f"{audio_id}.mp3")
    if not os.path.exists(audio_file_path):
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        download_youtube_audio(audio_url, os.path.join(BaseConfig.DATA_DIR, audio_id))