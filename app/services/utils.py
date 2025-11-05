from app.db.schema import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.task_service import TaskService


def get_task_service(session: Session = Depends(get_db)):
    return TaskService(session)