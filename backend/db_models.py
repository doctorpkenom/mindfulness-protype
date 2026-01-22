"""
SQLAlchemy database models for persistent storage.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    """User/Persona model for storing simulated users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    base_stress = Column(Float, nullable=False)
    base_energy = Column(Float, nullable=False)
    resilience = Column(Float, default=0.3)
    
    # Relationships
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Interaction(Base):
    """Record of each user interaction with the system."""
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Context at time of interaction
    context = Column(JSON, nullable=False)  # {"stress": "high", "energy": "low", "time": "evening"}
    
    # Strategy presented
    strategy_name = Column(String(200), nullable=False)
    strategy_data = Column(JSON, nullable=False)  # Full strategy object
    
    # Outcome
    outcome = Column(String(50), nullable=False)  # "completed", "started", "ignored"
    completion_time = Column(Float, nullable=True)  # Time in seconds to complete
    
    # Feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 rating
    user_feedback = Column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="interactions")
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Simulation(Base):
    """Record of longitudinal simulations."""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Simulation parameters
    days = Column(Integer, default=30)
    
    # Results
    week_1_avg = Column(Float, nullable=False)
    week_4_avg = Column(Float, nullable=False)
    improvement = Column(Float, nullable=False)
    daily_completion_rates = Column(JSON, nullable=False)  # Array of daily rates
    
    # Metadata
    ml_model_weights = Column(JSON, nullable=True)  # Snapshot of model weights used
    
    # Relationship
    user = relationship("User", back_populates="simulations")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class ModelPerformance(Base):
    """Track ML model performance over time."""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    
    model_name = Column(String(100), nullable=False, index=True)
    
    # Performance metrics
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Training info
    training_samples = Column(Integer, nullable=False)
    training_duration = Column(Float, nullable=True)  # In seconds
    
    # Model weights snapshot
    weights = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class ResearchModule(Base):
    """Track which research modules are active and their usage."""
    __tablename__ = "research_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    module_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    
    # Usage statistics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_completion_time = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Full module data
    module_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemLog(Base):
    """System logs for debugging and monitoring."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    level = Column(String(20), nullable=False, index=True)  # "INFO", "WARNING", "ERROR", "DEBUG"
    component = Column(String(100), nullable=False, index=True)  # "ml_coordinator", "research_engine", etc.
    message = Column(Text, nullable=False)
    
    # Additional context
    context_data = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# ============================================================================
# NEW MODELS FOR PRODUCTIVITY APP
# ============================================================================

class Account(Base):
    """Authenticated user accounts for the productivity app."""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # User preferences for ML personalization
    preferred_work_hours = Column(JSON, nullable=True)  # {"start": "09:00", "end": "17:00"}
    energy_patterns = Column(JSON, nullable=True)  # {"morning": 0.8, "afternoon": 0.6, "evening": 0.4}
    focus_duration_preference = Column(Integer, default=25)  # Default Pomodoro length
    
    # Relationships
    tasks = relationship("Task", back_populates="account", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="account", cascade="all, delete-orphan")
    timer_sessions = relationship("TimerSession", back_populates="account", cascade="all, delete-orphan")
    ml_weights = relationship("UserMLWeights", back_populates="account", cascade="all, delete-orphan", uselist=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Task(Base):
    """User tasks with time estimates and metadata."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    estimated_minutes = Column(Integer, nullable=False)  # User's estimate
    actual_minutes = Column(Integer, nullable=True)  # Actual time taken (after completion)
    
    # Task properties for ML optimization
    priority = Column(Integer, default=3)  # 1-5 scale
    difficulty = Column(Integer, default=3)  # 1-5 scale
    energy_required = Column(Float, default=0.5)  # 0.0-1.0
    focus_required = Column(Float, default=0.5)  # 0.0-1.0
    category = Column(String(50), nullable=True)  # "work", "personal", "health", etc.
    tags = Column(JSON, nullable=True)  # ["urgent", "creative", "admin"]
    
    # Status
    status = Column(String(20), default="pending", index=True)  # "pending", "scheduled", "in_progress", "completed", "cancelled"
    scheduled_start = Column(DateTime, nullable=True, index=True)
    scheduled_end = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Deadline and Recurrence
    deadline = Column(DateTime, nullable=True, index=True)  # Task deadline (date and time)
    recurrence_pattern = Column(String(50), nullable=True)  # "daily", "weekly", "monthly", "custom", "none"
    recurrence_end_date = Column(DateTime, nullable=True)  # When to stop recurring
    custom_recurrence_days = Column(Integer, nullable=True)  # For custom recurrence (e.g., every 3 days)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # For recurring task chains
    
    # ML learning data
    completion_accuracy = Column(Float, nullable=True)  # estimated vs actual time ratio
    user_satisfaction = Column(Integer, nullable=True)  # 1-5 rating after completion
    
    # Relationships
    account = relationship("Account", back_populates="tasks")
    schedule_items = relationship("ScheduleItem", back_populates="task", cascade="all, delete-orphan")
    timer_sessions = relationship("TimerSession", back_populates="task", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Schedule(Base):
    """ML-optimized daily/weekly schedules for users."""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Schedule metadata
    date = Column(DateTime, nullable=False, index=True)  # Date this schedule is for
    schedule_type = Column(String(20), default="daily")  # "daily", "weekly"
    
    # ML optimization info
    optimization_score = Column(Float, nullable=True)  # How well tasks are optimized
    ml_model_version = Column(String(50), nullable=True)  # Which ML models were used
    optimization_context = Column(JSON, nullable=True)  # Context used for optimization
    
    # Relationships
    account = relationship("Account", back_populates="schedules")
    items = relationship("ScheduleItem", back_populates="schedule", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScheduleItem(Base):
    """Individual task items within a schedule."""
    __tablename__ = "schedule_items"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    
    # Scheduled time
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    
    # ML reasoning
    placement_reason = Column(Text, nullable=True)  # Why ML placed this here
    confidence_score = Column(Float, nullable=True)  # ML confidence in this placement
    
    # Status
    status = Column(String(20), default="scheduled")  # "scheduled", "started", "completed", "skipped"
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="items")
    task = relationship("Task", back_populates="schedule_items")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class TimerSession(Base):
    """Timer sessions for task tracking."""
    __tablename__ = "timer_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    
    # Timer details
    duration_seconds = Column(Integer, nullable=False)  # Planned duration
    actual_seconds = Column(Integer, nullable=True)  # Actual duration (if completed)
    
    # Status
    status = Column(String(20), default="active")  # "active", "paused", "completed", "cancelled"
    started_at = Column(DateTime, nullable=False, index=True)
    paused_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Focus metrics (for ML learning)
    interruptions = Column(Integer, default=0)
    focus_score = Column(Float, nullable=True)  # 0.0-1.0 based on interruptions
    
    # Relationships
    account = relationship("Account", back_populates="timer_sessions")
    task = relationship("Task", back_populates="timer_sessions")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class UserMLWeights(Base):
    """Personalized ML model weights per user for better optimization."""
    __tablename__ = "user_ml_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), unique=True, nullable=False, index=True)
    
    # Personalized weights for each ML model
    habit_optimizer_weight = Column(Float, default=1.0)
    stress_predictor_weight = Column(Float, default=1.8)
    curiosity_tuner_weight = Column(Float, default=1.0)
    flow_manager_weight = Column(Float, default=1.2)
    attention_manager_weight = Column(Float, default=1.1)
    motivation_booster_weight = Column(Float, default=1.3)
    zeigarnik_tracker_weight = Column(Float, default=0.9)
    
    # Learning history
    total_interactions = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    account = relationship("Account", back_populates="ml_weights")
