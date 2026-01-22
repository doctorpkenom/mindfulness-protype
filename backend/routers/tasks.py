"""
Task management router - CRUD operations for user tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.db_models import Account, Task, SystemLog
from backend.auth import get_current_user
from backend.models import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status_filter: str = None,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for the current user."""
    query = db.query(Task).filter(Task.account_id == current_user.id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.account_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task."""
    task = Task(
        account_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        estimated_minutes=task_data.estimated_minutes,
        priority=task_data.priority,
        difficulty=task_data.difficulty,
        energy_required=task_data.energy_required,
        focus_required=task_data.focus_required,
        category=task_data.category,
        tags=task_data.tags or [],
        status="pending"
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Log task creation
    log = SystemLog(
        level="INFO",
        component="task_manager",
        message=f"Task created: {task.title}",
        context_data={"task_id": task.id, "account_id": current_user.id}
    )
    db.add(log)
    db.commit()
    
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.account_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # If marking as completed, set completion time and calculate accuracy
    if task_data.status == "completed" and task.status != "completed":
        task.completed_at = datetime.utcnow()
        if task.estimated_minutes and task.actual_minutes:
            task.completion_accuracy = task.estimated_minutes / task.actual_minutes
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.account_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return None
