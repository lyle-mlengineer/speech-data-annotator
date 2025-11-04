from app.core.config import config  
import os
import yt_dlp
from app.core.utils import generate_id
from typing import TypedDict


class DownloadResult(TypedDict):
    audio_file_path: str
    task_id: str


class AudioService:
    def __init__(self):
        self.data_dir: str = os.path.join(config.DATA_DIR, "raw")
        
    def parse_video_id(self, url: str) -> str:
        video_id: str
        try:
            video_id: str = url.split("=")[1].split("&")[0]
        except IndexError:
            video_id = url
        return video_id
        
    def download_youtube_audio(self, audio_id: str, audio_url: str, output_path: str):
        """
        Downloads the audio from a YouTube video.

        Args:
            url (str): The URL of the YouTube video.
            output_path (str): The directory where the audio file will be saved.
        """

        print(f"Downloading audio for video ID: {audio_id}")
        
        ydl_opts = {
            'format': 'bestaudio/best',  # Selects the best audio format
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Converts to MP3
                'preferredquality': '192', # Audio quality
            }],
            'outtmpl': f'{output_path}/{audio_id}.%(ext)s', # Output file name template
            'noplaylist': True, # Download only the specified video, not a playlist
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([audio_url])
            print(f"Audio downloaded successfully from: {audio_url}")
        except Exception as e:
            print(f"Error downloading audio: {e}")
    
    def download_audio(self, audio_url: str) -> DownloadResult | None:
        audio_id: str = self.parse_video_id(audio_url)
        audio_dir: str = os.path.join(self.data_dir, audio_id)
        audio_file_path: str = os.path.join(audio_dir, f"{audio_id}.mp3")
        result = None
        if not os.path.exists(audio_file_path):
            task_id: str = self.create_task(audio_url)
            try:
                self.update_task(task_id, "IN_PROGRESS")
                if not os.path.exists(audio_dir):
                    os.makedirs(audio_dir)
                self.download_youtube_audio(audio_id, audio_url, audio_dir)
                result = DownloadResult(
                    audio_file_path=audio_file_path,
                    task_id=task_id
                )
            except Exception as e:
                print(f"Error in downloading audio: {e}")
                self.update_task(task_id, "FAILED")
            else:
                self.update_task(task_id, "COMPLETED")
        return result
    
    def create_task(self, audio_url: str):
        print(f"Creating download task for URL: {audio_url}")
        audio_id: str = self.parse_video_id(audio_url)
        task_id: str = generate_id(prefix="TASK")
        print(f"Task created with ID: {task_id} for audio ID: {audio_id}")
        return task_id
        
    def get_task(self, task_id: str):
        print(f"Getting task with ID: {task_id}")
        
    def list_tasks(self):
        print("Listing all tasks")
        
    def update_task(self, task_id: str, status: str):
        print(f"Updating task {task_id} to status {status}")