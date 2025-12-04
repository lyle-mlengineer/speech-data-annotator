from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from app.db.schema import get_db
from sqlalchemy.sql import text
import os
from app.core.config import config
import shutil
import logging
from app.services.task_service import TaskService


def is_db_ready(session: Session = get_db()):
    try:
        next(session).execute(text("SELECT 1"))
    except OperationalError:
        return False
    return True

def delete_all_audio():
    logging.info("Deleting all audio")
    audio_dir: str = os.path.join(config.DATA_DIR, "audio")
    for audio in os.listdir(audio_dir):
        shutil.rmtree(os.path.join(audio_dir, audio))
    logging.info("All audio deleted")
    
def delete_all_transcripts():
    logging.info("Deleting all transcripts")
    transcript_dir: str = os.path.join(config.DATA_DIR, "transcripts")
    for transcript in os.listdir(transcript_dir):
        os.remove(os.path.join(transcript_dir, transcript))
    logging.info("All transcripts deleted")

def delete_local_data():
    logging.info("Deleting local data")
    # delete_all_audio()
    # delete_all_transcripts()
    logging.info("Local data deleted")

def preload_tasks():
    logging.info("Preloading tasks")
    # service: TaskService = TaskService(session=get_db())
    # service.preload_tasks()
    logging.info("Tasks preloaded")

def un_assign_tasks():
    logging.info("Un-assigning tasks")
    service: TaskService = TaskService(session=get_db())
    # service.un_assign_tasks()
    logging.info("Tasks un-assigned")