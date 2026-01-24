# Machine Learning Models

The `ml` directory contains the intelligence of the system. It uses a **Ensemble Voting System** (Council of Experts) for real-time strategy selection and a specialized **Schedule Optimizer** for calendar planning.

## 🧠 Architecture: The Council of Experts (`online_coordinator.py`)

The `OnlineCoordinator` acts as the central decision maker. Instead of a single "black box" model, it delegates decisions to specialized "expert" models, each optimizing for a specific psychological principle.

### Voting Mechanism
1. **Context Vector**: The user's state (Energy, Stress, Time, etc.) is normalized.
2. **Consultation**: Each expert model receives the context and available strategies.
3. **Scoring**: Experts score strategies from 0.0 to 1.0 based on their domain.
4. **Weighted Aggregation**: Scores are multiplied by the expert's trust weight and summed.

```python
# Simplified Logic
final_score = (
    StressPredictor.score() * 1.8 +
    FlowManager.score() * 1.2 +
    HabitOptimizer.score() * 1.0 +
    ...
)
```

## 🤖 Expert Models

### 1. Stress Predictor (`models/stress_predictor.py`)
- **Goal**: Prevent burnout using Sirois (2014) principles.
- **Logic**:
  - If `stress > 0.8` (Critical): Veto all productivity tasks. Recommend only `self-compassion` or `reflection`.
  - If `stress > 0.6` (High): Penalize high-difficulty tasks.
  - If `stress` is increasing (Trend): Suggest preventive mindfulness.

### 2. Schedule Optimizer (`models/schedule_optimizer.py`)
A heavy-duty model for placing tasks in the calendar. It uses **30+ features** to score every time slot.

- **Time-Matching**: Strictly enforces Morning/Evening constraints (e.g., "Dinner" must be 5-9 PM).
- **Flow State**: Awards bonus points if `Task Difficulty ≈ User Energy`.
- **Cognitive Load**: Penalizes long/hard tasks when predicted energy is low.

```python
def score_task_for_slot(task, slot_energy, slot_stress):
    # ...
    if slot_energy > 0.7 and difficulty > 0.6:
         base_score += 0.2 # Flow Bonus
    
    if slot_stress > 0.6 and difficulty > 0.6:
         base_score -= 0.3 # Stress Penalty
    # ...
```

### Other Experts
- **FlowManager**: Balances challenge vs. skill (Csikszentmihalyi).
- **HabitOptimizer**: Boosts recurring tasks to build consistency (Lally).
- **CuriosityTuner**: Prioritizes novel or exploration-based tasks when engagement is low.
- **TaskAnalyzer**: Uses semantic analysis to understand what a task *actually* is (e.g., identifying "writing code" vs "writing email").

## 🛠️ Usage
To use the coordinator in a simulation or API:

```python
coordinator = OnlineCoordinator()
strategy = coordinator.select_strategy(user_context, available_strategies)
coordinator.log_outcome(strategy["name"], success=True) # Learning step
```
