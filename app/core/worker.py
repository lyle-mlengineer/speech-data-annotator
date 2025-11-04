from celery import Celery
from celery.result import AsyncResult
from app.core.config import config 
from app.services.audio_service import AudioService
from app.services.audio_service import DownloadResult
import logging


celery = Celery(
    'worker',
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

service = AudioService()


@celery.task(name='download_audio_task')
def download_audio_task(audio_url: str) -> int:
    audio_file_path = service.download_audio(audio_url)
    return audio_file_path

@celery.task(name='slice_audio_task')
def slice_audio_task(result: DownloadResult) -> None:
    if result:
        logging.info(f"Slicing audio file at: {result['audio_file_path']}")
        service.slice_audio(result['audio_id'], result['audio_file_path'], result['task_id'])
    return None