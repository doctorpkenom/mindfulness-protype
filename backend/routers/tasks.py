"""
Task management router - CRUD operations for user tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.db_models import Account, Task, SystemLog, UserMLWeights
from backend.auth import get_current_user
from backend.models import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

def update_ml_weights_from_completion(task: Task, account_id: int, db: Session):
    """
    Update user's ML weights based on task completion performance.
    This allows the system to learn and improve over time.
    """
    try:
        # Get or create user ML weights
        ml_weights = db.query(UserMLWeights).filter(UserMLWeights.account_id == account_id).first()
        if not ml_weights:
            ml_weights = UserMLWeights(account_id=account_id)
            db.add(ml_weights)
            db.commit()
            db.refresh(ml_weights)
        
        # Calculate performance metrics
        time_accuracy = task.completion_accuracy if task.completion_accuracy else 1.0
        satisfaction = task.user_satisfaction / 5.0 if task.user_satisfaction else 0.7  # Default to neutral
        
        # Performance score (0-1, higher is better)
        performance_score = (time_accuracy * 0.6 + satisfaction * 0.4)
        
        # Determine which ML models performed well based on task characteristics
        # High priority + good performance = stress_predictor and flow_manager worked well
        # High energy tasks completed = flow_manager and motivation_booster worked well
        # On-time completion = attention_manager worked well
        
        learning_rate = 0.05  # How much to adjust weights per completion
        
        # Adjust weights based on performance
        if task.priority >= 4:  # High priority tasks
            if performance_score > 0.7:
                ml_weights.stress_predictor_weight = min(2.0, ml_weights.stress_predictor_weight + learning_rate)
                ml_weights.flow_manager_weight = min(1.5, ml_weights.flow_manager_weight + learning_rate * 0.5)
            else:
                ml_weights.stress_predictor_weight = max(1.0, ml_weights.stress_predictor_weight - learning_rate * 0.5)
        
        if task.energy_required > 0.7:  # High energy tasks
            if performance_score > 0.7:
                ml_weights.flow_manager_weight = min(1.5, ml_weights.flow_manager_weight + learning_rate)
                ml_weights.motivation_booster_weight = min(1.5, ml_weights.motivation_booster_weight + learning_rate * 0.5)
            else:
                ml_weights.flow_manager_weight = max(0.8, ml_weights.flow_manager_weight - learning_rate * 0.5)
        
        if time_accuracy > 0.9:  # Very accurate time estimates
            ml_weights.attention_manager_weight = min(1.3, ml_weights.attention_manager_weight + learning_rate)
        
        if satisfaction > 0.8:  # High satisfaction
            ml_weights.motivation_booster_weight = min(1.5, ml_weights.motivation_booster_weight + learning_rate)
            ml_weights.curiosity_tuner_weight = min(1.2, ml_weights.curiosity_tuner_weight + learning_rate * 0.5)
        
        # Update interaction count
        ml_weights.total_interactions += 1
        ml_weights.last_updated = datetime.utcnow()
        
        db.commit()
        
        print(f"[ML LEARNING] Updated weights for user {account_id} based on task {task.id} completion. Performance: {performance_score:.2f}")
        
    except Exception as e:
        print(f"[ERROR] Failed to update ML weights: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise - learning is optional

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
        
        # Automatically schedule the task using ML
        try:
            # Import the optimization function directly to avoid circular dependencies
            from datetime import datetime, timedelta
            from backend.db_models import Schedule, ScheduleItem
            
            # Import ML coordinator and optimization logic
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sys.path.append(project_root)
            
            # Use the same optimization logic as schedule.py
            from ml.online_coordinator import OnlineCoordinator
            from backend.db_models import UserMLWeights
            
            # Get all pending/scheduled tasks for today
            today = datetime.utcnow().date()
            pending_tasks = db.query(Task).filter(
                Task.account_id == current_user.id,
                Task.status.in_(["pending", "scheduled"])
            ).all()
            
            if pending_tasks:
                # Use the optimization function from schedule module
                # Import it directly to avoid circular dependency
                import importlib.util
                schedule_path = os.path.join(os.path.dirname(__file__), "schedule.py")
                spec = importlib.util.spec_from_file_location("schedule_module", schedule_path)
                schedule_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(schedule_module)
                optimize_func = schedule_module.optimize_schedule_with_ml
                
                # Default work hours (6 AM to 10 PM) - full day schedule
                work_start = "06:00"
                work_end = "22:00"
                
                # Use task deadline date if available, otherwise use today
                schedule_date = task.deadline.date() if task.deadline else today
                
                # Get user's current state (could be enhanced with real-time tracking)
                energy = 0.7  # Default
                stress = 0.3  # Default
                
                # Optimize schedule
                scheduled_items = optimize_func(
                    tasks=pending_tasks,
                    work_start=work_start,
                    work_end=work_end,
                    schedule_date=datetime.combine(schedule_date, datetime.min.time()),
                    current_energy=energy,
                    current_stress=stress,
                    account_id=current_user.id,
                    db=db
                )
                
                # Find or create schedule for the date
                schedule = db.query(Schedule).filter(
                    Schedule.account_id == current_user.id,
                    Schedule.date >= datetime.combine(schedule_date, datetime.min.time()),
                    Schedule.date < datetime.combine(schedule_date, datetime.min.time()) + timedelta(days=1)
                ).first()
                
                if not schedule:
                    schedule = Schedule(
                        account_id=current_user.id,
                        date=datetime.combine(schedule_date, datetime.min.time()),
                        schedule_type="daily",
                        optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else 0.0,
                        optimization_context={
                            "energy": energy,
                            "stress": stress,
                            "work_hours": {"start": work_start, "end": work_end},
                            "auto_scheduled": True
                        }
                    )
                    db.add(schedule)
                    db.commit()
                    db.refresh(schedule)
                else:
                    # Update existing schedule
                    schedule.optimization_score = sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else schedule.optimization_score
                    db.commit()
                
                # Clear old schedule items for this schedule
                db.query(ScheduleItem).filter(ScheduleItem.schedule_id == schedule.id).delete()
                
                # Create new schedule items
                for item_data in scheduled_items:
                    task_obj = db.query(Task).filter(Task.id == item_data["task_id"]).first()
                    if task_obj:
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
                        task_obj.status = "scheduled"
                        task_obj.scheduled_start = item_data["start_time"]
                        task_obj.scheduled_end = item_data["end_time"]
                
                db.commit()
                
        except Exception as e:
            # Don't fail task creation if scheduling fails
            print(f"[WARNING] Auto-scheduling failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Get all pending/scheduled tasks for today
            today = datetime.utcnow().date()
            pending_tasks = db.query(Task).filter(
                Task.account_id == current_user.id,
                Task.status.in_(["pending", "scheduled"]),
                Task.deadline >= datetime.combine(today, datetime.min.time()) if task.deadline else True
            ).all()
            
            if pending_tasks:
                # Default work hours (6 AM to 10 PM) - full day schedule
                work_start = "06:00"
                work_end = "22:00"
                
                # Use task deadline date if available, otherwise use today
                schedule_date = task.deadline.date() if task.deadline else today
                
                # Get user's current state (could be enhanced with real-time tracking)
                energy = 0.7  # Default
                stress = 0.3  # Default
                
                # Optimize schedule
                scheduled_items = optimize_schedule_with_ml(
                    tasks=pending_tasks,
                    work_start=work_start,
                    work_end=work_end,
                    schedule_date=datetime.combine(schedule_date, datetime.min.time()),
                    current_energy=energy,
                    current_stress=stress,
                    account_id=current_user.id,
                    db=db
                )
                
                # Find or create schedule for the date
                from backend.db_models import Schedule, ScheduleItem
                schedule = db.query(Schedule).filter(
                    Schedule.account_id == current_user.id,
                    Schedule.date >= datetime.combine(schedule_date, datetime.min.time()),
                    Schedule.date < datetime.combine(schedule_date, datetime.min.time()) + timedelta(days=1)
                ).first()
                
                if not schedule:
                    schedule = Schedule(
                        account_id=current_user.id,
                        date=datetime.combine(schedule_date, datetime.min.time()),
                        schedule_type="daily",
                        optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else 0.0,
                        optimization_context={
                            "energy": energy,
                            "stress": stress,
                            "work_hours": {"start": work_start, "end": work_end},
                            "auto_scheduled": True
                        }
                    )
                    db.add(schedule)
                    db.commit()
                    db.refresh(schedule)
                else:
                    # Update existing schedule
                    schedule.optimization_score = sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else schedule.optimization_score
                    db.commit()
                
                # Clear old schedule items for this schedule
                db.query(ScheduleItem).filter(ScheduleItem.schedule_id == schedule.id).delete()
                
                # Create new schedule items
                for item_data in scheduled_items:
                    task_obj = db.query(Task).filter(Task.id == item_data["task_id"]).first()
                    if task_obj:
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
                        task_obj.status = "scheduled"
                        task_obj.scheduled_start = item_data["start_time"]
                        task_obj.scheduled_end = item_data["end_time"]
                
                db.commit()
                
        except Exception as e:
            # Don't fail task creation if scheduling fails
            print(f"[WARNING] Auto-scheduling failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Log task creation
        log = SystemLog(
            level="INFO",
            component="task_manager",
            message=f"Task created: {task.title}",
            context_data={"task_id": task.id, "account_id": current_user.id, "auto_scheduled": True}
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
    
    # Track if status changed to completed
    status_changed_to_completed = task_data.status == "completed" and task.status != "completed"
    status_changed_from_completed = task.status == "completed" and task_data.status and task_data.status != "completed"
    
    # If marking as completed, set completion time and calculate accuracy
    if status_changed_to_completed:
        task.completed_at = datetime.utcnow()
        if task.estimated_minutes and task.actual_minutes:
            task.completion_accuracy = task.estimated_minutes / task.actual_minutes
        
        # Learn from task completion to improve ML models
        try:
            update_ml_weights_from_completion(task, current_user.id, db)
        except Exception as e:
            print(f"[WARNING] ML learning update failed: {e}")
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    # Automatically update schedule when task is added, updated, or completed
    try:
        from datetime import timedelta
        from backend.db_models import Schedule, ScheduleItem
        import importlib.util
        import os
        
        # Import the optimization function
        schedule_path = os.path.join(os.path.dirname(__file__), "schedule.py")
        spec = importlib.util.spec_from_file_location("schedule_module", schedule_path)
        schedule_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(schedule_module)
        optimize_func = schedule_module.optimize_schedule_with_ml
        
        # Get all pending/scheduled tasks (excluding completed ones)
        pending_tasks = db.query(Task).filter(
            Task.account_id == current_user.id,
            Task.status.in_(["pending", "scheduled"])
        ).all()
        
        if pending_tasks:
            # Determine which date to schedule for
            today = datetime.utcnow().date()
            schedule_date = task.deadline.date() if task.deadline else today
            
            # Default work hours (6 AM to 10 PM) - full day schedule
            work_start = "06:00"
            work_end = "22:00"
            
            # Get user's current state (could be enhanced with real-time tracking)
            energy = 0.7  # Default
            stress = 0.3  # Default
            
            # Optimize schedule
            scheduled_items = optimize_func(
                tasks=pending_tasks,
                work_start=work_start,
                work_end=work_end,
                schedule_date=datetime.combine(schedule_date, datetime.min.time()),
                current_energy=energy,
                current_stress=stress,
                account_id=current_user.id,
                db=db
            )
            
            if scheduled_items:
                # Find or create schedule for the date
                schedule = db.query(Schedule).filter(
                    Schedule.account_id == current_user.id,
                    Schedule.date >= datetime.combine(schedule_date, datetime.min.time()),
                    Schedule.date < datetime.combine(schedule_date, datetime.min.time()) + timedelta(days=1)
                ).first()
                
                if not schedule:
                    schedule = Schedule(
                        account_id=current_user.id,
                        date=datetime.combine(schedule_date, datetime.min.time()),
                        schedule_type="daily",
                        optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items),
                        optimization_context={
                            "energy": energy,
                            "stress": stress,
                            "work_hours": {"start": work_start, "end": work_end},
                            "auto_scheduled": True
                        }
                    )
                    db.add(schedule)
                    db.commit()
                    db.refresh(schedule)
                else:
                    # Update existing schedule
                    schedule.optimization_score = sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items)
                    db.commit()
                
                # Clear old schedule items for this schedule
                db.query(ScheduleItem).filter(ScheduleItem.schedule_id == schedule.id).delete()
                
                # Create new schedule items
                for item_data in scheduled_items:
                    task_obj = db.query(Task).filter(Task.id == item_data["task_id"]).first()
                    if task_obj:
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
                        task_obj.status = "scheduled"
                        task_obj.scheduled_start = item_data["start_time"]
                        task_obj.scheduled_end = item_data["end_time"]
                
                db.commit()
                print(f"[AUTO-SCHEDULE] Updated schedule for {schedule_date} with {len(scheduled_items)} tasks")
    except Exception as e:
        # Don't fail task update if scheduling fails
        print(f"[WARNING] Auto-schedule update failed: {e}")
        import traceback
        traceback.print_exc()
    
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
