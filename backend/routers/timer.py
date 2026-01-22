"""
Timer router - Task timer functionality.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.db_models import Account, TimerSession, Task, SystemLog
from backend.auth import get_current_user
from backend.models import TimerStartRequest, TimerResponse

router = APIRouter()

@router.post("/start", response_model=TimerResponse, status_code=201)
def start_timer(
    request: TimerStartRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a timer session."""
    # Check if task exists (if provided)
    task = None
    if request.task_id:
        task = db.query(Task).filter(
            Task.id == request.task_id,
            Task.account_id == current_user.id
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
    
    # Allow multiple timers - no need to check for active timer
    # Users can have multiple timers running for different tasks
    
    # Create new timer session
    timer = TimerSession(
        account_id=current_user.id,
        task_id=request.task_id,
        duration_seconds=request.duration_seconds,
        status="active",
        started_at=datetime.utcnow()
    )
    
    db.add(timer)
    
    # Update task status if provided
    if task:
        task.status = "in_progress"
    
    db.commit()
    db.refresh(timer)
    
    # Log timer start
    log = SystemLog(
        level="INFO",
        component="timer",
        message=f"Timer started: {request.duration_seconds}s",
        context_data={"timer_id": timer.id, "task_id": request.task_id}
    )
    db.add(log)
    db.commit()
    
    return timer

@router.post("/{timer_id}/stop", response_model=TimerResponse)
def stop_timer(
    timer_id: int,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop an active timer."""
    timer = db.query(TimerSession).filter(
        TimerSession.id == timer_id,
        TimerSession.account_id == current_user.id
    ).first()
    
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    
    if timer.status != "active":
        raise HTTPException(status_code=400, detail="Timer is not active")
    
    # Calculate actual duration
    actual_duration = (datetime.utcnow() - timer.started_at).total_seconds()
    timer.actual_seconds = int(actual_duration)
    timer.status = "completed"
    timer.completed_at = datetime.utcnow()
    
    # Calculate focus score (simplified - based on interruptions)
    # In real implementation, this would track actual interruptions
    focus_score = max(0.0, 1.0 - (timer.interruptions * 0.1))
    timer.focus_score = focus_score
    
    # Update task if associated
    if timer.task_id:
        task = db.query(Task).get(timer.task_id)
        if task:
            # Update actual time
            task.actual_minutes = int(actual_duration / 60)
            # Calculate completion accuracy
            if task.estimated_minutes:
                task.completion_accuracy = task.estimated_minutes / task.actual_minutes if task.actual_minutes > 0 else 1.0
    
    db.commit()
    db.refresh(timer)
    
    return timer

@router.post("/{timer_id}/pause", response_model=TimerResponse)
def pause_timer(
    timer_id: int,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause an active timer."""
    timer = db.query(TimerSession).filter(
        TimerSession.id == timer_id,
        TimerSession.account_id == current_user.id
    ).first()
    
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    
    if timer.status != "active":
        raise HTTPException(status_code=400, detail="Timer is not active")
    
    timer.status = "paused"
    timer.paused_at = datetime.utcnow()
    
    db.commit()
    db.refresh(timer)
    
    return timer

@router.get("/active", response_model=List[TimerResponse])
def get_active_timers(
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active timers for the user."""
    timers = db.query(TimerSession).filter(
        TimerSession.account_id == current_user.id,
        TimerSession.status == "active"
    ).order_by(TimerSession.started_at.desc()).all()
    
    return timers

@router.get("/", response_model=List[TimerResponse])
def get_timer_history(
    limit: int = 50,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timer history for the user."""
    timers = db.query(TimerSession).filter(
        TimerSession.account_id == current_user.id
    ).order_by(TimerSession.started_at.desc()).limit(limit).all()
    
    return timers
