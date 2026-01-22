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
    from datetime import datetime as dt
    from fastapi import HTTPException
    
    try:
        # Parse deadline if provided
        deadline = None
        if task_data.deadline:
            try:
                # Handle both date-only and datetime strings
                deadline_str = task_data.deadline.replace("Z", "+00:00")
                deadline = dt.fromisoformat(deadline_str)
            except (ValueError, AttributeError) as e:
                print(f"[ERROR] Failed to parse deadline '{task_data.deadline}': {e}")
                # Don't fail, just skip deadline
        
        # Parse recurrence_end_date if provided
        recurrence_end = None
        if task_data.recurrence_end_date:
            try:
                recurrence_str = task_data.recurrence_end_date.replace("Z", "+00:00")
                recurrence_end = dt.fromisoformat(recurrence_str)
            except (ValueError, AttributeError) as e:
                print(f"[ERROR] Failed to parse recurrence_end_date '{task_data.recurrence_end_date}': {e}")
                # Don't fail, just skip recurrence_end_date
        
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
            status="pending",
            deadline=deadline,
            recurrence_pattern=task_data.recurrence_pattern,
            recurrence_end_date=recurrence_end,
            custom_recurrence_days=task_data.custom_recurrence_days
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
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR /api/tasks/] Failed to create task: {str(e)}")
        print(error_details)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        )

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
    from datetime import datetime as dt
    update_data = task_data.dict(exclude_unset=True)
    
    # Handle deadline parsing
    if "deadline" in update_data and update_data["deadline"]:
        try:
            update_data["deadline"] = dt.fromisoformat(update_data["deadline"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            update_data["deadline"] = None
    elif "deadline" in update_data and update_data["deadline"] is None:
        update_data["deadline"] = None
    
    # Handle recurrence_end_date parsing
    if "recurrence_end_date" in update_data and update_data["recurrence_end_date"]:
        try:
            update_data["recurrence_end_date"] = dt.fromisoformat(update_data["recurrence_end_date"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            update_data["recurrence_end_date"] = None
    elif "recurrence_end_date" in update_data and update_data["recurrence_end_date"] is None:
        update_data["recurrence_end_date"] = None
    
    # Handle custom_recurrence_days
    if "custom_recurrence_days" in update_data:
        if update_data["custom_recurrence_days"] is not None:
            task.custom_recurrence_days = update_data["custom_recurrence_days"]
        else:
            task.custom_recurrence_days = None
    
    for field, value in update_data.items():
        if field != "custom_recurrence_days":  # Already handled above
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
