from fastapi import APIRouter, HTTPException
from backend.models import SimulationRequest, SimulationResult

# Import existing logic
from simulated_testing.user_manager import UserManager
from simulated_testing.run_simulation import run_simulation

router = APIRouter()
user_manager = UserManager()

@router.post("/run", response_model=SimulationResult)
def run_user_simulation(req: SimulationRequest):
    user = user_manager.get_user(req.user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Run the existing simulation logic
    # Note: run_simulation might need a 'days' argument if it supports it, 
    # but based on reading it seems fixed to 30 days or internal logic.
    # We'll just call it as is.
    try:
        results = run_simulation(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

    return SimulationResult(
        user_name=user.name,
        week_1_avg=results.get("week_1_avg", 0.0),
        week_4_avg=results.get("week_4_avg", 0.0),
        improvement=results.get("improvement", 0.0),
        daily_completion_rates=results.get("daily_completion_rates", [])
    )
