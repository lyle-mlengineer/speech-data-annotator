from app.core.config import config  
import os
import yt_dlp
from app.core.utils import generate_id
from typing import TypedDict
import librosa
import soundfile as sf
import logging


class DownloadResult(TypedDict):
    audio_file_path: str
    task_id: str
    audio_id: str


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
        logging.info(f"Downloading audio for video ID: {audio_id}")
        
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
            logging.info(f"Audio downloaded successfully from: {audio_url}")
        except Exception as e:
            logging.error(f"Error downloading audio: {e}")
    
    def download_audio(self, audio_url: str) -> DownloadResult | None:
        audio_id: str = self.parse_video_id(audio_url)
        audio_dir: str = os.path.join(self.data_dir, audio_id)
        audio_file_path: str = os.path.join(audio_dir, f"{audio_id}.mp3")
        result = None
        if not os.path.exists(audio_file_path):
            task_id: str = self.create_task(audio_url)
            try:
                self.update_task(task_id, "DOWNLOADING")
                if not os.path.exists(audio_dir):
                    os.makedirs(audio_dir)
                self.download_youtube_audio(audio_id, audio_url, audio_dir)
                result = DownloadResult(
                    audio_file_path=audio_file_path,
                    task_id=task_id,
                    audio_id=audio_id
                )
            except Exception as e:
                logging.error(f"Error in downloading audio: {e}")
                self.update_task(task_id, "DOWNLOAD_FAILED")
            else:
                self.update_task(task_id, "DOWNLOADED")
        return result
    
    def slice_audio(self, audio_id: str, audio_file_path: str, task_id: str) -> None:
        self.update_task(task_id, "SLICING")
        audio_dir: str = os.path.join(self.data_dir, audio_id)
        audio , sr = librosa.load(audio_file_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=0)
        try:
            for start_idx in range(0, len(audio), config.MAX_AUDIO_DURATION_SECONDS * sr):
                end_idx = start_idx + config.MAX_AUDIO_DURATION_SECONDS * sr
                audio_segment = audio[start_idx:end_idx]
                if len(audio_segment) < config.MIN_AUDIO_DURATION_SECONDS * sr:
                    continue
                sf.write(os.path.join(audio_dir, f"{audio_id}_{start_idx}.wav"), audio_segment, sr)
        except Exception as e:
            logging.error(f"Error slicing audio: {e}")
            self.update_task(task_id, "SLICING_FAILED")
        else:
            self.update_task(task_id, "SLICED")
    
    def create_task(self, audio_url: str):
        logging.info(f"Creating download task for URL: {audio_url}")
        audio_id: str = self.parse_video_id(audio_url)
        task_id: str = generate_id(prefix="TASK")
        logging.info(f"Task created with ID: {task_id} for audio ID: {audio_id}")
        return task_id
        
    def get_task(self, task_id: str):
        logging.info(f"Getting task with ID: {task_id}")
        
    def list_tasks(self):
        logging.info("Listing all tasks")
        
    def update_task(self, task_id: str, status: str):
        logging.info(f"Updating task {task_id} to status {status}")
        logging.info(f"Task {task_id} updated to status {status}")
