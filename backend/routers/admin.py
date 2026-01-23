"""
Admin API endpoints for user account management and system administration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import random

from backend.database import get_db
from backend.db_models import Account, Task, TimerSession, Schedule, ScheduleItem, SystemLog
from backend.auth import get_current_user
from backend.db_models import Account as DBAccount

router = APIRouter()

# Request/Response Models
class AccountResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None

class SimulatedDataRequest(BaseModel):
    days: int = 30

def require_admin(current_user: Account = Depends(get_current_user)):
    """Dependency to ensure user is admin."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/accounts", response_model=List[AccountResponse])
def get_all_accounts(
    current_user: Account = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all user accounts (admin only)."""
    accounts = db.query(DBAccount).order_by(DBAccount.created_at.desc()).all()
    return accounts

@router.put("/accounts/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: Account = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user account (admin only)."""
    account = db.query(DBAccount).filter(DBAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Prevent self-demotion
    if account.id == current_user.id and account_data.is_admin is False:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin status")
    
    # Update fields
    if account_data.username is not None:
        # Check if username is already taken by another account
        existing = db.query(DBAccount).filter(
            DBAccount.username == account_data.username,
            DBAccount.id != account_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        account.username = account_data.username
    
    if account_data.email is not None:
        # Check if email is already taken by another account
        existing = db.query(DBAccount).filter(
            DBAccount.email == account_data.email,
            DBAccount.id != account_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        account.email = account_data.email
    
    if account_data.is_admin is not None:
        account.is_admin = account_data.is_admin
    
    if account_data.is_active is not None:
        account.is_active = account_data.is_active
    
    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    
    # Log update
    log = SystemLog(
        level="INFO",
        component="admin",
        message=f"Account {account.username} updated by admin",
        context_data={"account_id": account_id, "updated_by": current_user.id}
    )
    db.add(log)
    db.commit()
    
    return account

@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    current_user: Account = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user account (admin only)."""
    account = db.query(DBAccount).filter(DBAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Prevent self-deletion
    if account.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    username = account.username
    
    # Log deletion before deleting
    log = SystemLog(
        level="INFO",
        component="admin",
        message=f"Account {username} deleted by admin",
        context_data={"account_id": account_id, "deleted_by": current_user.id}
    )
    db.add(log)
    
    # Delete account (cascade will handle related records)
    db.delete(account)
    db.commit()
    
    return {"status": "deleted", "username": username}

@router.post("/generate-simulated-data")
def generate_simulated_data(
    request: SimulatedDataRequest,
    current_user: Account = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Generate realistic simulated user data over a period of time for ML training."""
    days = max(1, min(365, request.days))  # Clamp between 1 and 365 days
    
    # Get current user's account
    account = db.query(DBAccount).filter(DBAccount.id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Generate data going backwards from today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    generated_count = {
        "tasks": 0,
        "timer_sessions": 0,
        "schedules": 0,
        "completions": 0
    }
    
    # Task categories and patterns
    task_templates = [
        {"title": "Morning workout", "category": "health", "difficulty": 3, "energy": 0.6, "minutes": 30},
        {"title": "Review emails", "category": "work", "difficulty": 2, "energy": 0.4, "minutes": 20},
        {"title": "Team meeting", "category": "work", "difficulty": 2, "energy": 0.5, "minutes": 60},
        {"title": "Write report", "category": "work", "difficulty": 4, "energy": 0.7, "minutes": 90},
        {"title": "Lunch break", "category": "personal", "difficulty": 1, "energy": 0.2, "minutes": 30},
        {"title": "Code review", "category": "work", "difficulty": 3, "energy": 0.6, "minutes": 45},
        {"title": "Evening walk", "category": "health", "difficulty": 1, "energy": 0.3, "minutes": 20},
        {"title": "Read book", "category": "learning", "difficulty": 2, "energy": 0.4, "minutes": 40},
        {"title": "Dinner prep", "category": "daily", "difficulty": 2, "energy": 0.4, "minutes": 45},
        {"title": "Project planning", "category": "work", "difficulty": 3, "energy": 0.6, "minutes": 60},
    ]
    
    for day_offset in range(days):
        day_date = today - timedelta(days=day_offset)
        
        # Generate 2-5 tasks per day
        num_tasks = random.randint(2, 5)
        for _ in range(num_tasks):
            template = random.choice(task_templates)
            
            # Add some variation
            estimated_minutes = template["minutes"] + random.randint(-10, 20)
            priority = random.randint(1, 5)
            difficulty = max(1, min(5, template["difficulty"] + random.randint(-1, 1)))
            
            # Create task
            task = Task(
                account_id=account.id,
                title=template["title"],
                description=f"Simulated task from {day_date.date()}",
                estimated_minutes=estimated_minutes,
                priority=priority,
                difficulty=difficulty,
                energy_required=template["energy"] + random.uniform(-0.1, 0.1),
                focus_required=0.5 + random.uniform(-0.2, 0.2),
                category=template["category"],
                tags=["simulated", "training"],
                status="completed",
                completed_at=day_date + timedelta(hours=random.randint(9, 17), minutes=random.randint(0, 59))
            )
            db.add(task)
            db.flush()  # Get task ID
            
            generated_count["tasks"] += 1
            
            # Create timer session (70% completion rate)
            if random.random() < 0.7:
                actual_minutes = estimated_minutes + random.randint(-5, 15)
                timer_session = TimerSession(
                    account_id=account.id,
                    task_id=task.id,
                    duration_seconds=estimated_minutes * 60,
                    actual_seconds=actual_minutes * 60,
                    status="completed",
                    started_at=task.completed_at - timedelta(minutes=actual_minutes),
                    completed_at=task.completed_at
                )
                db.add(timer_session)
                generated_count["timer_sessions"] += 1
                
                # Update task with actual time
                task.actual_minutes = actual_minutes
                if estimated_minutes > 0:
                    task.completion_accuracy = actual_minutes / estimated_minutes
                generated_count["completions"] += 1
        
        # Generate schedule for some days (60% of days)
        if random.random() < 0.6:
            schedule = Schedule(
                account_id=account.id,
                date=day_date,
                schedule_type="daily",
                optimization_score=0.7 + random.uniform(0, 0.3),
                optimization_context={
                    "energy": 0.6 + random.uniform(-0.2, 0.2),
                    "stress": 0.3 + random.uniform(-0.1, 0.2)
                }
            )
            db.add(schedule)
            db.flush()
            generated_count["schedules"] += 1
    
    db.commit()
    
    # Log generation
    log = SystemLog(
        level="INFO",
        component="admin",
        message=f"Generated {days} days of simulated data",
        context_data={
            "days": days,
            "generated_by": current_user.id,
            "counts": generated_count
        }
    )
    db.add(log)
    db.commit()
    
    return {
        "message": f"Generated {days} days of simulated data",
        "days": days,
        "generated": generated_count
    }
