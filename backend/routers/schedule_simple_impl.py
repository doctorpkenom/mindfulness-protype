"""
SIMPLIFIED single-day schedule optimizer - replaces complex multi-day logic.
Uses advanced ScheduleOptimizer with research-backed ML.
"""
from datetime import datetime, timedelta
from typing import List, Dict
from backend.db_models import Task

def optimize_schedule_simple_day(
    tasks: List[Task],
    work_start: str,
    work_end: str,
    schedule_date: datetime,
    current_energy: float = 0.7,
    current_stress: float = 0.3,
    account_id: int = None,
    db = None
) -> List[dict]:
    """
    SIMPLIFIED: Single-day scheduling only.
    Uses advanced ScheduleOptimizer with 32+ features and research-backed insights.
    NO recurring expansion, NO multi-day - just schedule today perfectly.
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
    day_start = datetime.combine(schedule_date_only, datetime.min.time().replace(hour=work_start_hour, minute=work_start_min))
    day_end = datetime.combine(schedule_date_only, datetime.min.time().replace(hour=work_end_hour, minute=work_end_min))
    
    # Convert tasks to dict format
    task_dicts = []
    for task in tasks:
        task_dicts.append({
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
        })
    
    # Sort by priority and deadline urgency
    def task_priority(task_dict):
        score = task_dict["priority"] / 5.0
        if task_dict.get("deadline"):
            try:
                deadline = task_dict["deadline"]
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                if isinstance(deadline, datetime):
                    days_until = (deadline.date() - schedule_date_only).days
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
    
    # Schedule tasks using greedy algorithm with ML scoring
    scheduled_items = []
    scheduled_task_ids = set()
    current_time = day_start
    energy = current_energy
    stress = current_stress
    
    for task_dict in sorted_tasks:
        if task_dict["id"] in scheduled_task_ids:
            continue
        
        task_minutes = task_dict["estimated_minutes"]
        task_end = current_time + timedelta(minutes=task_minutes)
        
        # Check if task fits in remaining time
        if task_end > day_end:
            # Try to find a better slot later in the day
            # For now, skip if it doesn't fit
            continue
        
        # Score this time slot using advanced ML
        slot_hour = current_time.hour
        score, reasoning = optimizer.score_task_for_slot(
            task_dict, slot_hour, energy, stress, research_metadata
        )
        
        # STRICT time enforcement
        title_lower = (task_dict["title"] or "").lower()
        tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task_dict.get("tags") or [])]
        
        # Morning tasks MUST be in morning (6-12)
        if any(kw in title_lower for kw in ["breakfast", "morning", "meditation", "yoga", "exercise"]) or "morning" in tags:
            if not (6 <= slot_hour < 12):
                continue  # Skip - wrong time
        
        # Evening tasks MUST be in evening (17-22)
        if any(kw in title_lower for kw in ["dinner", "supper", "cook", "prep"]) or "evening" in tags:
            if not (17 <= slot_hour < 22):
                continue  # Skip - wrong time
        
        # Only schedule if score is positive
        if score > 0:
            scheduled_items.append({
                "task_id": task_dict["id"],
                "task_title": task_dict["title"],
                "start_time": current_time,
                "end_time": task_end,
                "placement_reason": f"ML Score: {score:.2f} | " + " | ".join(reasoning[:3]),
                "confidence_score": score
            })
            
            scheduled_task_ids.add(task_dict["id"])
            
            # Update time and energy
            current_time = task_end + timedelta(minutes=5)  # 5 min break
            energy = max(0.1, energy - (task_dict["energy_required"] * 0.1))
            stress = min(1.0, stress + 0.05)
    
    return scheduled_items
