from sqlalchemy.orm import Session

from app.db.schema import Task
from app.core.utils import generate_id


class TaskService:
    def __init__(self, session: Session):
        self._db = session

    def list_tasks(self) -> list[Task]:
        return self._db.query(Task).all() 

    def get_task(self, task_id: str) -> Task | None:
        return self._db.query(Task).filter(Task.id == task_id).first()

    def create_task(self, id: str, audio_id: str) -> Task:
        task = Task(id=id, audio_id=audio_id, status="CREATED")
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task

    def update_task(self, task_id: str, status: str = None, user_id: str = None) -> Task | None:
        task = self.get_task(task_id)
        if not task:
            return None
        if status:
            task.status = status
        if user_id:
            task.user_id = user_id
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
