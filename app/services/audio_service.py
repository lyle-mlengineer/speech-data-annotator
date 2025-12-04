from app.core.config import config  
import os
import yt_dlp
import shutil
from app.core.utils import generate_id
from app.services.helpers import (
    get_youtube, 
    find_video, 
    parse_video_details, 
    save_video_details, 
    load_video_details
)
from typing import TypedDict
import librosa
import soundfile as sf
import logging
from pydantic import BaseModel, Field
from tubectrl import YouTube
from tubectrl.models import Video
from sqlalchemy.orm import Session
from app.db.schema import Audio
from app.services.task_service import TaskService
from app.db.schema import SessionLocal
from app.db.schema import Task
from oryks_google_drive import GoogleDrive
from oryks_google_drive.mime_types import MimeType
from fastapi import UploadFile, HTTPException
from app.core.utils import generate_id


class AudioDetails(BaseModel):
    id: str = Field(..., description="Unique identifier for the video")
    url: str = Field(..., description="URL of the video")
    title: str = Field(..., description="Title of the video")
    # duration_seconds: int = Field(..., description="Duration of the video in seconds")
    # uploaded_at: str = Field(..., description="Upload timestamp of the video")


class DownloadResult(TypedDict):
    audio_file_path: str
    task_id: str
    audio_id: str


class AudioService:
    def __init__(self, session: Session):
        self.data_dir: str = os.path.join(config.DATA_DIR, "audio")
        self._db = session
        self.drive = GoogleDrive()
        self.drive.authenticate_from_credentials(config.GOOGLE_DRIVE_CREDENTIALS)
        
    def parse_video_id(self, url: str) -> str:
        video_id: str
        try:
            video_id: str = url.split("=")[1].split("&")[0]
        except IndexError:
            video_id = url
        return video_id
    
    def get_audio_details(self, video_url: str) -> AudioDetails:
        video_id: str = self.parse_video_id(video_url)
        metadata_path = os.path.join(config.DATA_DIR, "metadata", f"{video_id}.json")
        if os.path.exists(metadata_path):
            video_details: AudioDetails = load_video_details(video_id)
        else:
            youtube: YouTube = get_youtube()
            video: Video = find_video(video_id, youtube)
            video_details = parse_video_details(video, video_url)
            save_video_details(video_details)
        return video_details
    
    def get_audio_metadata(self, audio_id: str):
        logging.info(f"Getting metadata for audio ID: {audio_id}")
        
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
            logging.info(f"Downloading audio for video ID: {audio_id}")
            self.create_audio(audio_id)
            try:
                self.update_audio(audio_id, "DOWNLOADING")
                if not os.path.exists(audio_dir):
                    os.makedirs(audio_dir)
                self.download_youtube_audio(audio_id, audio_url, audio_dir)
                result = DownloadResult(
                    audio_file_path=audio_file_path,
                    audio_id=audio_id
                )
            except Exception as e:
                logging.error(f"Error in downloading audio: {e}")
                self.update_audio(audio_id, "DOWNLOAD_FAILED")
            else:
                self.update_audio(audio_id, "DOWNLOADED")
        else:
            logging.info(f"Audio already downloaded for video ID: {audio_id}")
        return result
    
    def slice_audio(self, audio_id: str, audio_file_path: str) -> None:
        self.update_audio(audio_id, "SLICING")
        audio_dir: str = os.path.join(self.data_dir, audio_id)
        audio , sr = librosa.load(audio_file_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=0)
        try:
            for i, start_idx in enumerate(range(0, len(audio), config.MAX_AUDIO_DURATION_SECONDS * sr)):
                end_idx = start_idx + config.MAX_AUDIO_DURATION_SECONDS * sr
                audio_segment = audio[start_idx:end_idx]
                if len(audio_segment) < config.MIN_AUDIO_DURATION_SECONDS * sr:
                    continue
                task_id: str = f"{audio_id}_{i+1}"
                sf.write(os.path.join(audio_dir, f"{task_id}.wav"), audio_segment, sr)
                self.create_task(id=task_id, audio_id=audio_id)
        except Exception as e:
            logging.error(f"Error slicing audio: {e}")
            self.update_audio(audio_id, "SLICING_FAILED")
        else:
            self.update_audio(audio_id, "SLICED")

    def upload_to_google_drive(self, file_path: str) -> str:
        """Upload a file to Google Drive and return the file ID."""
        try:
            file = self.drive.upload_file(
                file_path,
                mime_type=MimeType.AUDIO_MP3.value if file_path.endswith('.mp3') else MimeType.AUDIO_WAV.value
            )
            return file.get("id", "")
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to Google Drive: {e}")
        
    def move_file_in_drive(self, file_id: str, destination_folder_id: str = config.GOOGLE_DRIVE_FOLDER_ID) -> None:
        """Move a file in Google Drive to a different folder."""
        try:
            self.drive.move_file(file_id, destination_folder_id)
        except Exception as e:
            raise RuntimeError(f"Failed to move file in Google Drive: {e}")

    def download_and_slice_audio(self, audio_url: str) -> DownloadResult | None:
        logging.info(f"Downloading and slicing audio for URL: {audio_url}")
        download_result = self.download_audio(audio_url)
        if not download_result:
            return None
        audio_id: str = download_result['audio_id']
        audio_file_path: str = download_result['audio_file_path']
        self.slice_audio(audio_id, audio_file_path)
        return download_result
            
    def create_task(self, id: str, audio_id: str) -> Task:
        logging.info(f"Creating task for audio ID: {audio_id} and segment ID: {id}")
        service = TaskService(session=self._db)
        task = service.create_task(id=id, audio_id=audio_id)
        self._db.add(task)
        self._db.commit()
        logging.info(f"Task created for audio ID: {audio_id} and segment ID: {id}")
        return task
    
    def create_audio(self, audio_id: str):
        audio = Audio(id=audio_id, status="CREATED")
        self._db.add(audio)
        self._db.commit()
        logging.info(f"Task created for audio ID: {audio_id}")
        return audio_id
        
    def get_audio(self, audio_id: str) -> Audio | None:
        logging.info(f"Getting audio with ID: {audio_id}")
        audio = self._db.query(Audio).filter(Audio.id == audio_id).first()
        return audio
        
    def list_audio(self) -> list[Audio]:
        logging.info("Listing all audio")
        return self._db.query(Audio).all()
        
    def update_audio(self, audio_id: str, status: str) -> None | Audio:
        logging.info(f"Updating task {audio_id} to status {status}")
        audio = self._db.query(Audio).filter(Audio.id == audio_id).first()
        if not audio:
            return None
        audio.status = status
        self._db.commit()
        logging.info(f"Task {audio_id} updated to status {status}")
        return audio

    def process_audio(self, audio_url: str) -> None:
        logging.info(f"Processing audio for URL: {audio_url}")
        download_result = self.download_audio(audio_url)
        if not download_result:
            return None
        audio_id: str = download_result['audio_id']
        audio_file_path: str = download_result['audio_file_path']
        self.slice_audio(audio_id, audio_file_path)
        # audio_dir: str = os.path.join(self.data_dir, audio_id)
        # service: TaskService = TaskService(session=self._db)
        # for file in os.listdir(audio_dir):
        #     if file.endswith(".wav"):
        #         file_path = os.path.join(audio_dir, file)
        #         file_id = self.upload_to_google_drive(file_path)
        #         task_id = file.split(".")[0]
        #         service.update_task(task_id=task_id, fileid=file_id)
        #         self.move_file_in_drive(file_id)
        # self.update_audio(audio_id, "UPLOADED")
        # self.delete_audio(audio_id)

    def save_uploaded_file(self, upload_file: UploadFile) -> dict:
        """Save an uploaded file to the specified destination."""
        try:
            # Save the uploaded file
            audio_id: str = generate_id(prefix="AUDIO")
            extension: str = os.path.splitext(upload_file.filename)[1]
            audio_dir: str = os.path.join(config.DATA_DIR, "audio", audio_id)
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            file_path = os.path.join(audio_dir, f"{audio_id}{extension}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        except Exception as e:
            logging.error(f"There was an error uploading the file: {e}")
            raise HTTPException(status_code=400, detail="There was an error uploading the file")
        finally:
            upload_file.file.close()
        return {"audio_id": audio_id, "audio_file_path": file_path}
    
    def process_uploaded_file(self, upload_file: UploadFile) -> None:
        logging.info(f"Processing uploaded file: {upload_file.filename}")
        result = self.save_uploaded_file(upload_file)
        audio_id: str = result['audio_id']
        audio_path: str = result['audio_file_path']
        self.create_audio(audio_id)
        self.slice_audio(audio_id, audio_path)

    def delete_audio(self, audio_id: str) -> None:
        logging.info(f"Deleting audio with ID: {audio_id}")
        audio_dir: str = os.path.join(self.data_dir, audio_id)
        audio_file_path: str = os.path.join(audio_dir, f"{audio_id}.mp3")
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        if os.path.exists(audio_dir):
            shutil.rmtree(audio_dir)
        self.update_audio(audio_id, "DELETED")