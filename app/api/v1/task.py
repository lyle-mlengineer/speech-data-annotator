from fastapi import APIRouter, Depends, HTTPException

from app.db.schema import SessionLocal
from app.models.task import TaskRead, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(
    tags=["Task Management"],
)


def get_task_service() -> TaskService:
    return TaskService(session=SessionLocal())


@router.get("/tasks", response_model=list[TaskRead])
def get_tasks(service: TaskService = Depends(get_task_service)):
    return service.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: str, service: TaskService = Depends(get_task_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str, task: TaskUpdate, service: TaskService = Depends(get_task_service)
):
    updated = service.update_task(task_id, task.status, task.user_id )
    if not updated:
        raise HTTPException(status_code=404, detail="task not found")
    return updated


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="task not found")
    return {"success": True}
