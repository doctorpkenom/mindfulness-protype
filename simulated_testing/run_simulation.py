import sys
import os
import random
import sys
import os
import random
# import matplotlib.pyplot as plt # Removed to avoid dependency issues

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.online_coordinator import OnlineCoordinator
from processor.research_engine import ResearchEngine
from simulated_testing.user_persona import UserPersona

def run_simulation(user: UserPersona = None):
    """
    Runs a 30-day simulation for the given user.
    Returns a dictionary of results for visualization.
    """
    print(f"=== INITIALIZING 30-DAY SIMULATION FOR {user.name if user else 'Default'} ===")
    
    # 1. Setup System
    engine = ResearchEngine()
    coordinator = OnlineCoordinator()
    all_strategies = engine.strategies
    
    # 2. Setup User (if not provided, create default)
    if not user:
        user = UserPersona(name="Alex (Burnout Student)", base_stress=0.75, base_energy=0.4)
    
    # Metrics
    daily_completion_rates = []
    daily_stress = []
    daily_energy = []
    
    # 3. Run 30 Days
    for day in range(1, 31):
        user.next_day()
        
        interactions = 5 # 5 distraction events per day
        successes = 0
        
        for i in range(interactions):
            # A. Get Context
            context = user.get_context()
            
            # B. ML Selects Strategy
            chosen_strat = coordinator.select_strategy(context, all_strategies)
            
            # C. User Reacts
            outcome, reward = user.react_to_strategy(chosen_strat)
            
            # D. Feedback Loop
            coordinator.log_outcome(chosen_strat["name"], outcome == "completed")
            
            # Log
            if outcome == "completed": successes += 1
            
        rate = successes / interactions
        daily_completion_rates.append(rate)
        daily_stress.append(user.current_stress)
        daily_energy.append(user.current_energy)

    # 4. Compile Results
    avg_first_week = sum(daily_completion_rates[:7]) / 7
    avg_last_week = sum(daily_completion_rates[-7:]) / 7
    improvement = avg_last_week - avg_first_week
    
    results = {
        "user_name": user.name,
        "daily_completion_rates": daily_completion_rates,
        "daily_stress": daily_stress,
        "daily_energy": daily_energy,
        "week_1_avg": avg_first_week,
        "week_4_avg": avg_last_week,
        "improvement": improvement
    }
    
    return results

if __name__ == "__main__":
    # Test run
    res = run_simulation()
    print(f"Simulation Complete. Improvement: {res['improvement']*100:+.1f}%")
