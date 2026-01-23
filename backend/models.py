from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Authentication Models ---
class UserSignup(BaseModel):
    email: EmailStr
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- User Models (Legacy - for simulations) ---
class UserCreate(BaseModel):
    name: str
    stress: float
    energy: float
    resilience: float = 0.3

class UserResponseLegacy(BaseModel):
    name: str
    base_stress: float
    base_energy: float
    resilience: float

# --- Research Models ---
class StrategyResponse(BaseModel):
    name: str
    logic: str
    source_title: Optional[str] = None
    source_id: Optional[str] = None
    tags: List[str] = []
    difficulty: Optional[str] = None

class PlanStep(BaseModel):
    phase: str
    strategy: str
    logic: str
    source: Optional[str] = None

class CompositePlan(BaseModel):
    name: str
    rationale: str
    steps: List[PlanStep]
    adaptation_note: Optional[str] = None

# --- Simulation Models ---
class SimulationRequest(BaseModel):
    user_name: str
    days: int = 30

class SimulationResult(BaseModel):
    user_name: str
    week_1_avg: float
    week_4_avg: float
    improvement: float
    daily_completion_rates: List[float]

# --- Task Models ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_minutes: int
    priority: int = 3  # 1-5
    difficulty: int = 3  # 1-5
    energy_required: float = 0.5  # 0.0-1.0
    focus_required: float = 0.5  # 0.0-1.0
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    deadline: Optional[str] = None  # ISO datetime string
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly", "custom", "none"
    recurrence_end_date: Optional[str] = None  # ISO datetime string
    custom_recurrence_days: Optional[int] = None  # For custom recurrence (e.g., every 3 days)

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_minutes: Optional[int] = None
    priority: Optional[int] = None
    difficulty: Optional[int] = None
    energy_required: Optional[float] = None
    focus_required: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    user_satisfaction: Optional[int] = None
    deadline: Optional[str] = None  # ISO datetime string
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly", "custom", "none"
    recurrence_end_date: Optional[str] = None  # ISO datetime string
    custom_recurrence_days: Optional[int] = None  # For custom recurrence (e.g., every 3 days)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    estimated_minutes: int
    deadline: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    custom_recurrence_days: Optional[int] = None
    actual_minutes: Optional[int]
    priority: int
    difficulty: int
    energy_required: float
    focus_required: float
    category: Optional[str]
    tags: Optional[List[str]]
    status: str
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    completed_at: Optional[datetime]
    completion_accuracy: Optional[float]
    user_satisfaction: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Schedule Models ---
class ScheduleOptimizeRequest(BaseModel):
    date: str  # ISO date string
    task_ids: List[int]  # Tasks to schedule
    work_hours_start: str = "06:00"  # HH:MM - full day schedule
    work_hours_end: str = "22:00"  # HH:MM - full day schedule
    current_energy: Optional[float] = None
    current_stress: Optional[float] = None
    days_ahead: int = 7  # Number of days to schedule ahead (default 7 for week view)

class ScheduleItemResponse(BaseModel):
    id: int
    task_id: int
    task_title: str  # Required field - will be populated from task relationship
    start_time: datetime
    end_time: datetime
    placement_reason: Optional[str]
    confidence_score: Optional[float]
    status: str
    
    class Config:
        from_attributes = True

class ScheduleResponse(BaseModel):
    id: int
    date: datetime
    schedule_type: str
    optimization_score: Optional[float]
    items: List[ScheduleItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Timer Models ---
class TimerStartRequest(BaseModel):
    task_id: Optional[int] = None
    duration_seconds: int  # e.g., 1500 for 25 minutes

class TimerResponse(BaseModel):
    id: int
    task_id: Optional[int]
    duration_seconds: int
    actual_seconds: Optional[int]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    interruptions: int
    focus_score: Optional[float]
    
    class Config:
        from_attributes = True
