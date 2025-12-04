from sqlalchemy.orm import Session

from app.db.schema import Task
from app.core.utils import generate_id
from app.models.task import TaskRead
import logging
from oryks_google_drive import GoogleDrive
from app.core.config import config
import os


class TaskService:
    def __init__(self, session: Session):
        self._db = session
        self.drive = GoogleDrive()
        self.drive.authenticate_from_credentials(config.GOOGLE_DRIVE_CREDENTIALS)

    def list_tasks(self) -> list[TaskRead]:
        tasks = self._db.query(Task).all()
        tasks = [
            TaskRead(
                id=task.id,
                status=task.status,
                date_created=task.date_created,
                date_updated=task.date_updated,
                audio_id=task.audio_id
            ) for task in tasks
        ]
        return tasks
    
    def assign_task(self, task_id: str, user_id: str) -> TaskRead | None:
        task = self.get_task(task_id)
        if not task:
            return None
        task.user_id = user_id
        task.status = "ASSIGNED"
        self._db.commit()
        self._db.refresh(task)
        task = TaskRead(
            id=task.id,
            status=task.status,
            date_created=task.date_created,
            date_updated=task.date_updated,
            audio_id=task.audio_id,
            user_id=task.user_id,
            fileid=task.fileid
        )
        return task
    
    def un_assign_task(self, task_id: str) -> TaskRead | None:
        task = self.get_task(task_id)
        if not task:
            return None
        task.user_id = None
        task.status = "CREATED"
        self._db.commit()
        self._db.refresh(task)
        task = TaskRead(
            id=task.id,
            status=task.status,
            date_created=task.date_created,
            date_updated=task.date_updated,
            audio_id=task.audio_id,
            user_id=task.user_id,
            fileid=task.fileid
        )
        return task
    
    def get_available_task(self) -> TaskRead | None:
        """Get the first task with `status` = `CREATED`. Order by date added."""
        task = self._db.query(Task).filter(Task.status == "CREATED").order_by(Task.date_created).first()
        if not task:
            return None
        task = TaskRead(
            id=task.id,
            status=task.status,
            date_created=task.date_created,
            date_updated=task.date_updated,
            audio_id=task.audio_id,
            fileid=task.fileid
        )
        return task
        
    def list_available_tasks(self, offset: int = 0, limit: int = 10) -> list[TaskRead]:
        """List available tasks and oredr by date added."""
        tasks = (
            self._db.query(Task)
            .filter(Task.status == "CREATED")
            .order_by(Task.date_created)
            .offset(offset)
            .limit(limit)
            .all()
        )
        tasks = [
            TaskRead(
                id=task.id,
                status=task.status,
                date_created=task.date_created,
                date_updated=task.date_updated,
                audio_id=task.audio_id,
                fileid=task.fileid
            ) for task in tasks
        ]
        
    def list_assigned_tasks(self, offset: int = 0, limit: int = 10) -> list[Task]:
        """List assigned tasks and oredr by date added."""
        return (
            self._db.query(Task)
            .filter(Task.status == "ASSIGNED")
            .order_by(Task.date_created)
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def un_assign_tasks(self):
        tasks = self._db.query(Task).filter(Task.status == "ASSIGNED").all()
        for task in tasks:
            task.status = "CREATED"
            self._db.commit()
            self._db.refresh(task)    
        
    def list_completed_tasks(self, offset: int = 0, limit: int = 10) -> list[Task]:
        """List completed tasks and oredr by date added."""
        return (
            self._db.query(Task)
            .filter(Task.status == "COMPLETED")
            .order_by(Task.date_created)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
    def list_unassigned_tasks(self, offset: int = 0, limit: int = 10) -> list[Task]:
        """List unassigned tasks and oredr by date added."""
        return (
            self._db.query(Task)
            .filter(Task.status == "CREATED")
            .order_by(Task.date_created)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
    def list_user_assigned_tasks(self, user_id: str, offset: int = 0, limit: int = 10) -> list[Task]:
        """List assigned tasks and oredr by date added."""
        return (
            self._db.query(Task)
            .filter(Task.status == "ASSIGNED")
            .filter(Task.user_id == user_id)
            .order_by(Task.date_created)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
    def list_user_completed_tasks(self, user_id: str, offset: int = 0, limit: int = 10) -> list[Task]:
        """List completed tasks and oredr by date added."""
        return (
            self._db.query(Task)
            .filter(Task.status == "COMPLETED")
            .filter(Task.user_id == user_id)
            .order_by(Task.date_created)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
    def get_and_assign_task(self, user_id: str) -> TaskRead | None:
        task = self.get_available_task()
        if not task:
            return None
        task = self.assign_task(task_id=task.id, user_id=user_id)
        task = TaskRead(
            id=task.id,
            status=task.status,
            date_created=task.date_created,
            date_updated=task.date_updated,
            audio_id=task.audio_id,
            fileid=task.fileid,
            user_id=task.user_id
        )
        return task
    
    def mark_task_completed(self, task_id: str) -> Task | None:
        task = self.get_task(task_id)
        if not task:
            return None
        task.status = "COMPLETED"
        self._db.commit()
        self._db.refresh(task)
        return task

    def get_task(self, task_id: str) -> Task | None:
        return self._db.query(Task).filter(Task.id == task_id).first()

    def create_task(self, id: str, audio_id: str) -> Task:
        task = Task(id=id, audio_id=audio_id, status="CREATED")
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task

    def update_task(self, task_id: str, status: str = None, user_id: str = None, fileid: str = None) -> Task | None:
        task = self.get_task(task_id)
        if not task:
            return None
        if status:
            logging.info(f"Updating task {task_id} to status {status}")
            task.status = status
        if user_id:
            logging.info(f"Assigning task {task_id} to user {user_id}")
            task.user_id = user_id
        if fileid:
            logging.info(f"Uploading task {task_id} to file {fileid}")
            task.fileid = fileid
        self._db.commit()
        self._db.refresh(task)
        return task

    def delete_task(self, task_id: str) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        self._db.delete(task)
        self._db.commit()
        return True
    
    def download_audio(self, file_id: str, audio_id: str, task_id: str) -> None:
        """Download an audio file from Google Drive to the specified destination path."""
        logging.info(f"Downloading audio file with ID {file_id} from Google Drive")
        try:
            audio_dir: str = os.path.join(config.DATA_DIR, 'audio', audio_id)
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            destination_path: str = os.path.join(audio_dir, f"{task_id}.wav")
            self.drive.download_file(file_id=file_id, file_path=destination_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download file from Google Drive: {e}")

    def preload_tasks(self) -> None:
        logging.info("Preloading tasks")
        tasks = self.list_unassigned_tasks(limit=config.TASKS_PRE_LOAD)
        for task in tasks:
            audio_id = task.audio_id
            task_id = task.id
            audio_dir: str = os.path.join(config.DATA_DIR, 'audio', audio_id)
            destination_path: str = os.path.join(audio_dir, f"{task_id}.wav")
            if not os.path.exists(destination_path):
                logging.info(f"Downloading audio file with ID {task.fileid} from Google Drive")
                self.download_audio(file_id=task.fileid, audio_id=task.audio_id, task_id=task.id)