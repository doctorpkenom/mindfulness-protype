from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from backend.models import CompositePlan, StrategyResponse

# Import existing logic
from processor.research_engine import ResearchEngine

router = APIRouter()
# Initialize engine once
engine = ResearchEngine() 

@router.get("/strategies", response_model=List[StrategyResponse])
def get_strategies(tag: Optional[str] = None):
    if tag:
        strats = engine.get_strategies_by_tag(tag)
    else:
        strats = engine.strategies
        
    results = []
    for s in strats:
        results.append(StrategyResponse(
            name=s.get("name", "Unknown"),
            logic=s.get("logic", ""),
            source_title=s.get("source_title"),
            source_id=s.get("source_id"),
            tags=s.get("tags", []),
            difficulty=s.get("difficulty")
        ))
    return results

@router.post("/plan/composite", response_model=CompositePlan)
def generate_plan(context: Dict[str, Any] = {}):
    """
    Generate a composite plan based on user context (e.g. {'stress': 'high'})
    """
    plan = engine.generate_composite_plan(user_context=context)
    return plan
