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

def run_simulation():
    print("=== INITIALIZING 30-DAY SIMULATION ===")
    
    # 1. Setup System
    engine = ResearchEngine()
    coordinator = OnlineCoordinator()
    all_strategies = engine.strategies
    
    # 2. Setup User: "The Burnout Student"
    # High stress, fluctuating energy, needs scaffolding
    user = UserPersona(name="Alex (Burnout Student)", base_stress=0.75, base_energy=0.4)
    
    print(f"User Profile: {user.name}")
    print(f"Base Stress: {user.base_stress}, Base Energy: {user.base_energy}")
    
    # Metrics
    history = []
    daily_completion_rates = []
    
    # 3. Run 30 Days
    for day in range(1, 31):
        user.next_day()
        print(f"\n--- Day {day} (Stress: {user.current_stress:.2f}, Energy: {user.current_energy:.2f}) ---")
        
        interactions = 5 # 5 distraction events per day
        successes = 0
        
        for i in range(interactions):
            # A. Get Context
            context = user.get_context()
            
            # B. ML Selects Strategy
            # Filter strategies slightly to simulate relevant options (e.g., only 5 random ones available to pick from)
            # In real app, this might be filtered by "Trigger" type. 
            # Here we pass ALL strategies to let the model pick the absolute best.
            chosen_strat = coordinator.select_strategy(context, all_strategies)
            
            # C. User Reacts
            outcome, reward = user.react_to_strategy(chosen_strat)
            
            # D. Feedback Loop
            coordinator.log_outcome(chosen_strat["name"], outcome == "completed")
            
            # Log
            if outcome == "completed": successes += 1
            print(f"  Event {i+1}: Suggested '{chosen_strat['name']}' -> {outcome.upper()}")
            
        rate = successes / interactions
        daily_completion_rates.append(rate)
        print(f"  >> Day {day} Completion Rate: {rate*100:.0f}%")

    # 4. Final Report
    print("\n\n=== SIMULATION REPORT ===")
    print(f"User: {user.name}")
    print(f"Total Days: 30")
    print(f"Interactions: {30 * 5}")
    
    avg_first_week = sum(daily_completion_rates[:7]) / 7
    avg_last_week = sum(daily_completion_rates[-7:]) / 7
    improvement = avg_last_week - avg_first_week
    
    print(f"Avg Completion Rate (Week 1): {avg_first_week*100:.1f}%")
    print(f"Avg Completion Rate (Week 4): {avg_last_week*100:.1f}%")
    print(f"Improvement: {improvement*100:+.1f}%")
    
    if improvement > 0:
        print("CONCLUSION: The ML Ensemble successfully adapted to the user's needs.")
    else:
        print("CONCLUSION: The model failed to improve user performance.")

if __name__ == "__main__":
    run_simulation()
