from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from service.task_service import TaskService

router = APIRouter()
task_service = TaskService()


class CreateTaskRequest(BaseModel):
    name: str


class UpdateTaskRequest(BaseModel):
    name: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    name: str
    is_completed: bool


def error_response(code: str, message: str, status_code: int):
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": "TaskError",
            "code": code,
            "details": [{"field": "general", "message": message}],
        },
    )


@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks():
    tasks = task_service.get_all_tasks()
    return [{"id": t.id, "name": t.name, "is_completed": t.is_completed} for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = task_service.get_task_by_id(task_id)
    if not task:
        error_response("NOT_FOUND", "Task not found", status.HTTP_404_NOT_FOUND)
    return {"id": task.id, "name": task.name, "is_completed": task.is_completed}


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(request: CreateTaskRequest):
    if not request.name.strip():
        error_response(
            "VALIDATION_ERROR", "Name cannot be empty", status.HTTP_400_BAD_REQUEST
        )

    task = task_service.create_task(request.name)
    return {"id": task.id, "name": task.name, "is_completed": task.is_completed}


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, request: UpdateTaskRequest):
    task = task_service.update_task(
        task_id, new_name=request.name, is_completed=request.is_completed
    )
    if not task:
        error_response("NOT_FOUND", "Task not found", status.HTTP_404_NOT_FOUND)
    return {"id": task.id, "name": task.name, "is_completed": task.is_completed}


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    success = task_service.delete_task(task_id)
    if not success:
        error_response("NOT_FOUND", "Task not found", status.HTTP_404_NOT_FOUND)
