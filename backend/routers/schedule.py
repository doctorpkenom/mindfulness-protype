"""
Schedule optimization router - ML-powered task scheduling.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
import sys
import os

# Add project root to path for ML imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import get_db
from backend.db_models import Account, Task, Schedule, ScheduleItem, SystemLog, UserMLWeights
from backend.auth import get_current_user
from backend.models import ScheduleOptimizeRequest, ScheduleResponse, ScheduleItemResponse

router = APIRouter()

# Chunking system removed - tasks are scheduled as single blocks

def infer_appropriate_time_slot(task: Task) -> dict:
    """
    Intelligently infer appropriate time slots for a task based on:
    - Task title (keywords like "breakfast", "dinner", "morning", "evening")
    - Category (work, personal, health, daily)
    - Tags
    - Task type patterns
    
    Returns: dict with "preferred_hours" (list of hour ranges) and "penalty_hours" (list of hour ranges to avoid)
    """
    title_lower = (task.title or "").lower()
    category_lower = (task.category or "").lower()
    tags = [tag.lower() if isinstance(tag, str) else str(tag).lower() for tag in (task.tags or [])]
    
    preferred_hours = []  # List of (start_hour, end_hour) tuples
    penalty_hours = []    # Hours to heavily penalize
    
    # Morning tasks (6 AM - 12 PM) - CHECK FIRST to prevent conflicts
    # These tasks MUST be in the morning, never in evening
    morning_keywords = ["breakfast", "morning", "wake", "coffee", "meditation", "yoga", "exercise", "workout", "gym", "run", "jog"]
    has_morning_keyword = any(kw in title_lower for kw in morning_keywords)
    has_morning_tag = "morning" in tags
    
    # STRICT: If it's a morning task, MUST be in morning hours
    if has_morning_keyword or has_morning_tag:
        preferred_hours = [(6, 12)]  # 6 AM - 12 PM ONLY
        penalty_hours = [(12, 24)]  # HEAVILY penalize anything after 12 PM
        # Don't check other keywords if it's clearly a morning task
        print(f"[TIME_INFERENCE] Task '{task.title}' detected as morning task - forcing morning (6-12), penalizing (12-24)")
        return {
            "preferred_hours": preferred_hours,
            "penalty_hours": penalty_hours
        }
    
    # Afternoon tasks (12 PM - 5 PM)
    afternoon_keywords = ["lunch", "afternoon", "meeting", "call", "conference"]
    if any(kw in title_lower for kw in afternoon_keywords) or "afternoon" in tags:
        preferred_hours.append((12, 17))
        penalty_hours.extend([(6, 12), (17, 22)])  # Penalize morning/evening
    
    # Evening tasks (5 PM - 10 PM) - CHECK FIRST for meal prep tasks
    # Check for dinner/cooking keywords FIRST before other checks
    # Use word boundary matching to catch "dinner prep", "dinner preparation", etc.
    dinner_keywords = ["dinner", "supper"]
    cooking_keywords = ["cook", "cooking", "meal prep", "meal preparation", "dinner prep", "dinner preparation", "prep"]
    
    # Check if title contains dinner or cooking keywords
    has_dinner = any(kw in title_lower for kw in dinner_keywords)
    has_cooking = any(kw in title_lower for kw in cooking_keywords)
    
    # Also check tags for evening/cooking indicators
    has_evening_tag = "evening" in tags or "cooking" in tags
    
    # If it has "prep" and is in daily category or has cooking tag, it's likely dinner prep
    has_prep = "prep" in title_lower or "preparation" in title_lower
    is_daily_cooking = (has_prep or has_cooking) and category_lower == "daily"
    
    # STRICT: If it's dinner/cooking related, MUST be evening
    if has_dinner or (has_cooking and has_evening_tag) or is_daily_cooking or (has_prep and "dinner" in title_lower):
        preferred_hours = [(17, 21)]  # 5 PM - 9 PM ONLY
        penalty_hours = [(0, 17), (21, 24)]  # HEAVILY penalize anything before 5 PM or after 9 PM
        # Don't check other keywords if it's clearly a dinner/cooking task
        print(f"[TIME_INFERENCE] Task '{task.title}' detected as dinner/cooking - forcing evening (17-21), penalizing (0-17)")
        return {
            "preferred_hours": preferred_hours,
            "penalty_hours": penalty_hours
        }
    
    evening_keywords = ["evening", "night"]
    if any(kw in title_lower for kw in evening_keywords) or "evening" in tags:
        preferred_hours.append((17, 22))
        penalty_hours.extend([(6, 12), (12, 17)])  # Penalize morning/afternoon
    
    # Work tasks - prefer business hours (9 AM - 5 PM)
    work_keywords = ["work", "project", "code", "develop", "meeting", "call", "email", "report", "presentation", "deadline"]
    if category_lower == "work" or any(kw in title_lower for kw in work_keywords):
        preferred_hours.append((9, 17))
        penalty_hours.extend([(6, 9), (17, 22)])  # Penalize early morning/late evening
    
    # Personal/health tasks - more flexible but avoid work hours
    if category_lower in ["personal", "health", "daily"]:
        # Personal tasks can be morning or evening, but not during peak work hours
        if "morning" not in title_lower and "evening" not in title_lower and "dinner" not in title_lower:
            preferred_hours.extend([(6, 9), (17, 22)])  # Early morning or evening
            penalty_hours.append((9, 17))  # Avoid work hours
    
    # Meal-related tasks - check for meal keywords (but skip if already handled by dinner check above)
    # Only process if we haven't already set preferred hours from dinner check
    if not preferred_hours or len([h for h in preferred_hours if h[0] >= 17]) == 0:
        meal_keywords = ["breakfast", "lunch", "supper", "meal", "eat"]
        for kw in meal_keywords:
            if kw in title_lower:
                if kw in ["breakfast", "coffee"]:
                    preferred_hours.append((6, 10))
                    penalty_hours.extend([(10, 17), (17, 22)])
                elif kw in ["lunch"]:
                    preferred_hours.append((11, 14))
                    penalty_hours.extend([(6, 11), (14, 22)])
                elif kw in ["supper"]:
                    preferred_hours.append((17, 21))
                    penalty_hours.extend([(6, 17)])
    
    # Chores/household tasks - prefer morning or evening, not work hours
    chore_keywords = ["clean", "laundry", "dishes", "vacuum", "organize", "tidy", "grocery", "shopping"]
    if any(kw in title_lower for kw in chore_keywords) or category_lower == "daily":
        if not preferred_hours:  # Only if no other preferences set
            preferred_hours.extend([(6, 9), (17, 22)])
            penalty_hours.append((9, 17))
    
    # Check for preferred_time tag
    for tag in tags:
        if tag.startswith("preferred_time:"):
            try:
                time_str = tag.split(":", 1)[1]
                hour = int(time_str.split(":")[0])
                preferred_hours.append((max(0, hour - 1), min(23, hour + 2)))  # ±1 hour window
            except:
                pass
    
    return {
        "preferred_hours": preferred_hours,
        "penalty_hours": penalty_hours
    }

def expand_recurring_tasks(tasks: List[Task], start_date: datetime, days_ahead: int) -> List[dict]:
    """
    Expand recurring tasks across multiple days based on their recurrence pattern.
    Returns a list of task dicts with expanded instances for each day.
    """
    expanded_tasks = []
    start_date_only = start_date.date()
    end_date = start_date_only + timedelta(days=days_ahead - 1)
    
    for task in tasks:
        base_task = {
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
            "recurrence_pattern": task.recurrence_pattern,
            "recurrence_end_date": task.recurrence_end_date,
            "custom_recurrence_days": task.custom_recurrence_days
        }
        
        # Check if task has recurrence pattern
        if task.recurrence_pattern and task.recurrence_pattern != "none":
            # Check if recurrence has ended
            if task.recurrence_end_date and task.recurrence_end_date.date() < start_date_only:
                continue  # Skip tasks whose recurrence has ended
            
            # Expand based on recurrence pattern
            current_date = start_date_only
            day_offset = 0
            
            while current_date <= end_date:
                # Check if recurrence has ended for this instance
                if task.recurrence_end_date and current_date > task.recurrence_end_date.date():
                    break
                
                should_include = False
                
                if task.recurrence_pattern == "daily":
                    should_include = True
                elif task.recurrence_pattern == "weekly":
                    # Weekly: same day of week as the start date
                    # For simplicity, schedule weekly tasks on the same weekday as start_date
                    start_weekday = start_date_only.weekday()  # 0=Monday, 6=Sunday
                    current_weekday = current_date.weekday()
                    if current_weekday == start_weekday:
                        should_include = True
                elif task.recurrence_pattern == "monthly":
                    # Monthly: same day of month (simplified - every 30 days)
                    if day_offset == 0 or day_offset % 30 == 0:
                        should_include = True
                elif task.recurrence_pattern == "custom" and task.custom_recurrence_days:
                    # Custom: every N days
                    if day_offset == 0 or day_offset % task.custom_recurrence_days == 0:
                        should_include = True
                
                if should_include:
                    task_instance = base_task.copy()
                    task_instance["target_date"] = current_date
                    task_instance["original_task_id"] = task.id
                    expanded_tasks.append(task_instance)
                
                current_date += timedelta(days=1)
                day_offset += 1
        else:
            # Non-recurring task - schedule on appropriate day
            task_instance = base_task.copy()
            
            # If task has deadline, schedule it on the deadline day (or first day if deadline passed)
            if task.deadline:
                try:
                    deadline_date = task.deadline.date() if isinstance(task.deadline, datetime) else datetime.fromisoformat(str(task.deadline).replace("Z", "+00:00")).date()
                    if start_date_only <= deadline_date <= end_date:
                        task_instance["target_date"] = deadline_date
                    elif deadline_date < start_date_only:
                        task_instance["target_date"] = start_date_only  # Overdue - schedule ASAP
                    else:
                        # Deadline is after the week - schedule on first day
                        task_instance["target_date"] = start_date_only
                except:
                    task_instance["target_date"] = start_date_only
            else:
                # No deadline - schedule on first day (will be optimized by ML across the week)
                task_instance["target_date"] = start_date_only
            
            task_instance["original_task_id"] = task.id
            expanded_tasks.append(task_instance)
    
    return expanded_tasks

def optimize_schedule_with_ml(
    tasks: List[Task],
    work_start: str,
    work_end: str,
    schedule_date: datetime,
    current_energy: float = 0.7,
    current_stress: float = 0.3,
    account_id: int = None,
    db: Session = None,
    days_ahead: int = 7
) -> List[dict]:
    """
    MULTI-DAY ML-powered task scheduling with recurring task expansion.
    Uses advanced ScheduleOptimizer with 32+ features and research-backed insights.
    Expands recurring tasks across the week and finds optimal slots for each.
    """
    # Filter completed tasks
    tasks = [t for t in tasks if t.status in ["pending", "scheduled"]]
    if not tasks:
        return []
    
    # Load advanced ML optimizer
    from ml.models.schedule_optimizer import ScheduleOptimizer
    optimizer = ScheduleOptimizer()
    
    # Load research data
    research_metadata = None
    try:
        from processor.research_metadata import ResearchMetadata
        research_metadata = ResearchMetadata
    except Exception as e:
        print(f"[WARNING] Could not load research data: {e}")
    
    # Parse work hours
    work_start_hour, work_start_min = map(int, work_start.split(":"))
    work_end_hour, work_end_min = map(int, work_end.split(":"))
    
    schedule_date_only = schedule_date.date()
    end_date = schedule_date_only + timedelta(days=days_ahead - 1)
    
    # Expand recurring tasks across the week
    task_dicts = expand_recurring_tasks(tasks, schedule_date, days_ahead)
    
    if not task_dicts:
        return []
    
    # Sort by priority and deadline urgency (considering target_date)
    def task_priority(task_dict):
        score = task_dict["priority"] / 5.0
        target_date = task_dict.get("target_date", schedule_date_only)
        
        # Prioritize tasks for earlier days
        days_from_start = (target_date - schedule_date_only).days
        score += (days_ahead - days_from_start) * 0.5  # Earlier days get higher priority
        
        if task_dict.get("deadline"):
            try:
                deadline = task_dict["deadline"]
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                if isinstance(deadline, datetime):
                    deadline_date = deadline.date() if isinstance(deadline, datetime) else deadline
                    days_until = (deadline_date - target_date).days
                    if days_until < 0:
                        score += 10.0  # Overdue
                    elif days_until == 0:
                        score += 5.0  # Due today
                    elif days_until <= 1:
                        score += 2.0  # Due tomorrow
            except:
                pass
        return -score  # Negative for descending
    
    sorted_tasks = sorted(task_dicts, key=task_priority)
    
    # OPTIMAL SLOT FINDING: For each task, find the best time slot across all days
    scheduled_items = []
    scheduled_slots = []  # List of (start_time, end_time) tuples for conflict detection
    scheduled_per_day = {}  # Track scheduled tasks per day to avoid duplicates
    
    # Track energy/stress throughout each day (resets per day)
    def get_energy_at_time(date: datetime.date, hour: int, base_energy: float, scheduled_tasks: List[dict]) -> float:
        """Estimate energy at a given date/hour based on scheduled tasks for that day."""
        energy = base_energy
        for task in scheduled_tasks:
            task_date = task["start_time"].date()
            task_hour = task["start_time"].hour
            # Only consider tasks on the same day
            if task_date == date and task_hour < hour:
                # Energy decreases after each task
                energy = max(0.1, energy - (task.get("energy_cost", 0.1)))
        return energy
    
    def get_stress_at_time(date: datetime.date, hour: int, base_stress: float, scheduled_tasks: List[dict]) -> float:
        """Estimate stress at a given date/hour based on scheduled tasks for that day."""
        stress = base_stress
        for task in scheduled_tasks:
            task_date = task["start_time"].date()
            task_hour = task["start_time"].hour
            # Only consider tasks on the same day
            if task_date == date and task_hour < hour:
                # Stress increases slightly after each task
                stress = min(1.0, stress + 0.03)
        return stress
    
    def has_conflict(start_time: datetime, end_time: datetime, scheduled_slots: List[tuple], break_minutes: int = 5) -> bool:
        """Check if this time slot conflicts with already scheduled tasks (with break buffer)."""
        for slot_start, slot_end in scheduled_slots:
            # Add break buffer - tasks need at least 5 minutes between them
            buffer_start = start_time - timedelta(minutes=break_minutes)
            buffer_end = end_time + timedelta(minutes=break_minutes)
            # Check for overlap (with buffer)
            if not (buffer_end <= slot_start or buffer_start >= slot_end):
                return True
        return False
    
    # For each task, find the BEST time slot across all days
    for task_dict in sorted_tasks:
        target_date = task_dict.get("target_date", schedule_date_only)
        original_task_id = task_dict.get("original_task_id", task_dict["id"])
        is_recurring = task_dict.get("recurrence_pattern") and task_dict.get("recurrence_pattern") != "none"
        
        # Skip if we've already scheduled this original task on this day (for recurring tasks)
        day_key = (original_task_id, target_date)
        if day_key in scheduled_per_day:
            continue
        
        task_minutes = task_dict["estimated_minutes"]
        title_lower = (task_dict["title"] or "").lower()
        tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task_dict.get("tags") or [])]
        
        # Determine time constraints for this task
        must_be_morning = any(kw in title_lower for kw in ["breakfast", "morning", "meditation", "yoga", "exercise", "wake", "coffee", "journal"]) or "morning" in tags
        must_be_evening = any(kw in title_lower for kw in ["dinner", "supper", "cook", "prep", "preparation", "meal prep"]) or "evening" in tags
        must_be_afternoon = any(kw in title_lower for kw in ["lunch", "afternoon", "meeting"]) or "afternoon" in tags
        
        # Determine which days to try scheduling on
        # For recurring tasks, only try the target_date
        # For non-recurring tasks, try all days in the week to find the best slot
        if is_recurring:
            days_to_try = [target_date]
        else:
            # Try all days in the week for non-recurring tasks
            days_to_try = []
            current_date = schedule_date_only
            while current_date <= end_date:
                days_to_try.append(current_date)
                current_date += timedelta(days=1)
        
        # Find best slot by trying multiple time windows across eligible days
        best_slot = None
        best_score = -1.0
        best_reasoning = []
        best_date = None
        
        for try_date in days_to_try:
            # Skip if we've already scheduled this task on this day
            try_day_key = (original_task_id, try_date)
            if try_day_key in scheduled_per_day:
                continue
            
            # Get day boundaries for this date
            day_start = datetime.combine(try_date, datetime.min.time().replace(hour=work_start_hour, minute=work_start_min))
            day_end = datetime.combine(try_date, datetime.min.time().replace(hour=work_end_hour, minute=work_end_min))
            
            # Try slots throughout the day (every 30 minutes)
            test_time = day_start
            while test_time < day_end:
                task_end_time = test_time + timedelta(minutes=task_minutes)
                
                # Check if task fits
                if task_end_time > day_end:
                    test_time += timedelta(minutes=30)
                    continue
                
                # Check time constraints
                slot_hour = test_time.hour
                if must_be_morning and not (6 <= slot_hour < 12):
                    test_time += timedelta(minutes=30)
                    continue
                if must_be_evening and not (17 <= slot_hour < 22):
                    test_time += timedelta(minutes=30)
                    continue
                if must_be_afternoon and not (12 <= slot_hour < 17):
                    test_time += timedelta(minutes=30)
                    continue
                
                # Check for conflicts (with 5-minute break buffer)
                if has_conflict(test_time, task_end_time, scheduled_slots, break_minutes=5):
                    test_time += timedelta(minutes=30)
                    continue
                
                # Get energy/stress at this time (for this specific day)
                slot_energy = get_energy_at_time(try_date, slot_hour, current_energy, scheduled_items)
                slot_stress = get_stress_at_time(try_date, slot_hour, current_stress, scheduled_items)
                
                # Score this slot
                score, reasoning = optimizer.score_task_for_slot(
                    task_dict, slot_hour, slot_energy, slot_stress, research_metadata
                )
                
                # Only consider slots with positive scores
                if score > 0 and score > best_score:
                    best_slot = (test_time, task_end_time)
                    best_score = score
                    best_reasoning = reasoning
                    best_date = try_date
                
                test_time += timedelta(minutes=30)  # Try next 30-minute window
        
        # Schedule the task in the best slot found
        if best_slot and best_score > 0.1:  # Minimum threshold
            start_time, end_time = best_slot
            scheduled_items.append({
                "task_id": original_task_id,  # Use original task ID
                "task_title": task_dict["title"],
                "start_time": start_time,
                "end_time": end_time,
                "placement_reason": f"ML Score: {best_score:.2f} | " + " | ".join(best_reasoning[:3]),
                "confidence_score": best_score,
                "energy_cost": task_dict["energy_required"] * 0.1
            })
            
            scheduled_slots.append((start_time, end_time))
            # Mark this task as scheduled for the day it was actually scheduled on
            scheduled_per_day[(original_task_id, best_date)] = True
    
    # Sort scheduled items by start time
    scheduled_items.sort(key=lambda x: x["start_time"])
    
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
        
        # Parse date
        try:
            if "T" in request.date or "Z" in request.date:
                schedule_date = datetime.fromisoformat(request.date.replace("Z", "+00:00"))
                schedule_date = schedule_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                schedule_date = datetime.strptime(request.date, "%Y-%m-%d")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        
        # Get user state
        energy = request.current_energy or 0.7
        stress = request.current_stress or 0.3
        
        # Optimize schedule (MULTI-DAY with recurring tasks - full week)
        days_ahead = 7  # Schedule for a full week to handle recurring tasks
        
        scheduled_items = optimize_schedule_with_ml(
            tasks=tasks,
            work_start=request.work_hours_start,
            work_end=request.work_hours_end,
            schedule_date=schedule_date,
            current_energy=energy,
            current_stress=stress,
            account_id=current_user.id,
            db=db,
            days_ahead=days_ahead  # Full week scheduling
        )
        
        if not scheduled_items:
            raise HTTPException(status_code=400, detail="No tasks could be scheduled")
        
        # Determine schedule type based on date range
        dates = set()
        for item in scheduled_items:
            if item.get("start_time"):
                try:
                    if isinstance(item["start_time"], str):
                        item_date = datetime.fromisoformat(item["start_time"].replace("Z", "+00:00"))
                    else:
                        item_date = item["start_time"]
                    dates.add(item_date.date())
                except:
                    pass
        
        schedule_type = "weekly" if len(dates) > 1 else "daily"
        
        # Create or update schedule
        if schedule_type == "weekly":
            # For weekly schedules, find schedule that covers the date range
            min_date = min(dates) if dates else schedule_date.date()
            max_date = max(dates) if dates else schedule_date.date()
            schedule = db.query(Schedule).filter(
                Schedule.account_id == current_user.id,
                Schedule.date >= datetime.combine(min_date, datetime.min.time()),
                Schedule.date <= datetime.combine(max_date, datetime.min.time()),
                Schedule.schedule_type == "weekly"
            ).first()
        else:
            # For daily schedules, look for exact date
            schedule = db.query(Schedule).filter(
                Schedule.account_id == current_user.id,
                Schedule.date >= datetime.combine(schedule_date.date(), datetime.min.time()),
                Schedule.date < datetime.combine(schedule_date.date(), datetime.min.time()) + timedelta(days=1)
            ).first()
        
        if not schedule:
            schedule = Schedule(
                account_id=current_user.id,
                date=schedule_date,
                schedule_type=schedule_type,
                optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else 0.0,
                optimization_context={
                    "energy": energy,
                    "stress": stress,
                    "work_hours": {"start": request.work_hours_start, "end": request.work_hours_end},
                    "method": "ml_with_recurring",
                    "days_ahead": days_ahead
                }
            )
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
        else:
            # Clear old items
            db.query(ScheduleItem).filter(ScheduleItem.schedule_id == schedule.id).delete()
            schedule.optimization_score = sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else 0.0
            schedule.schedule_type = schedule_type
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
            items=item_responses,
            created_at=schedule.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Schedule optimization failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Schedule optimization error: {str(e)}")

@router.get("/{date}", response_model=ScheduleResponse)
def get_schedule(
    date: str,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedule for a specific date (returns week view if available)."""
    schedule_date = datetime.fromisoformat(date.replace("Z", "+00:00")).date()
    week_end = schedule_date + timedelta(days=7)
    
    from sqlalchemy.orm import joinedload
    # Get schedule that covers this date (could be daily or weekly)
    schedule = db.query(Schedule).options(
        joinedload(Schedule.items).joinedload(ScheduleItem.task)
    ).filter(
        Schedule.account_id == current_user.id,
        Schedule.date >= datetime.combine(schedule_date, datetime.min.time()),
        Schedule.date < datetime.combine(week_end, datetime.min.time())
    ).order_by(Schedule.date.asc()).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this date")
    
    # Manually construct response with task_title
    from backend.models import ScheduleItemResponse, ScheduleResponse
    item_responses = []
    for item in schedule.items:
        task_title = item.task.title if item.task else "Unknown Task"
        item_response = ScheduleItemResponse(
            id=item.id,
            task_id=item.task_id,
            task_title=task_title,
            start_time=item.start_time,
            end_time=item.end_time,
            placement_reason=item.placement_reason,
            confidence_score=item.confidence_score,
            status=item.status
        )
        item_responses.append(item_response)
    
    schedule_response = ScheduleResponse(
        id=schedule.id,
        date=schedule.date,
        schedule_type=schedule.schedule_type,
        optimization_score=schedule.optimization_score,
        items=item_responses,
        created_at=schedule.created_at
    )
    
    return schedule_response
