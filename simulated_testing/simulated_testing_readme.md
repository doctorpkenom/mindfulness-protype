# Simulated Testing Documentation

The `simulated_testing` directory contains the logic for running offline simulations to validate the system's effectiveness before deploying to real users.

## 🧑‍💻 User Persona (`user_persona.py`)
This class simulates a human user with dynamic internal states. It is used to test if the ML model's recommendations actually help "improve" a user's state over time.

### State Model
Each persona has:
- **Base Stats**: `base_stress`, `base_energy`, `resilience`.
- **Dynamic Stats**: `current_stress`, `current_energy`, `streak`.

### Reaction Logic (`react_to_strategy`)
The core simulation method. It determines if a user "accepts" or "rejects" a proposed strategy based on their current state.

```python
def react_to_strategy(self, strategy):
    # 1. Fatigue Check
    if strategy.difficulty == "high" and self.energy < 0.4:
        prob_success -= 0.4 # User is too tired
        
    # 2. Stress Check
    if self.stress > 0.7:
        if "productivity" in strategy.tags:
             prob_success -= 0.5 # Stressed users reject work
             self.stress += 0.1 # And get more stressed
             
    # 3. Roll Dice
    if random() < prob_success:
        return "completed"
    else:
        return "ignored"
```

## 🔄 Simulation Loop
The simulation script (`run_simulation.py`) coordinates the interaction between the `UserPersona` and the `OnlineCoordinator` (ML Model) for a set number of days (e.g., 30 days).
