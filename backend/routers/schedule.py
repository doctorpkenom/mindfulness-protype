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

def optimize_schedule_with_ml(
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
    Use ML ensemble to optimize task scheduling with personalized weights.
    Enhanced with research-backed insights from productivity literature.
    Returns list of scheduled tasks with start/end times and reasoning.
    """
    # Load research data for enhanced ML scoring
    research_metadata = None
    research_indexer = None
    try:
        from processor.research_metadata import ResearchMetadata, ResearchIndexer
        research_metadata = ResearchMetadata
        research_indexer = ResearchIndexer()
        print(f"[RESEARCH] Loaded {len(research_indexer.strategy_lookup)} research-backed strategies")
    except Exception as e:
        print(f"[WARNING] Could not load research data: {e}. Continuing without research enhancements.")
    
    try:
        # Initialize ML coordinator
        from ml.online_coordinator import OnlineCoordinator
        coordinator = OnlineCoordinator()
        
        # Load user's personalized ML weights if available
        user_weights = None
        if account_id and db:
            user_weights = db.query(UserMLWeights).filter(UserMLWeights.account_id == account_id).first()
            if user_weights:
                # Apply personalized weights to coordinator
                coordinator.expert_weights = {
                    "habit_optimizer": user_weights.habit_optimizer_weight,
                    "stress_predictor": user_weights.stress_predictor_weight,
                    "curiosity_tuner": user_weights.curiosity_tuner_weight,
                    "flow_manager": user_weights.flow_manager_weight,
                    "attention_manager": user_weights.attention_manager_weight,
                    "motivation_booster": user_weights.motivation_booster_weight,
                    "zeigarnik_tracker": user_weights.zeigarnik_tracker_weight
                }
    except Exception as e:
        print(f"[WARNING] Could not load ML coordinator: {e}. Using basic scheduling.")
        coordinator = None
    
    # Parse work hours
    start_hour, start_min = map(int, work_start.split(":"))
    end_hour, end_min = map(int, work_end.split(":"))
    
    # Create schedule items using the schedule date (not today)
    scheduled_items = []
    schedule_date_only = schedule_date.date() if isinstance(schedule_date, datetime) else schedule_date
    if isinstance(schedule_date_only, datetime):
        schedule_date_only = schedule_date_only.date()
    
    current_time = datetime.combine(schedule_date_only, datetime.min.time()).replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
    end_time = datetime.combine(schedule_date_only, datetime.min.time()).replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
    
    # Use ML to score and rank tasks
    task_scores = {}
    if coordinator:
        try:
            # Create context for ML evaluation
            ml_context = {
                "energy": "high" if current_energy > 0.7 else "medium" if current_energy > 0.4 else "low",
                "stress": "high" if current_stress > 0.6 else "medium" if current_stress > 0.3 else "low",
                "time_of_day": current_time.hour,
                "hour": current_time.hour
            }
            
            # Score each task using ML models enhanced with research insights
            for task in tasks:
                # Create a task "strategy" for ML evaluation
                task_strategy = {
                    "name": f"task_{task.id}",
                    "difficulty": "High" if task.difficulty >= 4 else "Medium" if task.difficulty >= 3 else "Low",
                    "tags": task.tags or [],
                    "category": task.category or "general"
                }
                
                # Get ML score by evaluating task characteristics
                try:
                    from ml.models.flow_manager import FlowManager
                    from ml.models.stress_predictor import StressPredictor
                    from data_pipeline.preprocessor import DataPreprocessor
                    
                    preprocessor = DataPreprocessor()
                    flow_manager = FlowManager()
                    stress_predictor = StressPredictor()
                    
                    # Create context vector for ML models
                    context_vec = preprocessor.normalize_context({
                        "energy": current_energy,
                        "stress": current_stress,
                        "time_of_day": current_time.hour
                    })
                    
                    # Get scores from ML models
                    flow_scores = flow_manager.predict(context_vec, [task_strategy])
                    stress_scores = stress_predictor.predict(context_vec, [task_strategy])
                    
                    flow_score = flow_scores.get(task_strategy["name"], 0.5)
                    stress_score = stress_scores.get(task_strategy["name"], 0.5)
                    
                    # Apply research-backed enhancements to ML scores
                    research_boost = 0.0
                    research_reason = []
                    
                    if research_metadata:
                        # Check task characteristics against research insights
                        energy_level = "high" if current_energy > 0.7 else "medium" if current_energy > 0.4 else "low"
                        stress_level = "high" if current_stress > 0.6 else "medium" if current_stress > 0.3 else "low"
                        
                        # Fogg (2009): Low energy -> prefer simple tasks
                        if energy_level == "low" and task.difficulty <= 2:
                            fogg_features = research_metadata.ML_FEATURES.get("fogg_2009", {})
                            if current_energy < fogg_features.get("energy_threshold", 0.3):
                                research_boost += 0.15
                                research_reason.append("Fogg: Simple tasks for low energy")
                        
                        # Csikszentmihalyi (1990): High energy -> prefer challenging tasks
                        if energy_level == "high" and task.difficulty >= 4:
                            flow_features = research_metadata.ML_FEATURES.get("csikszentmihalyi_1990", {})
                            if current_energy > flow_features.get("energy_threshold", 0.6):
                                research_boost += 0.12
                                research_reason.append("Flow: Challenge matches high energy")
                        
                        # Sirois (2014): High stress -> prefer low-difficulty, self-compassion tasks
                        if stress_level == "high":
                            sirois_features = research_metadata.ML_FEATURES.get("sirois_2014", {})
                            if current_stress > sirois_features.get("stress_threshold", 0.6):
                                if task.difficulty <= 2:
                                    research_boost += 0.20
                                    research_reason.append("Sirois: Low difficulty for high stress")
                                else:
                                    research_boost -= 0.15  # Penalize hard tasks when stressed
                        
                        # Lally (2010): Habit formation - boost recurring tasks
                        if task.recurrence_pattern and task.recurrence_pattern != "none":
                            lally_features = research_metadata.ML_FEATURES.get("lally_2010", {})
                            research_boost += 0.10
                            research_reason.append("Lally: Habit consistency boost")
                        
                        # Ryan & Deci (2000): SDT - boost tasks with autonomy/competence
                        if task.category in ["personal", "learning"] or "autonomy" in (task.tags or []):
                            sdt_features = research_metadata.ML_FEATURES.get("ryan_deci_2000", {})
                            research_boost += 0.08
                            research_reason.append("SDT: Autonomy/competence boost")
                        
                        # Sweller (1988): Cognitive load - penalize complex tasks when energy is low
                        if energy_level == "low" and task.difficulty >= 4:
                            sweller_features = research_metadata.ML_FEATURES.get("sweller_1988", {})
                            research_boost -= 0.12
                            research_reason.append("Sweller: High cognitive load penalty")
                        
                        # Gollwitzer (1999): Implementation intentions - boost tasks with clear deadlines
                        if task.deadline:
                            gollwitzer_features = research_metadata.ML_FEATURES.get("gollwitzer_1999", {})
                            research_boost += 0.05
                            research_reason.append("Gollwitzer: Clear goal boost")
                    
                    # Combine ML scores with priority and research insights
                    flow_weight = coordinator.expert_weights.get("flow_manager", 1.2)
                    stress_weight = coordinator.expert_weights.get("stress_predictor", 1.8)
                    
                    base_ml_score = (
                        flow_score * flow_weight * 0.4 + 
                        stress_score * stress_weight * 0.3 + 
                        (task.priority / 5.0) * 0.3
                    ) / (flow_weight + stress_weight + 1.0)  # Normalize
                    
                    # Apply research boost (capped at reasonable limits)
                    ml_score = min(1.0, max(0.0, base_ml_score + research_boost))
                    
                    # Store research reasoning for later use
                    task_scores[task.id] = {
                        "score": ml_score,
                        "research_reasons": research_reason,
                        "base_score": base_ml_score,
                        "research_boost": research_boost
                    }
                except Exception as e:
                    print(f"[WARNING] ML model scoring failed for task {task.id}: {e}")
                    # Fallback to priority-based scoring
                    task_scores[task.id] = {
                        "score": task.priority / 5.0,
                        "research_reasons": [],
                        "base_score": task.priority / 5.0,
                        "research_boost": 0.0
                    }
        except Exception as e:
            print(f"[WARNING] ML scoring failed: {e}. Using fallback scoring.")
            # Fallback: use priority and difficulty
            for task in tasks:
                task_scores[task.id] = {
                    "score": task.priority / 5.0,
                    "research_reasons": [],
                    "base_score": task.priority / 5.0,
                    "research_boost": 0.0
                }
    
    # Sort tasks using ML scores (with research enhancements) if available, otherwise use priority
    if task_scores:
        def get_score(task_id):
            score_data = task_scores.get(task_id)
            if isinstance(score_data, dict):
                return score_data["score"]
            return score_data if score_data else 0.0
        
        sorted_tasks = sorted(tasks, key=lambda t: (-get_score(t.id), t.difficulty))
    else:
        sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.difficulty))
    
    # Schedule tasks
    for task in sorted_tasks:
        # Initialize research reasons for this task
        research_reasons = []
        
        # Create context for placement scoring
        context = {
            "stress": current_stress,
            "energy": current_energy,
            "time_of_day": current_time.hour,
            "task_difficulty": task.difficulty / 5.0,
            "task_energy_required": task.energy_required,
            "task_focus_required": task.focus_required
        }
        
        # Calculate energy match
        energy_match = abs(current_energy - task.energy_required)
        
        # Enhanced placement score using ML insights and research data
        score_data = task_scores.get(task.id) if task_scores else None
        if isinstance(score_data, dict):
            ml_score = score_data["score"]
            research_reasons = score_data.get("research_reasons", [])
        elif score_data is not None:
            # Handle legacy format (just a number)
            ml_score = score_data
            research_reasons = []
        else:
            ml_score = task.priority / 5.0
            research_reasons = []
        
        placement_score = (
            ml_score * 0.4 +  # ML-based priority
            (1 - energy_match) * 0.3 +  # Energy match
            (1 - task.difficulty / 5.0) * 0.2 +  # Easier tasks when energy is lower
            (1 - current_stress) * 0.1  # Lower stress = better placement
        )
        
        # Calculate task duration (use estimated minutes, but consider historical accuracy)
        estimated_duration = task.estimated_minutes
        if task.completion_accuracy and task.completion_accuracy > 0:
            # Adjust based on historical accuracy
            estimated_duration = int(estimated_duration * task.completion_accuracy)
        
        task_duration = timedelta(minutes=estimated_duration)
        
        # Check if task fits in remaining time
        # Be more aggressive: allow tasks to go up to 2 hours past end_time to fit more tasks
        effective_end_time = end_time + timedelta(hours=2)
        time_remaining = (end_time - current_time).total_seconds() / 60  # minutes
        
        if current_time + task_duration > effective_end_time:
            # Task is too large even with overflow allowance
            print(f"[SCHEDULE] Task '{task.title}' ({estimated_duration} min) is too large. Remaining time: {time_remaining:.1f} min")
            continue
        
        # If task goes past normal end_time, note it but schedule anyway
        goes_past_end = current_time + task_duration > end_time
        if goes_past_end:
            overflow_minutes = ((current_time + task_duration) - end_time).total_seconds() / 60
            base_reason = f"ML Score: {ml_score:.2f}, Priority: {task.priority}, Energy match: {1-energy_match:.2f}, Final Score: {placement_score:.2f} (Extends {overflow_minutes:.0f} min past work hours)"
            confidence_score = placement_score * 0.85  # Slightly lower score for overflow
        else:
            base_reason = f"ML Score: {ml_score:.2f}, Priority: {task.priority}, Energy match: {1-energy_match:.2f}, Final Score: {placement_score:.2f}"
            confidence_score = placement_score
        
        # Add research insights to placement reason
        if research_reasons:
            research_note = " | Research: " + ", ".join(research_reasons[:2])  # Limit to 2 reasons
            placement_reason = base_reason + research_note
        else:
            placement_reason = base_reason
        
        # Create schedule item
        item = {
            "task_id": task.id,
            "task_title": task.title,
            "start_time": current_time,
            "end_time": current_time + task_duration,
            "placement_reason": placement_reason,
            "confidence_score": confidence_score
        }
        
        scheduled_items.append(item)
        
        # Update energy (tasks drain energy based on their requirements)
        energy_drain = task.energy_required * 0.15  # More realistic energy drain
        current_energy = max(0.1, current_energy - energy_drain)
        
        # Add break between tasks (shorter breaks to fit more tasks)
        # Reduce break time if we're running low on time or past end_time
        time_remaining_after_task = (end_time - (current_time + task_duration)).total_seconds() / 60
        if goes_past_end or time_remaining_after_task < 30:  # Past end or less than 30 min remaining
            break_duration = 0  # No break to maximize task fitting
        elif time_remaining_after_task < 60:  # Less than 1 hour remaining
            break_duration = 2 if task.energy_required < 0.6 else 3  # Very short breaks
        else:
            break_duration = 5 if task.energy_required < 0.6 else 10
        
        current_time = current_time + task_duration + timedelta(minutes=break_duration)
        
        # Only stop if we're way past the effective end time
        if current_time >= effective_end_time:
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
        
        # Optimize schedule with ML
        scheduled_items = optimize_schedule_with_ml(
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
            raise HTTPException(status_code=400, detail="Could not schedule any tasks - not enough time")
        
        # Warn if not all tasks were scheduled
        if len(scheduled_items) < len(tasks):
            unscheduled_count = len(tasks) - len(scheduled_items)
            print(f"[WARNING] Only scheduled {len(scheduled_items)}/{len(tasks)} tasks. {unscheduled_count} tasks couldn't fit in the available time window.")
    
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
        
        # Return schedule with items - manually construct response to ensure task_title is included
        # Reload with eager loading to include task relationship
        from sqlalchemy.orm import joinedload
        schedule_with_items = db.query(Schedule).options(
            joinedload(Schedule.items).joinedload(ScheduleItem.task)
        ).filter(Schedule.id == schedule.id).first()
        
        if not schedule_with_items:
            schedule_with_items = schedule
            # Reload items with task relationship
            db.refresh(schedule_with_items)
            for item in schedule_with_items.items:
                if item.task_id:
                    item.task = db.query(Task).filter(Task.id == item.task_id).first()
        
        # Manually construct ScheduleItemResponse objects with task_title
        from backend.models import ScheduleItemResponse
        item_responses = []
        for item in schedule_with_items.items:
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
        
        # Manually construct ScheduleResponse
        from backend.models import ScheduleResponse
        schedule_response = ScheduleResponse(
            id=schedule_with_items.id,
            date=schedule_with_items.date,
            schedule_type=schedule_with_items.schedule_type,
            optimization_score=schedule_with_items.optimization_score,
            items=item_responses,
            created_at=schedule_with_items.created_at
        )
        
        return schedule_response
        
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
    
    from sqlalchemy.orm import joinedload
    schedule = db.query(Schedule).options(
        joinedload(Schedule.items).joinedload(ScheduleItem.task)
    ).filter(
        Schedule.account_id == current_user.id,
        Schedule.date >= datetime.combine(schedule_date, datetime.min.time()),
        Schedule.date < datetime.combine(schedule_date, datetime.min.time()) + timedelta(days=1)
    ).first()
    
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
