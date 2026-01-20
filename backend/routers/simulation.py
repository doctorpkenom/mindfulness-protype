from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models import SimulationRequest, SimulationResult
from backend.database import get_db
from backend.db_models import User as DBUser, Simulation as DBSimulation, Interaction, SystemLog
import sys
import os
from datetime import datetime
import random

# Import existing logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from simulated_testing.user_persona import UserPersona
from ml.online_coordinator import OnlineCoordinator
from processor.research_engine import ResearchEngine

router = APIRouter()

def run_enhanced_simulation(user: UserPersona, days: int, db: Session):
    """
    Run an enhanced simulation with database logging.
    """
    coordinator = OnlineCoordinator()
    engine = ResearchEngine()
    
    daily_rates = []
    all_interactions = []
    
    for day in range(days):
        user.next_day()
        context = user.get_context()
        
        # Get available strategies
        strategies = engine.strategies[:10]  # Sample of strategies
        
        # Let coordinator choose best strategy
        chosen_strategy = coordinator.select_strategy(context, strategies)
        
        # User reacts to strategy
        outcome, reward = user.react_to_strategy(chosen_strategy)
        
        # Log interaction to database
        interaction = Interaction(
            user_id=None,  # Will be set by caller
            context=context,
            strategy_name=chosen_strategy.get("name", "Unknown"),
            strategy_data=chosen_strategy,
            outcome=outcome
        )
        all_interactions.append(interaction)
        
        # Update coordinator with feedback
        coordinator.log_outcome(chosen_strategy["name"], outcome == "completed")
        
        # Calculate daily rate
        day_success = 1.0 if outcome == "completed" else 0.0
        daily_rates.append(day_success)
    
    # Calculate statistics
    week_1_avg = sum(daily_rates[:7]) / 7 if len(daily_rates) >= 7 else 0.0
    week_4_avg = sum(daily_rates[-7:]) / 7 if len(daily_rates) >= 7 else 0.0
    improvement = week_4_avg - week_1_avg
    
    return {
        "week_1_avg": week_1_avg,
        "week_4_avg": week_4_avg,
        "improvement": improvement,
        "daily_completion_rates": daily_rates,
        "interactions": all_interactions
    }

@router.post("/run", response_model=SimulationResult)
def run_user_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    """Run a 30-day simulation for a user and save results to database."""
    
    # Get user from database
    db_user = db.query(DBUser).filter(DBUser.name == req.user_name).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log simulation start
    log = SystemLog(
        level="INFO",
        component="simulation",
        message=f"Starting {req.days}-day simulation for {req.user_name}",
        context_data={"user_id": db_user.id, "days": req.days}
    )
    db.add(log)
    db.commit()
    
    try:
        # Create user persona from database user
        user_persona = UserPersona(
            name=db_user.name,
            base_stress=db_user.base_stress,
            base_energy=db_user.base_energy,
            resilience=db_user.resilience
        )
        
        # Run simulation
        results = run_enhanced_simulation(user_persona, req.days, db)
        
        # Save simulation to database
        simulation = DBSimulation(
            user_id=db_user.id,
            days=req.days,
            week_1_avg=results["week_1_avg"],
            week_4_avg=results["week_4_avg"],
            improvement=results["improvement"],
            daily_completion_rates=results["daily_completion_rates"]
        )
        db.add(simulation)
        
        # Save interactions
        for interaction in results["interactions"]:
            interaction.user_id = db_user.id
            db.add(interaction)
        
        db.commit()
        
        # Log success
        log = SystemLog(
            level="INFO",
            component="simulation",
            message=f"Simulation completed: {improvement:.2%} improvement",
            context_data={
                "user_id": db_user.id,
                "simulation_id": simulation.id,
                "improvement": results["improvement"]
            }
        )
        db.add(log)
        db.commit()
        
        return SimulationResult(
            user_name=db_user.name,
            week_1_avg=results["week_1_avg"],
            week_4_avg=results["week_4_avg"],
            improvement=results["improvement"],
            daily_completion_rates=results["daily_completion_rates"]
        )
        
    except Exception as e:
        # Log error
        log = SystemLog(
            level="ERROR",
            component="simulation",
            message=f"Simulation failed: {str(e)}",
            context_data={"user_id": db_user.id, "error": str(e)}
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.get("/history/{user_name}")
def get_simulation_history(user_name: str, db: Session = Depends(get_db)):
    """Get simulation history for a user."""
    
    db_user = db.query(DBUser).filter(DBUser.name == user_name).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    simulations = db.query(DBSimulation).filter(
        DBSimulation.user_id == db_user.id
    ).order_by(DBSimulation.created_at.desc()).all()
    
    return [
        {
            "id": sim.id,
            "days": sim.days,
            "week_1_avg": sim.week_1_avg,
            "week_4_avg": sim.week_4_avg,
            "improvement": sim.improvement,
            "created_at": sim.created_at.isoformat()
        }
        for sim in simulations
    ]
