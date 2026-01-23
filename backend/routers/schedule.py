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

def can_split_task(task: Task) -> bool:
    """
    Determine if a task can be split into multiple time slots.
    Tasks that can be split: long tasks (>2 hours), non-urgent, not meetings/deadlines.
    """
    # Don't split if task is too short
    if task.estimated_minutes < 120:  # Less than 2 hours
        return False
    
    # Don't split urgent tasks or tasks with deadlines
    if task.priority >= 5 or task.deadline:
        return False
    
    # Don't split tasks with specific tags that indicate they shouldn't be split
    tags = task.tags or []
    non_splittable_tags = ["meeting", "deadline", "urgent", "one-shot", "continuous"]
    if any(tag in non_splittable_tags for tag in tags):
        return False
    
    # Can split if it's a long task that's not urgent
    return True

def get_optimal_chunk_size(task: Task) -> int:
    """
    Get optimal chunk size for splitting a task (in minutes).
    Prefers 60-90 minute chunks for focus, but adapts to task characteristics.
    """
    total_minutes = task.estimated_minutes
    
    # For very long tasks (>4 hours), use 90-minute chunks
    if total_minutes > 240:
        return 90
    # For medium-long tasks (2-4 hours), use 60-minute chunks
    elif total_minutes > 120:
        return 60
    # For tasks just over 2 hours, try 45-minute chunks
    else:
        return 45

def optimize_schedule_with_ml(
    tasks: List[Task],
    work_start: str,
    work_end: str,
    schedule_date: datetime,
    current_energy: float = 0.7,
    current_stress: float = 0.3,
    account_id: int = None,
    db: Session = None,
    days_ahead: int = 1
) -> List[dict]:
    """
    Use ML ensemble to optimize task scheduling with personalized weights.
    Enhanced with research-backed insights from productivity literature.
    Supports multi-day scheduling and task splitting.
    Returns list of scheduled tasks with start/end times and reasoning.
    
    Args:
        days_ahead: Number of days to schedule ahead (default 1 for single day, 7 for week)
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
    
    # Create schedule items for multiple days
    scheduled_items = []
    schedule_date_only = schedule_date.date() if isinstance(schedule_date, datetime) else schedule_date
    if isinstance(schedule_date_only, datetime):
        schedule_date_only = schedule_date_only.date()
    
    # Create day slots for multi-day scheduling
    day_slots = []
    for day_offset in range(days_ahead):
        day_date = schedule_date_only + timedelta(days=day_offset)
        day_start = datetime.combine(day_date, datetime.min.time()).replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
        day_end = datetime.combine(day_date, datetime.min.time()).replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
        day_slots.append({
            "date": day_date,
            "start": day_start,
            "end": day_end,
            "current_time": day_start,
            "energy": current_energy if day_offset == 0 else 0.8,  # Reset energy each day
            "stress": current_stress if day_offset == 0 else 0.2  # Reset stress each day
        })
    
    # Use first day's start time for initial ML scoring (will be refined during actual scheduling)
    initial_time = day_slots[0]["start"] if day_slots else datetime.now()
    end_time = day_slots[-1]["end"] if day_slots else datetime.now()  # Overall end time
    
    # Use ML to score and rank tasks (batch scoring for efficiency)
    task_scores = {}
    if coordinator:
        try:
            # Create context for ML evaluation
            # Get historical timer data for better estimates
            timer_history = {}
            if account_id and db:
                from backend.db_models import TimerSession
                # Get recent timer sessions for this user to learn from actual times
                recent_timers = db.query(TimerSession).filter(
                    TimerSession.account_id == account_id,
                    TimerSession.status == "completed",
                    TimerSession.actual_seconds.isnot(None)
                ).order_by(TimerSession.completed_at.desc()).limit(50).all()
                
                # Build a map of task patterns -> actual durations
                for timer in recent_timers:
                    if timer.task_id:
                        task = db.query(Task).filter(Task.id == timer.task_id).first()
                        if task:
                            key = f"{task.category}_{task.difficulty}"
                            if key not in timer_history:
                                timer_history[key] = []
                            timer_history[key].append(timer.actual_seconds / 60)  # Convert to minutes
            
            # Batch process tasks for ML scoring (more efficient)
            task_strategies = []
            for task in tasks:
                # Build comprehensive task strategy with all relevant attributes
                task_tags = task.tags or []
                task_strategies.append({
                    "name": f"task_{task.id}",
                    "difficulty": "Very High" if task.difficulty >= 5 else "High" if task.difficulty >= 4 else "Medium" if task.difficulty >= 3 else "Low",
                    "tags": task_tags,
                    "category": task.category or "general",
                    "priority": task.priority,
                    "energy_required": task.energy_required,
                    "focus_required": task.focus_required,
                    "has_deadline": bool(task.deadline),
                    "is_recurring": bool(task.recurrence_pattern and task.recurrence_pattern != "none")
                })
            
            # Score all tasks in batch for efficiency with robust error handling
            try:
                from ml.models.flow_manager import FlowManager
                from ml.models.stress_predictor import StressPredictor
                from data_pipeline.preprocessor import DataPreprocessor
                
                preprocessor = DataPreprocessor()
                flow_manager = FlowManager()
                stress_predictor = StressPredictor()
                
                # Use initial time for batch scoring (will be refined per time slot during scheduling)
                initial_hour = initial_time.hour if hasattr(initial_time, 'hour') else 12
                
                # Create context vector for ML models with validation
                try:
                    context_dict = {
                        "energy": max(0.0, min(1.0, float(current_energy))),
                        "stress": max(0.0, min(1.0, float(current_stress))),
                        "time_of_day": max(0, min(23, int(initial_hour)))
                    }
                    context_vec = preprocessor.normalize_context(context_dict)
                    
                    # Validate context vector
                    if context_vec is None or len(context_vec) == 0:
                        raise ValueError("Empty context vector from preprocessor")
                    
                    # Ensure it's a numpy array or list
                    if hasattr(context_vec, 'tolist'):
                        context_vec = context_vec.tolist()
                    elif not isinstance(context_vec, (list, np.ndarray)):
                        raise ValueError(f"Invalid context vector type: {type(context_vec)}")
                    
                except Exception as ctx_error:
                    print(f"[WARNING] Context normalization failed: {ctx_error}. Using defaults.")
                    # Fallback: create a simple context vector [Morning, Afternoon, Evening, Night, Energy, Stress]
                    import numpy as np
                    hour = int(initial_hour) if hasattr(initial_hour, '__int__') else 12
                    time_vec = [0] * 4
                    if 5 <= hour < 12: time_vec[0] = 1
                    elif 12 <= hour < 17: time_vec[1] = 1
                    elif 17 <= hour < 22: time_vec[2] = 1
                    else: time_vec[3] = 1
                    context_vec = np.array(time_vec + [max(0.0, min(1.0, float(current_energy))), max(0.0, min(1.0, float(current_stress)))])
                
                # Batch predict for all tasks with error handling per model
                flow_scores = {}
                stress_scores = {}
                
                try:
                    flow_scores = flow_manager.predict(context_vec, task_strategies)
                    if not flow_scores or len(flow_scores) == 0:
                        print("[WARNING] FlowManager returned empty scores, using defaults")
                        flow_scores = {s["name"]: 0.5 for s in task_strategies}
                except Exception as flow_error:
                    print(f"[WARNING] FlowManager prediction failed: {flow_error}. Using defaults.")
                    flow_scores = {s["name"]: 0.5 for s in task_strategies}
                
                try:
                    stress_scores = stress_predictor.predict(context_vec, task_strategies)
                    if not stress_scores or len(stress_scores) == 0:
                        print("[WARNING] StressPredictor returned empty scores, using defaults")
                        stress_scores = {s["name"]: 0.5 for s in task_strategies}
                except Exception as stress_error:
                    print(f"[WARNING] StressPredictor prediction failed: {stress_error}. Using defaults.")
                    stress_scores = {s["name"]: 0.5 for s in task_strategies}
                
                # Process each task's scores
                for idx, task in enumerate(tasks):
                    task_strategy = task_strategies[idx]
                    task_id = task.id
                    
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
                        
                        # Rubinstein (2001): Task switching - penalize high-focus tasks when already focused
                        if task.focus_required and task.focus_required > 0.7:
                            rubinstein_features = research_metadata.ML_FEATURES.get("rubinstein_2001", {})
                            # If we're already doing high-focus work, switching is costly
                            if current_energy < 0.5:  # Low energy = already taxed
                                research_boost -= 0.08
                                research_reason.append("Rubinstein: Task switching cost when low energy")
                        
                        # Zeigarnik (1927): Unfinished tasks - boost tasks that provide closure
                        if task.status == "pending" and task.priority >= 4:
                            zeigarnik_features = research_metadata.ML_FEATURES.get("zeigarnik_1927", {})
                            research_boost += 0.06
                            research_reason.append("Zeigarnik: Closure for high-priority pending tasks")
                        
                        # Bandura (1977): Self-efficacy - boost tasks that build confidence
                        if task.difficulty <= 2 and task.category in ["personal", "learning"]:
                            bandura_features = research_metadata.ML_FEATURES.get("bandura_1977", {})
                            if bandura_features.get("confidence_building", False):
                                research_boost += 0.07
                                research_reason.append("Bandura: Confidence-building task")
                        
                        # Kang (2009): Epistemic curiosity - boost learning tasks when energy is medium-high
                        if task.category == "learning" and 0.4 <= current_energy <= 0.8:
                            kang_features = research_metadata.ML_FEATURES.get("kang_2009", {})
                            learning_bonus = kang_features.get("learning_bonus", 0.2)
                            research_boost += learning_bonus
                            research_reason.append("Kang: Epistemic curiosity boost")
                        
                        # Gollwitzer (1999): Implementation intentions - boost tasks with clear deadlines
                        # Also enforce deadline urgency - tasks closer to deadline get higher priority
                        if task.deadline:
                            gollwitzer_features = research_metadata.ML_FEATURES.get("gollwitzer_1999", {})
                            research_boost += 0.05
                            research_reason.append("Gollwitzer: Clear goal boost")
                            
                            # Calculate deadline urgency - boost tasks that are closer to deadline
                            deadline_urgency = None
                            if isinstance(task.deadline, datetime):
                                days_until_deadline = (task.deadline.date() - schedule_date_only).days
                                if days_until_deadline < 0:
                                    # Past deadline - very high priority
                                    deadline_urgency = 0.5
                                    research_reason.append("URGENT: Past deadline")
                                elif days_until_deadline == 0:
                                    # Due today - very high priority
                                    deadline_urgency = 0.4
                                    research_reason.append("URGENT: Due today")
                                elif days_until_deadline <= 1:
                                    # Due tomorrow - high priority
                                    deadline_urgency = 0.3
                                    research_reason.append("URGENT: Due tomorrow")
                                elif days_until_deadline <= 3:
                                    # Due soon - moderate priority
                                    deadline_urgency = 0.2
                                    research_reason.append("Due in 2-3 days")
                                elif days_until_deadline <= 7:
                                    # Due this week - slight priority
                                    deadline_urgency = 0.1
                                    research_reason.append("Due this week")
                                
                                if deadline_urgency:
                                    research_boost += deadline_urgency
                    
                    # Combine ML scores with priority and research insights
                    flow_weight = coordinator.expert_weights.get("flow_manager", 1.2)
                    stress_weight = coordinator.expert_weights.get("stress_predictor", 1.8)
                    
                    base_ml_score = (
                        flow_score * flow_weight * 0.4 + 
                        stress_score * stress_weight * 0.3 + 
                        (task.priority / 5.0) * 0.3
                    ) / (flow_weight + stress_weight + 1.0)  # Normalize
                    
                    # Time-of-day preference boost (will be refined during actual scheduling)
                    time_boost = 0.0
                    task_tags = task.tags or []
                    
                    # Check for time-related tags (general boost, refined per time slot)
                    if "morning" in task_tags:
                        time_boost += 0.05  # General boost, will be enhanced if scheduled in morning
                    elif "afternoon" in task_tags:
                        time_boost += 0.05
                    elif "evening" in task_tags:
                        time_boost += 0.05
                    
                    # Use timer history to adjust estimates if available
                    if timer_history:
                        task_key = f"{task.category or 'general'}_{task.difficulty}"
                        if task_key in timer_history:
                            avg_actual = sum(timer_history[task_key]) / len(timer_history[task_key])
                            # If actual times are consistently different, adjust score
                            if task.estimated_minutes:
                                accuracy_ratio = avg_actual / task.estimated_minutes
                                if 0.8 <= accuracy_ratio <= 1.2:
                                    time_boost += 0.05  # Good estimate accuracy
                                    research_reason.append("Timer data: Good time estimates")
                                elif accuracy_ratio > 1.5:
                                    # Task takes longer than estimated - slight penalty
                                    time_boost -= 0.05
                                    research_reason.append("Timer data: Task often takes longer")
                    
                    # Apply research boost and time boost (capped at reasonable limits)
                    ml_score = min(1.0, max(0.0, base_ml_score + research_boost + time_boost))
                    
                    # Store research reasoning for later use
                    task_scores[task_id] = {
                        "score": ml_score,
                        "research_reasons": research_reason,
                        "base_score": base_ml_score,
                        "research_boost": research_boost,
                        "time_boost": time_boost
                    }
            except Exception as e:
                print(f"[WARNING] Batch ML scoring failed: {e}")
                # Fallback: score individually with simple priority-based scoring
                for task in tasks:
                    task_scores[task.id] = {
                        "score": task.priority / 5.0,
                        "research_reasons": [],
                        "base_score": task.priority / 5.0,
                        "research_boost": 0.0,
                        "time_boost": 0.0
                    }
        except Exception as e:
            print(f"[WARNING] ML scoring failed: {e}. Using fallback scoring.")
            # Fallback: use priority and difficulty
            for task in tasks:
                task_scores[task.id] = {
                    "score": task.priority / 5.0,
                    "research_reasons": [],
                    "base_score": task.priority / 5.0,
                    "research_boost": 0.0,
                    "time_boost": 0.0
                }
    
    # Expand recurring tasks into multiple instances for the week
    expanded_tasks = []
    for task in tasks:
        if task.recurrence_pattern and task.recurrence_pattern != "none":
            # Check if recurrence has ended
            if task.recurrence_end_date and task.recurrence_end_date.date() < schedule_date_only:
                continue  # Skip tasks whose recurrence has ended
            
            # Expand based on recurrence pattern
            if task.recurrence_pattern == "daily":
                # Create instance for each day in the week
                for day_offset in range(days_ahead):
                    day_date = schedule_date_only + timedelta(days=day_offset)
                    # Create a task instance for this day
                    expanded_tasks.append((task, day_date))
            elif task.recurrence_pattern == "weekly":
                # Create instance for the first day of the week (or specific day)
                expanded_tasks.append((task, schedule_date_only))
            elif task.recurrence_pattern == "monthly":
                # Create instance for the first day
                expanded_tasks.append((task, schedule_date_only))
            elif task.recurrence_pattern == "custom" and task.custom_recurrence_days:
                # Create instances based on custom interval
                day_offset = 0
                while day_offset < days_ahead:
                    day_date = schedule_date_only + timedelta(days=day_offset)
                    expanded_tasks.append((task, day_date))
                    day_offset += task.custom_recurrence_days
        else:
            # Non-recurring task - add once
            expanded_tasks.append((task, None))
    
    # Prepare tasks for scheduling - split tasks that can be split
    task_chunks = {}  # (task_id, day_date) -> list of chunks (remaining minutes)
    for task, day_date in expanded_tasks:
        task_key = (task.id, day_date)
        if can_split_task(task):
            chunk_size = get_optimal_chunk_size(task)
            chunks = []
            remaining = task.estimated_minutes
            while remaining > 0:
                chunk_mins = min(chunk_size, remaining)
                chunks.append(chunk_mins)
                remaining -= chunk_mins
            task_chunks[task_key] = chunks
        else:
            task_chunks[task_key] = [task.estimated_minutes]
    
    # Sort expanded tasks using ML scores (with research enhancements) if available, otherwise use priority
    # Also prioritize tasks with deadlines that are approaching
    def get_task_score(task_tuple):
        task, day_date = task_tuple
        task_id = task.id
        
        # Base score from ML
        if task_scores:
            score_data = task_scores.get(task_id)
            if isinstance(score_data, dict):
                base_score = score_data["score"]
            else:
                base_score = score_data if score_data else 0.0
        else:
            base_score = task.priority / 5.0
        
        # Deadline urgency boost - tasks with deadlines get prioritized
        deadline_boost = 0.0
        if task.deadline and isinstance(task.deadline, datetime):
            days_until_deadline = (task.deadline.date() - schedule_date_only).days
            if days_until_deadline < 0:
                deadline_boost = 1000  # Past deadline - very high priority
            elif days_until_deadline == 0:
                deadline_boost = 500  # Due today
            elif days_until_deadline <= 1:
                deadline_boost = 200  # Due tomorrow
            elif days_until_deadline <= 3:
                deadline_boost = 100  # Due soon
            elif days_until_deadline <= 7:
                deadline_boost = 50  # Due this week
        
        # For recurring tasks, prefer scheduling on their specific day
        day_boost = 0.0
        if day_date:
            # Prefer scheduling recurring tasks on their designated day
            day_boost = 0.1
        
        return -(base_score + deadline_boost + day_boost)  # Negative for descending sort
    
    sorted_expanded_tasks = sorted(expanded_tasks, key=get_task_score)
    
    # Track which chunks of which tasks have been scheduled
    scheduled_chunks = {}  # (task_id, day_date) -> list of scheduled chunk indices
    
    # Schedule tasks across multiple days with task splitting
    for task, day_date in sorted_expanded_tasks:
        task_key = (task.id, day_date)
        chunks = task_chunks.get(task_key, [task.estimated_minutes])
        scheduled_chunks[task_key] = []
        
        # Determine which day slots this task can be scheduled on
        # For recurring tasks with a specific day, only consider that day
        # For tasks with deadlines, prioritize scheduling before deadline
        eligible_day_slots = []
        if day_date:
            # Recurring task - find the matching day slot
            for day_idx, day_slot in enumerate(day_slots):
                if day_slot["date"] == day_date:
                    eligible_day_slots = [(day_idx, day_slot)]
                    break
        elif task.deadline:
            # Task with deadline - only schedule on days before deadline
            deadline_date = task.deadline.date() if isinstance(task.deadline, datetime) else task.deadline
            for day_idx, day_slot in enumerate(day_slots):
                if day_slot["date"] <= deadline_date:
                    eligible_day_slots.append((day_idx, day_slot))
        else:
            # Regular task - can be scheduled on any day
            eligible_day_slots = [(idx, slot) for idx, slot in enumerate(day_slots)]
        
        for chunk_idx, chunk_minutes in enumerate(chunks):
            # Find the best day and time slot for this chunk
            best_slot = None
            best_score = -1
            
            for day_idx, day_slot in eligible_day_slots:
                # Check if this day has enough time
                if day_slot["current_time"] + timedelta(minutes=chunk_minutes) > day_slot["end"] + timedelta(hours=2):
                    continue
                
                # For tasks with deadlines, ensure we schedule before deadline
                if task.deadline:
                    deadline_datetime = task.deadline if isinstance(task.deadline, datetime) else datetime.combine(task.deadline, datetime.min.time())
                    if day_slot["current_time"] > deadline_datetime:
                        continue  # Skip slots after deadline
                
                # Calculate score for this time slot
                slot_hour = day_slot["current_time"].hour
                slot_energy = day_slot["energy"]
                slot_stress = day_slot["stress"]
                
                # Get ML score for this time slot
                score_data = task_scores.get(task.id) if task_scores else None
                if isinstance(score_data, dict):
                    base_score = score_data["score"]
                else:
                    base_score = task.priority / 5.0 if score_data is None else (score_data if isinstance(score_data, (int, float)) else task.priority / 5.0)
                
                # Adjust score based on current day/time slot
                time_boost = 0.0
                task_tags = task.tags or []
                if "morning" in task_tags and 6 <= slot_hour < 12:
                    time_boost += 0.15
                elif "afternoon" in task_tags and 12 <= slot_hour < 17:
                    time_boost += 0.15
                elif "evening" in task_tags and 17 <= slot_hour < 22:
                    time_boost += 0.15
                
                # Energy match
                energy_match = abs(slot_energy - task.energy_required)
                
                slot_score = (
                    base_score * 0.4 +
                    (1 - energy_match) * 0.3 +
                    (1 - slot_stress) * 0.2 +
                    time_boost * 0.1
                )
                
                if slot_score > best_score:
                    best_score = slot_score
                    best_slot = (day_idx, day_slot)
            
            if not best_slot:
                # Can't fit this chunk anywhere
                continue
            
            day_idx, day_slot = best_slot
            current_time = day_slot["current_time"]
            
            # Calculate task duration
            estimated_duration = chunk_minutes
            if task.completion_accuracy and task.completion_accuracy > 0:
                estimated_duration = int(estimated_duration * task.completion_accuracy)
            
            task_duration = timedelta(minutes=estimated_duration)
            chunk_end = current_time + task_duration
            
            # Check if chunk fits (with 2-hour overflow allowance)
            effective_end = day_slot["end"] + timedelta(hours=2)
            if chunk_end > effective_end:
                continue
            
            # Create schedule item for this chunk
            # Use task_key instead of task.id since scheduled_chunks uses (task_id, day_date) as key
            chunk_num = len(scheduled_chunks.get(task_key, [])) + 1
            total_chunks = len(chunks)
            chunk_label = f" (Part {chunk_num}/{total_chunks})" if total_chunks > 1 else ""
            
            # For recurring tasks, add day indicator to title
            if day_date:
                try:
                    day_label = day_date.strftime(" (%a %b %d)")
                    chunk_label = day_label + chunk_label
                except:
                    pass  # Skip if date formatting fails
            
            score_data = task_scores.get(task.id) if task_scores else None
            research_reasons = score_data.get("research_reasons", []) if isinstance(score_data, dict) else []
            
            # Get base_score for this task (used in reason string)
            score_data_for_reason = task_scores.get(task.id) if task_scores else None
            if isinstance(score_data_for_reason, dict):
                base_score_for_reason = score_data_for_reason["score"]
            else:
                base_score_for_reason = task.priority / 5.0
            
            goes_past_end = chunk_end > day_slot["end"]
            if goes_past_end:
                overflow_minutes = ((chunk_end - day_slot["end"]).total_seconds() / 60)
                base_reason = f"ML Score: {base_score_for_reason:.2f}, Priority: {task.priority}, Chunk {chunk_num}/{total_chunks} (Extends {overflow_minutes:.0f} min past work hours)"
                confidence_score = best_score * 0.85
            else:
                base_reason = f"ML Score: {base_score_for_reason:.2f}, Priority: {task.priority}, Chunk {chunk_num}/{total_chunks}"
                confidence_score = best_score
            
            if research_reasons:
                research_note = " | Research: " + ", ".join(research_reasons[:2])
                placement_reason = base_reason + research_note
            else:
                placement_reason = base_reason
            
            item = {
                "task_id": task.id,
                "task_title": task.title + chunk_label,
                "start_time": current_time,
                "end_time": chunk_end,
                "placement_reason": placement_reason,
                "confidence_score": confidence_score,
                "chunk_index": chunk_idx,
                "total_chunks": total_chunks
            }
            
            scheduled_items.append(item)
            scheduled_chunks[task_key].append(chunk_idx)
            
            # Update day slot
            energy_drain = task.energy_required * 0.15
            day_slot["energy"] = max(0.1, day_slot["energy"] - energy_drain)
            
            # Calculate break duration based on task characteristics and time remaining
            time_remaining_after = (day_slot["end"] - chunk_end).total_seconds() / 60
            hours_worked_today = (current_time - day_slot["start"]).total_seconds() / 3600
            
            # Longer breaks after longer tasks or after several hours
            if goes_past_end or time_remaining_after < 30:
                break_duration = 0
            elif hours_worked_today > 6:  # After 6 hours, need longer breaks
                break_duration = 15 if task.energy_required > 0.7 else 10
            elif hours_worked_today > 4:  # After 4 hours, moderate breaks
                break_duration = 10 if task.energy_required > 0.6 else 5
            elif chunk_minutes > 90:  # Long task chunk
                break_duration = 10 if task.energy_required > 0.7 else 5
            elif chunk_minutes > 60:  # Medium task chunk
                break_duration = 5 if task.energy_required > 0.6 else 3
            else:  # Short task chunk
                break_duration = 3 if task.energy_required > 0.5 else 2
            
            # Update current time for this day
            day_slot["current_time"] = chunk_end + timedelta(minutes=break_duration)
            
            # Energy recovery during break
            if break_duration > 0:
                recovery = min(0.1, break_duration * 0.01)  # Small energy recovery
                day_slot["energy"] = min(1.0, day_slot["energy"] + recovery)
    
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
            db=db,
            days_ahead=getattr(request, 'days_ahead', 7)  # Default to 7 days (week view)
        )
        
        if not scheduled_items:
            print(f"[WARNING] No scheduled items created for {len(tasks)} tasks")
            raise HTTPException(
                status_code=400, 
                detail=f"Could not schedule any tasks. This might be because tasks are too large for the available time window ({request.work_hours_start} - {request.work_hours_end} for {getattr(request, 'days_ahead', 7)} days). Try adjusting work hours or reducing task durations."
            )
        
        # Warn if not all tasks were scheduled
        if len(scheduled_items) < len(tasks):
            unscheduled_count = len(tasks) - len(scheduled_items)
            print(f"[WARNING] Only scheduled {len(scheduled_items)}/{len(tasks)} tasks. {unscheduled_count} tasks couldn't fit in the available time window.")
    
        # Determine schedule type based on days_ahead
        days_ahead = getattr(request, 'days_ahead', 7)
        schedule_type = "weekly" if days_ahead > 1 else "daily"
        
        # Create schedule
        schedule = Schedule(
            account_id=current_user.id,
            date=schedule_date,
            schedule_type=schedule_type,
            optimization_score=sum(item["confidence_score"] for item in scheduled_items) / len(scheduled_items) if scheduled_items else 0.0,
            optimization_context={
                "energy": energy,
                "stress": stress,
                "work_hours": {"start": request.work_hours_start, "end": request.work_hours_end},
                "days_ahead": days_ahead
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
                
                # Update task status (only set if this is the first chunk or if task isn't already scheduled)
                # For split tasks, we keep the task as scheduled but don't overwrite times
                if task.status != "scheduled" or not task.scheduled_start:
                    task.status = "scheduled"
                    # Set to first chunk's start time
                    first_chunk = next((item for item in scheduled_items if item["task_id"] == task.id), None)
                    if first_chunk:
                        task.scheduled_start = first_chunk["start_time"]
                        # Set end time to last chunk's end time
                        last_chunk = next((item for item in reversed(scheduled_items) if item["task_id"] == task.id), None)
                        if last_chunk:
                            task.scheduled_end = last_chunk["end_time"]
        
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
        
        # Provide more helpful error messages based on error type
        error_type = type(e).__name__
        error_msg = str(e)
        
        if "context" in error_msg.lower() or "vector" in error_msg.lower() or "index" in error_msg.lower():
            detail_msg = f"ML data processing error: {error_msg}. The system is using fallback scoring. Please check task data format."
        elif "predict" in error_msg.lower() or "model" in error_msg.lower() or "coordinator" in error_msg.lower():
            detail_msg = f"ML model error: {error_msg}. Models are using fallback priority-based scoring."
        elif "import" in error_msg.lower() or "module" in error_msg.lower():
            detail_msg = f"ML module import error: {error_msg}. Please check ML model files are present."
        elif "NoneType" in error_type or "AttributeError" in error_type:
            detail_msg = f"Data attribute error: {error_msg}. Please check all tasks have required fields."
        else:
            detail_msg = f"Schedule optimization error: {error_msg}. Please try again or check backend logs for details."
        
        raise HTTPException(
            status_code=500,
            detail=detail_msg
        )

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
