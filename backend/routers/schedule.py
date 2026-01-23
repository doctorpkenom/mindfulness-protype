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
    
    # Morning tasks (6 AM - 12 PM)
    morning_keywords = ["breakfast", "morning", "wake", "coffee", "meditation", "yoga", "exercise", "workout", "gym", "run", "jog"]
    if any(kw in title_lower for kw in morning_keywords) or "morning" in tags:
        preferred_hours.append((6, 12))
        penalty_hours.extend([(12, 17), (17, 22)])  # Penalize afternoon/evening
    
    # Afternoon tasks (12 PM - 5 PM)
    afternoon_keywords = ["lunch", "afternoon", "meeting", "call", "conference"]
    if any(kw in title_lower for kw in afternoon_keywords) or "afternoon" in tags:
        preferred_hours.append((12, 17))
        penalty_hours.extend([(6, 12), (17, 22)])  # Penalize morning/evening
    
    # Evening tasks (5 PM - 10 PM)
    evening_keywords = ["dinner", "evening", "night", "supper", "cook", "prep", "meal prep", "cooking"]
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
    
    # Meal-related tasks
    meal_keywords = ["breakfast", "lunch", "dinner", "supper", "cook", "prep", "meal", "eat"]
    for kw in meal_keywords:
        if kw in title_lower:
            if kw in ["breakfast", "coffee"]:
                preferred_hours.append((6, 10))
                penalty_hours.extend([(10, 17), (17, 22)])
            elif kw in ["lunch"]:
                preferred_hours.append((11, 14))
                penalty_hours.extend([(6, 11), (14, 22)])
            elif kw in ["dinner", "supper", "cook", "prep", "meal prep", "cooking"]:
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
            # Get historical timer data for better estimates - enhanced with user patterns
            timer_history = {}
            user_time_patterns = {}  # task_id -> list of actual durations
            if account_id and db:
                from backend.db_models import TimerSession
                # Get recent timer sessions for this user to learn from actual times
                recent_timers = db.query(TimerSession).filter(
                    TimerSession.account_id == account_id,
                    TimerSession.status == "completed",
                    TimerSession.actual_seconds.isnot(None)
                ).order_by(TimerSession.completed_at.desc()).limit(100).all()  # Increased limit for better data
                
                # Build a map of task patterns -> actual durations
                for timer in recent_timers:
                    if timer.task_id:
                        task = db.query(Task).filter(Task.id == timer.task_id).first()
                        if task:
                            # Pattern-based history (category + difficulty)
                            key = f"{task.category or 'general'}_{task.difficulty}"
                            if key not in timer_history:
                                timer_history[key] = []
                            timer_history[key].append(timer.actual_seconds / 60)  # Convert to minutes
                            
                            # Task-specific history (for exact task matches)
                            if timer.task_id not in user_time_patterns:
                                user_time_patterns[timer.task_id] = []
                            user_time_patterns[timer.task_id].append(timer.actual_seconds / 60)
            
            # Make timer data available for ML scoring
            ml_timer_history = timer_history
            ml_user_patterns = user_time_patterns
            
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
                    
                    # Use timer history to adjust estimates if available - enhanced with user data
                    estimated_duration = task.estimated_minutes
                    if ml_timer_history or ml_user_patterns:
                        # Prefer task-specific history if available
                        if task.id in ml_user_patterns and len(ml_user_patterns[task.id]) >= 3:
                            # Use actual average for this specific task
                            avg_actual = sum(ml_user_patterns[task.id]) / len(ml_user_patterns[task.id])
                            estimated_duration = int(avg_actual)  # Use actual average
                            research_reason.append(f"User data: {len(ml_user_patterns[task.id])} previous completions")
                        else:
                            # Fall back to pattern-based history
                            task_key = f"{task.category or 'general'}_{task.difficulty}"
                            if task_key in ml_timer_history and len(ml_timer_history[task_key]) >= 3:
                                avg_actual = sum(ml_timer_history[task_key]) / len(ml_timer_history[task_key])
                                # Adjust estimate based on pattern - blend user data with estimate
                                estimated_duration = int((estimated_duration * 0.3 + avg_actual * 0.7))  # Weight actual data more
                                research_reason.append(f"Pattern data: {len(ml_timer_history[task_key])} similar tasks")
                        
                        # Boost score if estimates are accurate
                        if task.estimated_minutes and estimated_duration:
                            accuracy_ratio = estimated_duration / task.estimated_minutes
                            if 0.85 <= accuracy_ratio <= 1.15:
                                time_boost += 0.08  # Good estimate accuracy
                            elif accuracy_ratio > 1.3:
                                # Task takes longer - slight penalty but still schedule it
                                time_boost -= 0.03
                                research_reason.append("Note: Task often takes longer than estimated")
                    
                    # Apply research boost and time boost (capped at reasonable limits)
                    ml_score = min(1.0, max(0.0, base_ml_score + research_boost + time_boost))
                    
                    # Store research reasoning and adjusted duration for later use
                    task_scores[task_id] = {
                        "score": ml_score,
                        "research_reasons": research_reason,
                        "base_score": base_ml_score,
                        "research_boost": research_boost,
                        "time_boost": time_boost,
                        "adjusted_duration": estimated_duration  # Store for scheduling
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
                    "time_boost": 0.0,
                    "adjusted_duration": task.estimated_minutes
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
    
    # Prepare tasks for scheduling - NO CHUNKING, schedule as single blocks
    # Use user data to adjust time estimates
    task_durations = {}  # (task_id, day_date) -> adjusted duration in minutes
    for task, day_date in expanded_tasks:
        task_key = (task.id, day_date)
        
        # Get adjusted duration from ML scoring (uses user timer data)
        base_duration = task.estimated_minutes
        if task_scores and task.id in task_scores:
            score_data = task_scores[task.id]
            if isinstance(score_data, dict) and "adjusted_duration" in score_data:
                base_duration = score_data["adjusted_duration"]
        
        # Apply completion accuracy if available
        if task.completion_accuracy and task.completion_accuracy > 0:
            adjusted_duration = int(base_duration * task.completion_accuracy)
        else:
            adjusted_duration = base_duration
        
        task_durations[task_key] = adjusted_duration
    
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
    
    # Track which tasks have been scheduled to prevent duplicates
    scheduled_task_keys = set()
    
    # Schedule tasks across multiple days - NO CHUNKING, single blocks only
    for task, day_date in sorted_expanded_tasks:
        task_key = (task.id, day_date)
        
        # Skip if already scheduled (prevent duplicates)
        if task_key in scheduled_task_keys:
            continue
        
        # Get adjusted duration (uses user timer data)
        task_minutes = task_durations.get(task_key, task.estimated_minutes)
        
        # Determine which day slots this task can be scheduled on
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
        
        # Find the best day and time slot for this task
        best_slot = None
        best_score = -1
        
        # Calculate overflow allowance for urgent tasks (outside loop for efficiency)
        overflow_allowance = 30 if task.priority >= 4 or (task.deadline and isinstance(task.deadline, datetime) and (task.deadline.date() - schedule_date_only).days <= 1) else 0
        
        for day_idx, day_slot in eligible_day_slots:
            # Calculate available time including buffer for breaks
            available_time = (day_slot["end"] - day_slot["current_time"]).total_seconds() / 60
            
            # Need time for task + minimum break (5 minutes) + buffer (2 minutes)
            required_time = task_minutes + 7  # Task + break + buffer
            
            # Check if task fits (with small overflow allowance for urgent tasks only)
            if available_time < required_time - overflow_allowance:
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
            
            # Intelligently adjust score based on task content and time slot
            time_boost = 0.0
            time_penalty = 0.0  # Initialize time_penalty
            
            # Infer appropriate time slots from task content
            time_preferences = infer_appropriate_time_slot(task)
            preferred_hours = time_preferences["preferred_hours"]
            penalty_hours = time_preferences["penalty_hours"]
            
            # Check if current slot is in preferred hours
            in_preferred = False
            for start_hour, end_hour in preferred_hours:
                if start_hour <= slot_hour < end_hour:
                    in_preferred = True
                    time_boost += 0.5  # Strong boost for correct time
                    break
            
            # Check if current slot is in penalty hours (wrong time)
            in_penalty = False
            for start_hour, end_hour in penalty_hours:
                if start_hour <= slot_hour < end_hour:
                    in_penalty = True
                    time_penalty += 0.6  # Strong penalty for wrong time
                    break
            
            # Fallback: check tags if no intelligent inference
            if not preferred_hours and not penalty_hours:
                task_tags = task.tags or []
                if "morning" in task_tags and 6 <= slot_hour < 12:
                    time_boost += 0.3
                elif "afternoon" in task_tags and 12 <= slot_hour < 17:
                    time_boost += 0.3
                elif "evening" in task_tags and 17 <= slot_hour < 22:
                    time_boost += 0.3
                elif "morning" in task_tags and not (6 <= slot_hour < 12):
                    time_penalty += 0.4
                elif "afternoon" in task_tags and not (12 <= slot_hour < 17):
                    time_penalty += 0.4
                elif "evening" in task_tags and not (17 <= slot_hour < 22):
                    time_penalty += 0.4
                
                # Check for preferred_time tag
                for tag in task_tags:
                    if tag.startswith("preferred_time:"):
                        try:
                            preferred_hour = int(tag.split(":")[1].split(":")[0])
                            if abs(slot_hour - preferred_hour) <= 1:  # Within 1 hour of preferred time
                                time_boost += 0.4
                            elif abs(slot_hour - preferred_hour) > 3:  # More than 3 hours away
                                time_penalty += 0.3
                        except:
                            pass
            
            # Energy match
            energy_match = abs(slot_energy - task.energy_required)
            
            # Penalize if task would extend significantly past work hours
            task_end_time = day_slot["current_time"] + timedelta(minutes=task_minutes)
            overflow_penalty = 0.0
            if task_end_time > day_slot["end"]:
                overflow_minutes = ((task_end_time - day_slot["end"]).total_seconds() / 60)
                if overflow_minutes > 60:  # More than 1 hour overflow
                    overflow_penalty = 0.3
                elif overflow_minutes > 30:  # More than 30 min overflow
                    overflow_penalty = 0.15
            
            # Time appropriateness is now a major factor (40% weight)
            # This ensures tasks are scheduled at appropriate times
            slot_score = (
                base_score * 0.3 +           # ML score (reduced from 0.4)
                (1 - energy_match) * 0.2 +   # Energy match (reduced from 0.3)
                (1 - slot_stress) * 0.1 +   # Stress level (reduced from 0.2)
                time_boost * 0.3 -          # Time boost (increased from 0.1, now major factor)
                time_penalty * 0.3 -        # Time penalty (new, heavily penalizes wrong times)
                overflow_penalty * 0.2       # Overflow penalty (reduced from direct subtraction)
            )
            
            if slot_score > best_score:
                best_score = slot_score
                best_slot = (day_idx, day_slot)
        
        if not best_slot:
            # Can't fit this task anywhere
            continue
        
        day_idx, day_slot = best_slot
        current_time = day_slot["current_time"]
        
        # Use adjusted duration from user data
        task_duration = timedelta(minutes=task_minutes)
        task_end = current_time + task_duration
        
        # Check if task fits (with overflow allowance for urgent tasks)
        effective_end = day_slot["end"] + timedelta(minutes=overflow_allowance)
        if task_end > effective_end:
            continue
        
        # For recurring tasks, add day indicator to title
        task_label = ""
        if day_date:
            try:
                task_label = day_date.strftime(" (%a %b %d)")
            except:
                pass
        
        score_data = task_scores.get(task.id) if task_scores else None
        research_reasons = score_data.get("research_reasons", []) if isinstance(score_data, dict) else []
        
        # Get base_score for this task (used in reason string)
        score_data_for_reason = task_scores.get(task.id) if task_scores else None
        if isinstance(score_data_for_reason, dict):
            base_score_for_reason = score_data_for_reason["score"]
        else:
            base_score_for_reason = task.priority / 5.0
        
        goes_past_end = task_end > day_slot["end"]
        if goes_past_end:
            overflow_minutes = ((task_end - day_slot["end"]).total_seconds() / 60)
            base_reason = f"ML Score: {base_score_for_reason:.2f}, Priority: {task.priority} (Extends {overflow_minutes:.0f} min past work hours)"
            confidence_score = best_score * 0.85
        else:
            base_reason = f"ML Score: {base_score_for_reason:.2f}, Priority: {task.priority}"
            confidence_score = best_score
        
        if research_reasons:
            research_note = " | Research: " + ", ".join(research_reasons[:2])
            placement_reason = base_reason + research_note
        else:
            placement_reason = base_reason
        
        item = {
            "task_id": task.id,
            "task_title": task.title + task_label,
            "start_time": current_time,
            "end_time": task_end,
            "placement_reason": placement_reason,
            "confidence_score": confidence_score
        }
        
        scheduled_items.append(item)
        scheduled_task_keys.add(task_key)
        
        # Update day slot
        energy_drain = task.energy_required * 0.15
        day_slot["energy"] = max(0.1, day_slot["energy"] - energy_drain)
        
        # Calculate break duration based on task characteristics and time remaining
        time_remaining_after = (day_slot["end"] - task_end).total_seconds() / 60
        hours_worked_today = (current_time - day_slot["start"]).total_seconds() / 3600
        
        # Improved break calculation - prevents overlap and accounts for user patterns
        if goes_past_end or time_remaining_after < 15:
            break_duration = 0  # No break if at end of day or very little time left
        elif hours_worked_today > 6:  # After 6 hours, need longer breaks
            break_duration = 15 if task.energy_required > 0.7 else 10
        elif hours_worked_today > 4:  # After 4 hours, moderate breaks
            break_duration = 10 if task.energy_required > 0.6 else 5
        elif task_minutes > 120:  # Long task (>2 hours)
            break_duration = 15 if task.energy_required > 0.7 else 10
        elif task_minutes > 90:  # Long task (90-120 min)
            break_duration = 10 if task.energy_required > 0.6 else 5
        elif task_minutes > 60:  # Medium task (60-90 min)
            break_duration = 5 if task.energy_required > 0.5 else 3
        else:  # Short task (<60 min)
            break_duration = 3 if task.energy_required > 0.4 else 2
        
        # Ensure break doesn't cause overlap with next task
        # Add buffer to prevent tight scheduling
        break_duration = max(break_duration, 2)  # Minimum 2 minute buffer between tasks
        
        # Update current time for this day (task end + break)
        day_slot["current_time"] = task_end + timedelta(minutes=break_duration)
        
        # Energy recovery during break
        if break_duration > 0:
            recovery = min(0.15, break_duration * 0.015)  # Improved energy recovery
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
                
                # Update task status - single block scheduling
                if task.status != "scheduled" or not task.scheduled_start:
                    task.status = "scheduled"
                    # Find the scheduled item for this task
                    scheduled_item = next((item for item in scheduled_items if item["task_id"] == task.id), None)
                    if scheduled_item:
                        task.scheduled_start = scheduled_item["start_time"]
                        task.scheduled_end = scheduled_item["end_time"]
        
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
