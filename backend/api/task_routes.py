from fastapi import APIRouter, Header, HTTPException, Request, Response
from pydantic import BaseModel
from typing import List, Optional
from service.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])
task_service = TaskService()

idempotency_store = {}

class TaskCreateRequest(BaseModel):
    name: str

class TaskUpdateRequest(BaseModel):
    name: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    name: str
    is_completed: bool
    owner_id: Optional[int] = None
    requestId: Optional[str] = None


@router.get("/", response_model=List[TaskResponse])
def get_tasks(request: Request):
    tasks = task_service.get_all_tasks()
    req_id = getattr(request.state, "request_id", None)
    
    response_list = []
    for t in tasks:
        resp = TaskResponse(
            id=t.id, 
            name=t.name, 
            is_completed=t.is_completed, 
            owner_id=t.owner_id,
            requestId=req_id
        )
        response_list.append(resp)
        
    return response_list

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, request: Request):
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return TaskResponse(
        id=task.id, 
        name=task.name, 
        is_completed=task.is_completed, 
        owner_id=task.owner_id,
        requestId=getattr(request.state, "request_id", None)
    )

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    request: Request,
    task_data: TaskCreateRequest, 
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    req_id = getattr(request.state, "request_id", None)

    if not idempotency_key:
        raise HTTPException(status_code=400, detail="idempotency_key_required")

    if idempotency_key in idempotency_store:
        cached_response = idempotency_store[idempotency_key]
        cached_response["requestId"] = req_id
        return cached_response

    try:
        task = task_service.create_task(task_data.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    response_data = {
        "id": task.id,
        "name": task.name,
        "is_completed": task.is_completed,
        "owner_id": task.owner_id,
        "requestId": req_id
    }

    idempotency_store[idempotency_key] = response_data
    
    return response_data

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdateRequest, request: Request):
    task = task_service.update_task(task_id, task_data.name, task_data.is_completed)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return TaskResponse(
        id=task.id, 
        name=task.name, 
        is_completed=task.is_completed, 
        owner_id=task.owner_id,
        requestId=getattr(request.state, "request_id", None)
    )

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)