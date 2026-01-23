"""
SIMPLIFIED single-day schedule optimizer using advanced ML models.
No multi-day, no recurring expansion - just one perfect day.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import get_db
from backend.db_models import Account, Task, Schedule, ScheduleItem, SystemLog
from backend.auth import get_current_user
from backend.models import ScheduleOptimizeRequest, ScheduleResponse, ScheduleItemResponse

router = APIRouter()

def optimize_schedule_simple(
    tasks: List[Task],
    work_start: str,
    work_end: str,
    schedule_date: datetime,
    current_energy: float = 0.7,
    current_stress: float = 0.3,
    account_id: int = None,
    db: Session = None
) -> List[dict]:
    """
    SIMPLIFIED: Single-day ML-powered task scheduling.
    Uses advanced ScheduleOptimizer with research-backed insights.
    NO recurring expansion, NO multi-day - just schedule today's tasks perfectly.
    """
    # Filter out completed tasks
    tasks = [t for t in tasks if t.status in ["pending", "scheduled"]]
    
    if not tasks:
        return []
    
    # Load research data
    research_metadata = None
    try:
        from processor.research_metadata import ResearchMetadata
        research_metadata = ResearchMetadata
    except Exception as e:
        print(f"[WARNING] Could not load research data: {e}")
    
    # Initialize advanced ML optimizer
    from ml.models.schedule_optimizer import ScheduleOptimizer
    optimizer = ScheduleOptimizer()
    
    # Parse work hours
    work_start_hour, work_start_min = map(int, work_start.split(":"))
    work_end_hour, work_end_min = map(int, work_end.split(":"))
    
    schedule_date_only = schedule_date.date()
    work_start_time = datetime.combine(schedule_date_only, datetime.min.time().replace(hour=work_start_hour, minute=work_start_min))
    work_end_time = datetime.combine(schedule_date_only, datetime.min.time().replace(hour=work_end_hour, minute=work_end_min))
    
    # Create time slots (15-minute intervals)
    current_time = work_start_time
    time_slots = []
    while current_time < work_end_time:
        slot_end = min(current_time + timedelta(minutes=15), work_end_time)
        time_slots.append({
            "start": current_time,
            "end": slot_end,
            "hour": current_time.hour,
            "energy": current_energy,  # Energy decreases over time
            "stress": current_stress   # Stress increases over time
        })
        current_time = slot_end
    
    # Convert tasks to dict format for optimizer
    task_dicts = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "category": task.category or "personal",
            "tags": task.tags or [],
            "priority": task.priority,
            "difficulty": task.difficulty,
            "energy_required": task.energy_required or 0.5,
            "focus_required": task.focus_required or 0.5,
            "estimated_minutes": task.estimated_minutes,
            "deadline": task.deadline,
            "recurrence_pattern": task.recurrence_pattern
        }
        task_dicts.append(task_dict)
    
    # Schedule tasks using greedy algorithm with ML scoring
    scheduled_items = []
    scheduled_task_ids = set()
    current_slot_idx = 0
    
    # Sort tasks by priority and deadline
    def task_priority(task_dict):
        priority_score = task_dict["priority"] / 5.0
        if task_dict.get("deadline"):
            try:
                deadline = task_dict["deadline"]
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                if isinstance(deadline, datetime):
                    days_until = (deadline.date() - schedule_date_only).days
                    if days_until < 0:
                        priority_score += 10.0  # Overdue
                    elif days_until == 0:
                        priority_score += 5.0  # Due today
                    elif days_until <= 1:
                        priority_score += 2.0  # Due tomorrow
            except:
                pass
        return -priority_score  # Negative for descending sort
    
    sorted_tasks = sorted(task_dicts, key=task_priority)
    
    # Schedule each task
    for task_dict in sorted_tasks:
        if task_dict["id"] in scheduled_task_ids:
            continue
        
        task_minutes = task_dict["estimated_minutes"]
        best_slot_idx = None
        best_score = -1.0
        best_reasoning = []
        
        # Find best time slot for this task
        for slot_idx, slot in enumerate(time_slots):
            # Check if task fits in this slot
            slot_start = slot["start"]
            slot_end = slot["end"]
            task_end = slot_start + timedelta(minutes=task_minutes)
            
            if task_end > work_end_time:
                continue  # Task doesn't fit
            
            # Check if this slot is already taken
            slot_taken = False
            for scheduled in scheduled_items:
                scheduled_start = scheduled["start_time"]
                scheduled_end = scheduled["end_time"]
                if isinstance(scheduled_start, str):
                    scheduled_start = datetime.fromisoformat(scheduled_start.replace("Z", "+00:00"))
                if isinstance(scheduled_end, str):
                    scheduled_end = datetime.fromisoformat(scheduled_end.replace("Z", "+00:00"))
                
                # Check for overlap
                if not (task_end <= scheduled_start or slot_start >= scheduled_end):
                    slot_taken = True
                    break
            
            if slot_taken:
                continue
            
            # Score this slot using advanced ML optimizer
            slot_hour = slot["hour"]
            slot_energy = slot["energy"]
            slot_stress = slot["stress"]
            
            score, reasoning = optimizer.score_task_for_slot(
                task_dict, slot_hour, slot_energy, slot_stress, research_metadata
            )
            
            # STRICT time enforcement
            title_lower = (task_dict["title"] or "").lower()
            tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task_dict.get("tags") or [])]
            
            # Morning tasks MUST be in morning
            if any(kw in title_lower for kw in ["breakfast", "morning", "meditation", "yoga", "exercise"]) or "morning" in tags:
                if not (6 <= slot_hour < 12):
                    score = -1.0  # Reject
                    reasoning.append("REJECTED: Morning task in wrong time")
            
            # Evening tasks MUST be in evening
            if any(kw in title_lower for kw in ["dinner", "supper", "cook", "prep"]) or "evening" in tags:
                if not (17 <= slot_hour < 22):
                    score = -1.0  # Reject
                    reasoning.append("REJECTED: Evening task in wrong time")
            
            if score > best_score:
                best_score = score
                best_slot_idx = slot_idx
                best_reasoning = reasoning
        
        # Schedule task in best slot
        if best_slot_idx is not None and best_score > 0:
            slot = time_slots[best_slot_idx]
            task_start = slot["start"]
            task_end = task_start + timedelta(minutes=task_minutes)
            
            scheduled_items.append({
                "task_id": task_dict["id"],
                "task_title": task_dict["title"],
                "start_time": task_start,
                "end_time": task_end,
                "placement_reason": f"ML Score: {best_score:.2f} | " + " | ".join(best_reasoning[:3]),
                "confidence_score": best_score
            })
            
            scheduled_task_ids.add(task_dict["id"])
            
            # Mark slots as taken
            for i in range(best_slot_idx, len(time_slots)):
                slot_end_time = time_slots[i]["end"]
                if slot_end_time <= task_end:
                    time_slots[i]["taken"] = True
    
    return scheduled_items

@router.post("/optimize-simple", response_model=ScheduleResponse, status_code=201)
def optimize_schedule_simple_endpoint(
    request: ScheduleOptimizeRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simplified single-day schedule optimization."""
    try:
        # Get tasks
        tasks = db.query(Task).filter(
            Task.id.in_(request.task_ids),
            Task.account_id == current_user.id,
            Task.status.in_(["pending", "scheduled"])
        ).all()
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No valid tasks found")
        
        # Parse date
        try:
            if "T" in request.date or "Z" in request.date:
                schedule_date = datetime.fromisoformat(request.date.replace("Z", "+00:00"))
                schedule_date = schedule_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                schedule_date = datetime.strptime(request.date, "%Y-%m-%d")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        
        # Get user state (defaults)
        energy = 0.7
        stress = 0.3
        
        # Optimize schedule (SINGLE DAY ONLY)
        scheduled_items = optimize_schedule_simple(
            tasks=tasks,
            work_start=request.work_hours_start,
            work_end=request.work_hours_end,
            schedule_date=schedule_date,
            current_energy=energy,
            current_stress=stress,
            account_id=current_user.id,
            db=db
        )
        
        if not scheduled_items:
            raise HTTPException(status_code=400, detail="No tasks could be scheduled")
        
        # Create or update schedule
        schedule = db.query(Schedule).filter(
            Schedule.account_id == current_user.id,
            Schedule.date >= datetime.combine(schedule_date.date(), datetime.min.time()),
            Schedule.date < datetime.combine(schedule_date.date(), datetime.min.time()) + timedelta(days=1)
        ).first()
        
        if not schedule:
            schedule = Schedule(
                account_id=current_user.id,
                date=schedule_date,
                schedule_type="daily",
                optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items),
                optimization_context={
                    "energy": energy,
                    "stress": stress,
                    "work_hours": {"start": request.work_hours_start, "end": request.work_hours_end},
                    "method": "simple_ml"
                }
            )
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
        else:
            # Clear old items
            db.query(ScheduleItem).filter(ScheduleItem.schedule_id == schedule.id).delete()
            schedule.optimization_score = sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items)
            db.commit()
        
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
                task.status = "scheduled"
                task.scheduled_start = item_data["start_time"]
                task.scheduled_end = item_data["end_time"]
        
        db.commit()
        
        # Return schedule
        from sqlalchemy.orm import joinedload
        schedule = db.query(Schedule).options(
            joinedload(Schedule.items).joinedload(ScheduleItem.task)
        ).filter(Schedule.id == schedule.id).first()
        
        item_responses = []
        for item in schedule.items:
            task_title = item.task.title if item.task else "Unknown Task"
            item_responses.append(ScheduleItemResponse(
                id=item.id,
                task_id=item.task_id,
                task_title=task_title,
                start_time=item.start_time,
                end_time=item.end_time,
                placement_reason=item.placement_reason,
                confidence_score=item.confidence_score,
                status=item.status
            ))
        
        return ScheduleResponse(
            id=schedule.id,
            date=schedule.date,
            schedule_type=schedule.schedule_type,
            optimization_score=schedule.optimization_score,
            items=item_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Schedule optimization failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Schedule optimization error: {str(e)}")
