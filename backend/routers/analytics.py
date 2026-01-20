"""
Analytics API endpoints for dashboard metrics and insights.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.database import get_db
from backend.db_models import User, Interaction, Simulation, ModelPerformance, ResearchModule
from pydantic import BaseModel

router = APIRouter()

# Response Models
class DashboardStats(BaseModel):
    total_users: int
    total_interactions: int
    total_simulations: int
    avg_completion_rate: float
    active_users_7d: int
    top_strategies: List[Dict[str, Any]]

class ModelMetrics(BaseModel):
    model_name: str
    current_accuracy: float
    trend: str  # "improving", "declining", "stable"
    total_predictions: int
    last_updated: str

class InteractionTrend(BaseModel):
    date: str
    count: int
    success_rate: float

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics."""
    
    # Total counts
    total_users = db.query(User).count()
    total_interactions = db.query(Interaction).count()
    total_simulations = db.query(Simulation).count()
    
    # Average completion rate
    completed_count = db.query(Interaction).filter(
        Interaction.outcome == "completed"
    ).count()
    avg_completion_rate = completed_count / total_interactions if total_interactions > 0 else 0.0
    
    # Active users in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(func.count(func.distinct(Interaction.user_id))).filter(
        Interaction.timestamp >= seven_days_ago
    ).scalar() or 0
    
    # Top strategies by success rate
    strategy_stats = db.query(
        Interaction.strategy_name,
        func.count(Interaction.id).label('total'),
        func.sum(func.case([(Interaction.outcome == 'completed', 1)], else_=0)).label('completed')
    ).group_by(Interaction.strategy_name).all()
    
    top_strategies = [
        {
            "name": s.strategy_name,
            "total_uses": s.total,
            "success_rate": (s.completed / s.total) if s.total > 0 else 0.0
        }
        for s in strategy_stats
    ]
    top_strategies.sort(key=lambda x: x['success_rate'], reverse=True)
    
    return DashboardStats(
        total_users=total_users,
        total_interactions=total_interactions,
        total_simulations=total_simulations,
        avg_completion_rate=avg_completion_rate,
        active_users_7d=active_users,
        top_strategies=top_strategies[:5]
    )

@router.get("/models", response_model=List[ModelMetrics])
def get_model_metrics(db: Session = Depends(get_db)):
    """Get performance metrics for all ML models."""
    
    # Get latest performance for each model
    subquery = db.query(
        ModelPerformance.model_name,
        func.max(ModelPerformance.timestamp).label('max_timestamp')
    ).group_by(ModelPerformance.model_name).subquery()
    
    latest_performances = db.query(ModelPerformance).join(
        subquery,
        (ModelPerformance.model_name == subquery.c.model_name) &
        (ModelPerformance.timestamp == subquery.c.max_timestamp)
    ).all()
    
    results = []
    for perf in latest_performances:
        # Get previous performance to determine trend
        previous = db.query(ModelPerformance).filter(
            ModelPerformance.model_name == perf.model_name,
            ModelPerformance.timestamp < perf.timestamp
        ).order_by(desc(ModelPerformance.timestamp)).first()
        
        if previous:
            diff = perf.accuracy - previous.accuracy
            trend = "improving" if diff > 0.01 else "declining" if diff < -0.01 else "stable"
        else:
            trend = "stable"
        
        # Get total predictions (interactions where this model was used)
        total_predictions = db.query(Interaction).filter(
            Interaction.strategy_data.contains(perf.model_name)
        ).count()
        
        results.append(ModelMetrics(
            model_name=perf.model_name,
            current_accuracy=perf.accuracy,
            trend=trend,
            total_predictions=total_predictions,
            last_updated=perf.timestamp.isoformat()
        ))
    
    return results

@router.get("/interactions/trends")
def get_interaction_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get daily interaction trends."""
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Group by date
    daily_stats = db.query(
        func.date(Interaction.timestamp).label('date'),
        func.count(Interaction.id).label('count'),
        func.sum(func.case([(Interaction.outcome == 'completed', 1)], else_=0)).label('completed')
    ).filter(
        Interaction.timestamp >= cutoff
    ).group_by(func.date(Interaction.timestamp)).all()
    
    trends = [
        InteractionTrend(
            date=stat.date.isoformat(),
            count=stat.count,
            success_rate=(stat.completed / stat.count) if stat.count > 0 else 0.0
        )
        for stat in daily_stats
    ]
    
    return trends

@router.get("/research/usage")
def get_research_module_usage(db: Session = Depends(get_db)):
    """Get usage statistics for research modules."""
    
    modules = db.query(ResearchModule).all()
    
    return [
        {
            "module_id": m.module_id,
            "title": m.title,
            "times_used": m.times_used,
            "success_rate": m.success_rate,
            "avg_completion_time": m.avg_completion_time,
            "is_active": m.is_active
        }
        for m in modules
    ]

@router.get("/users/{user_id}/insights")
def get_user_insights(user_id: int, db: Session = Depends(get_db)):
    """Get detailed insights for a specific user."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # User interactions
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    
    if not interactions:
        return {
            "user_name": user.name,
            "total_interactions": 0,
            "message": "No interactions yet"
        }
    
    # Calculate insights
    total = len(interactions)
    completed = sum(1 for i in interactions if i.outcome == "completed")
    
    # Best time of day
    time_success = {}
    for interaction in interactions:
        time_key = interaction.context.get("time", "unknown")
        if time_key not in time_success:
            time_success[time_key] = {"total": 0, "completed": 0}
        time_success[time_key]["total"] += 1
        if interaction.outcome == "completed":
            time_success[time_key]["completed"] += 1
    
    best_time = max(
        time_success.items(),
        key=lambda x: x[1]["completed"] / x[1]["total"] if x[1]["total"] > 0 else 0
    )[0] if time_success else "unknown"
    
    # Best strategies
    strategy_success = {}
    for interaction in interactions:
        strat = interaction.strategy_name
        if strat not in strategy_success:
            strategy_success[strat] = {"total": 0, "completed": 0}
        strategy_success[strat]["total"] += 1
        if interaction.outcome == "completed":
            strategy_success[strat]["completed"] += 1
    
    best_strategies = sorted(
        [
            {
                "name": name,
                "success_rate": stats["completed"] / stats["total"] if stats["total"] > 0 else 0,
                "uses": stats["total"]
            }
            for name, stats in strategy_success.items()
        ],
        key=lambda x: x["success_rate"],
        reverse=True
    )[:3]
    
    return {
        "user_name": user.name,
        "total_interactions": total,
        "completion_rate": completed / total if total > 0 else 0,
        "best_time_of_day": best_time,
        "best_strategies": best_strategies,
        "avg_stress": user.base_stress,
        "avg_energy": user.base_energy,
        "resilience": user.resilience
    }
