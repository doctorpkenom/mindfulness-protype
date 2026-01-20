"""
Debug and testing API endpoints for system diagnostics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.database import get_db, reset_db
from backend.db_models import SystemLog, ModelPerformance, User, Interaction
import sys
import os

# Import ML components
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ml.online_coordinator import OnlineCoordinator
from processor.research_engine import ResearchEngine

router = APIRouter()

# Request/Response Models
class LogEntry(BaseModel):
    level: str
    component: str
    message: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None

class TestModelRequest(BaseModel):
    model_name: str
    context: Dict[str, Any]
    strategies: List[Dict[str, Any]]

class TestModelResponse(BaseModel):
    model_name: str
    predictions: Dict[str, float]
    best_strategy: str
    confidence: float

@router.get("/logs", response_model=List[LogEntry])
def get_system_logs(
    limit: int = 100,
    level: Optional[str] = None,
    component: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get system logs for debugging."""
    
    query = db.query(SystemLog)
    
    if level:
        query = query.filter(SystemLog.level == level.upper())
    if component:
        query = query.filter(SystemLog.component == component)
    
    logs = query.order_by(desc(SystemLog.timestamp)).limit(limit).all()
    
    return [
        LogEntry(
            level=log.level,
            component=log.component,
            message=log.message,
            timestamp=log.timestamp.isoformat(),
            context=log.context_data
        )
        for log in logs
    ]

@router.post("/logs")
def create_log(
    level: str,
    component: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Create a new log entry."""
    
    log = SystemLog(
        level=level.upper(),
        component=component,
        message=message,
        context_data=context
    )
    db.add(log)
    db.commit()
    
    return {"status": "logged", "level": level, "component": component}

@router.post("/test/model", response_model=TestModelResponse)
def test_model(request: TestModelRequest, db: Session = Depends(get_db)):
    """Test a specific ML model with given context and strategies."""
    
    try:
        coordinator = OnlineCoordinator()
        
        # Find the requested model
        target_model = None
        for expert in coordinator.experts:
            if expert.name == request.model_name:
                target_model = expert
                break
        
        if not target_model:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{request.model_name}' not found"
            )
        
        # Preprocess context
        ctx_vec = coordinator.preprocessor.normalize_context(request.context)
        
        # Get predictions
        predictions = target_model.predict(ctx_vec, request.strategies)
        
        # Find best strategy
        best_strategy_name = max(predictions, key=predictions.get)
        confidence = predictions[best_strategy_name]
        
        # Log this test
        log = SystemLog(
            level="DEBUG",
            component="model_test",
            message=f"Tested {request.model_name} with {len(request.strategies)} strategies",
            context_data={
                "model": request.model_name,
                "context": request.context,
                "best_strategy": best_strategy_name,
                "confidence": confidence
            }
        )
        db.add(log)
        db.commit()
        
        return TestModelResponse(
            model_name=request.model_name,
            predictions=predictions,
            best_strategy=best_strategy_name,
            confidence=confidence
        )
        
    except Exception as e:
        # Log error
        log = SystemLog(
            level="ERROR",
            component="model_test",
            message=f"Model test failed: {str(e)}",
            context_data={"model": request.model_name, "error": str(e)}
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/research")
def test_research_engine(db: Session = Depends(get_db)):
    """Test the research engine and return diagnostic info."""
    
    try:
        engine = ResearchEngine()
        
        info = {
            "status": "ok",
            "total_modules": len(engine.modules),
            "total_strategies": len(engine.strategies),
            "modules": [
                {
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "strategies_count": len(m.get("actionable_strategies", []))
                }
                for m in engine.modules
            ],
            "tags": list(set(
                tag for strat in engine.strategies 
                for tag in strat.get("tags", [])
            ))
        }
        
        # Log test
        log = SystemLog(
            level="DEBUG",
            component="research_test",
            message=f"Research engine test: {len(engine.modules)} modules, {len(engine.strategies)} strategies",
            context_data=info
        )
        db.add(log)
        db.commit()
        
        return info
        
    except Exception as e:
        log = SystemLog(
            level="ERROR",
            component="research_test",
            message=f"Research engine test failed: {str(e)}",
            context_data={"error": str(e)}
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/weights/{model_name}")
def get_model_weights(model_name: str, db: Session = Depends(get_db)):
    """Get current weights for a specific model."""
    
    try:
        coordinator = OnlineCoordinator()
        
        target_model = None
        for expert in coordinator.experts:
            if expert.name == model_name:
                target_model = expert
                break
        
        if not target_model:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        return {
            "model_name": model_name,
            "weights": target_model.weights,
            "weight_count": len(target_model.weights)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/reset")
def reset_database(confirm: bool = False, db: Session = Depends(get_db)):
    """Reset the entire database. USE WITH CAUTION!"""
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must confirm database reset by passing confirm=true"
        )
    
    try:
        # Log before reset
        log = SystemLog(
            level="WARNING",
            component="database",
            message="Database reset initiated"
        )
        db.add(log)
        db.commit()
        db.close()
        
        # Reset
        reset_db()
        
        return {"status": "success", "message": "Database reset complete"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/info")
def get_system_info(db: Session = Depends(get_db)):
    """Get system information and health status."""
    
    # Count records
    user_count = db.query(User).count()
    interaction_count = db.query(Interaction).count()
    log_count = db.query(SystemLog).count()
    
    # Recent activity
    recent_interaction = db.query(Interaction).order_by(
        desc(Interaction.timestamp)
    ).first()
    
    return {
        "status": "operational",
        "database": {
            "users": user_count,
            "interactions": interaction_count,
            "logs": log_count
        },
        "last_interaction": recent_interaction.timestamp.isoformat() if recent_interaction else None,
        "ml_models": [
            "habit_optimizer",
            "stress_predictor",
            "curiosity_tuner",
            "flow_manager"
        ],
        "research_modules": len(ResearchEngine().modules)
    }
