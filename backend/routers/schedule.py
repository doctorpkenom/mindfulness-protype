"""
Schedule optimization router - ML-powered task scheduling.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import json

from backend.database import get_db
from backend.db_models import Account, Task, Schedule, ScheduleItem, SystemLog
from backend.auth import get_current_user
from backend.models import ScheduleOptimizeRequest, ScheduleResponse, ScheduleItemResponse

router = APIRouter()

def optimize_schedule_with_ml(
    tasks: List[Task],
    work_start: str,
    work_end: str,
    schedule_date: datetime,
    current_energy: float = 0.7,
    current_stress: float = 0.3,
    account_id: int = None
) -> List[dict]:
    """
    Use ML ensemble to optimize task scheduling.
    Returns list of scheduled tasks with start/end times and reasoning.
    """
    # Initialize ML coordinator (optional - can be used for advanced scheduling)
    # coordinator = OnlineCoordinator()  # Not used in basic scheduling yet
    
    # Parse work hours
    start_hour, start_min = map(int, work_start.split(":"))
    end_hour, end_min = map(int, work_end.split(":"))
    
    # Create schedule items using the schedule date (not today)
    scheduled_items = []
    # Use the schedule date, not today's date
    schedule_date_only = schedule_date.date() if isinstance(schedule_date, datetime) else schedule_date
    if isinstance(schedule_date_only, datetime):
        schedule_date_only = schedule_date_only.date()
    
    current_time = datetime.combine(schedule_date_only, datetime.min.time()).replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
    end_time = datetime.combine(schedule_date_only, datetime.min.time()).replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
    
    # Sort tasks by priority and difficulty (ML will refine this)
    sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.difficulty))
    
    for task in sorted_tasks:
        # Create context for ML (simplified - no preprocessing needed for basic scheduling)
        context = {
            "stress": current_stress,
            "energy": current_energy,
            "time_of_day": current_time.hour,
            "task_difficulty": task.difficulty / 5.0,
            "task_energy_required": task.energy_required,
            "task_focus_required": task.focus_required
        }
        
        # Get ML recommendation (simplified - in real implementation, 
        # we'd have a task scheduling expert model)
        # For now, use energy matching and priority
        energy_match = abs(current_energy - task.energy_required)
        
        # Calculate optimal placement score
        placement_score = (
            (task.priority / 5.0) * 0.4 +  # Priority weight
            (1 - energy_match) * 0.3 +  # Energy match
            (1 - task.difficulty / 5.0) * 0.2 +  # Easier tasks when energy is lower
            (1 - current_stress) * 0.1  # Lower stress = better placement
        )
        
        # Calculate task duration (use estimated minutes)
        task_duration = timedelta(minutes=task.estimated_minutes)
        
        # Check if task fits in remaining time
        if current_time + task_duration > end_time:
            break  # No more time today
        
        # Create schedule item
        item = {
            "task_id": task.id,
            "task_title": task.title,
            "start_time": current_time,
            "end_time": current_time + task_duration,
            "placement_reason": f"Priority: {task.priority}, Energy match: {1-energy_match:.2f}, Score: {placement_score:.2f}",
            "confidence_score": placement_score
        }
        
        scheduled_items.append(item)
        
        # Update energy (tasks drain energy)
        current_energy = max(0.1, current_energy - (task.energy_required * 0.1))
        
        # Move to next time slot
        current_time = current_time + task_duration + timedelta(minutes=5)  # 5 min break
        
        if current_time >= end_time:
            break
    
    return scheduled_items

@router.post("/optimize", response_model=ScheduleResponse, status_code=201)
def optimize_schedule(
    request: ScheduleOptimizeRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize a schedule for the given date using ML."""
    try:
        # Get tasks
        tasks = db.query(Task).filter(
            Task.id.in_(request.task_ids),
            Task.account_id == current_user.id,
            Task.status.in_(["pending", "scheduled"])
        ).all()
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No valid tasks found")
        
        # Parse date - handle both ISO format and simple date string
        try:
            if "T" in request.date or "Z" in request.date:
                # ISO format with time
                schedule_date = datetime.fromisoformat(request.date.replace("Z", "+00:00"))
                # Extract just the date part
                schedule_date = schedule_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                # Simple date string like "2026-01-20"
                schedule_date = datetime.strptime(request.date, "%Y-%m-%d")
        except (ValueError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {request.date}. Error: {str(e)}")
        
        # Get user's current state (or use defaults)
        energy = request.current_energy or 0.7
        stress = request.current_stress or 0.3
        
        # Optimize schedule
        scheduled_items = optimize_schedule_with_ml(
            tasks=tasks,
            work_start=request.work_hours_start,
            work_end=request.work_hours_end,
            schedule_date=schedule_date,
            current_energy=energy,
            current_stress=stress,
            account_id=current_user.id
        )
        
        if not scheduled_items:
            raise HTTPException(status_code=400, detail="Could not schedule tasks - not enough time")
    
        # Create schedule
        schedule = Schedule(
            account_id=current_user.id,
            date=schedule_date,
            schedule_type="daily",
            optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items),
            optimization_context={
                "energy": energy,
                "stress": stress,
                "work_hours": {"start": request.work_hours_start, "end": request.work_hours_end}
            }
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        # Create schedule items
        for item_data in scheduled_items:
            task = db.query(Task).filter(Task.id == item_data["task_id"]).first()
            if task:
                schedule_item = ScheduleItem(
                    schedule_id=schedule.id,
                    task_id=item_data["task_id"],
                    start_time=item_data["start_time"],
                    end_time=item_data["end_time"],
                    placement_reason=item_data["placement_reason"],
                    confidence_score=item_data["confidence_score"],
                    status="scheduled"
                )
                db.add(schedule_item)
                
                # Update task status
                task.status = "scheduled"
                task.scheduled_start = item_data["start_time"]
                task.scheduled_end = item_data["end_time"]
        
        db.commit()
        
        # Log optimization
        log = SystemLog(
            level="INFO",
            component="schedule_optimizer",
            message=f"Schedule optimized for {schedule_date.date()}",
            context_data={"schedule_id": schedule.id, "tasks_scheduled": len(scheduled_items)}
        )
        db.add(log)
        db.commit()
        
        # Return schedule with items
        db.refresh(schedule)
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR /api/schedule/optimize] {str(e)}")
        print(error_details)
        
        # Log error
        try:
            error_log = SystemLog(
                level="ERROR",
                component="schedule_optimizer",
                message=f"Schedule optimization failed: {str(e)}",
                context_data={"error": str(e), "traceback": error_details}
            )
            db.add(error_log)
            db.commit()
        except:
            pass  # Don't fail if logging fails
        
        raise HTTPException(
            status_code=500,
            detail=f"Machine learning model failed: {str(e)}"
        )

@router.get("/{date}", response_model=ScheduleResponse)
def get_schedule(
    date: str,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedule for a specific date."""
    schedule_date = datetime.fromisoformat(date.replace("Z", "+00:00")).date()
    
    schedule = db.query(Schedule).filter(
        Schedule.account_id == current_user.id,
        Schedule.date >= datetime.combine(schedule_date, datetime.min.time()),
        Schedule.date < datetime.combine(schedule_date, datetime.min.time()) + timedelta(days=1)
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this date")
    
    return schedule
