from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- User Models ---
class UserCreate(BaseModel):
    name: str
    stress: float
    energy: float
    resilience: float = 0.3

class UserResponse(BaseModel):
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
