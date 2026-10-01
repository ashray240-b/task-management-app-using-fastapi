from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, payload)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    return crud.get_tasks(
        db, skip=skip, limit=limit, status=status_filter.value if status_filter else None
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
    return crud.update_task(db, task, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
    crud.delete_task(db, task)
