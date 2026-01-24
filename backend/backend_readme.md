# Backend Documentation

The `backend` directory contains the core logic, API endpoints, and database models for the Mindfulness Productivity Application. It is built using **FastAPI** and uses **SQLAlchemy** for ORM interactions with a SQLite database.

## 📂 Project Structure

```
backend/
├── main.py              # Application entry point, CORS, and router inclusion
├── db_models.py         # SQLAlchemy database models (User, Task, Schedule, etc.)
├── database.py          # Database connection and session management
├── auth.py              # Authentication logic (JWT, password hashing)
├── routers/             # API Endpoints organized by functionality
│   ├── auth.py          # User registration and login
│   ├── tasks.py         # Task management (CRUD)
│   ├── schedule.py      # ML-based schedule optimization algorithms
│   ├── simulation.py    # Simulation engine logic
│   ├── research.py      # Research strategy endpoints
│   └── ...
└── ...
```

## 🧠 Key Algorithms

### 1. ML-Optimized Schedule Logic (`routers/schedule.py`)
The most complex algorithm in the backend is the `optimize_schedule_with_ml` function. It uses a multi-factor approach to place tasks in optimal time slots.

#### A. Time Slot Inference
Before scheduling, the system infers "preferred" and "penalty" hours for a task based on its title and tags.

```python
def infer_appropriate_time_slot(task: Task) -> dict:
    # ... (excerpts)
    # Morning detection
    if "morning" in title_lower or "exercise" in title_lower:
        preferred_hours = [(6, 12)]
        penalty_hours = [(12, 24)]
    
    # Dinner/Cooking detection (High Priority)
    if "dinner" in title_lower or "cook" in title_lower:
        preferred_hours = [(17, 21)] # 5 PM - 9 PM
        
    # Work vs Personal logic
    if category == "work":
        preferred_hours = [(9, 17)]
```

#### B. Recursive Task Expansion
The system expands recurring tasks (daily, weekly) into individual instances for the target week.

```python
def expand_recurring_tasks(tasks, start_date, days_ahead):
    # Iterates through next 7 days
    # Checks recurrence patterns (daily, weekly, custom)
    # Creates temporary task instances with target_date
```

#### C. Energy & Stress-Aware Slot Scoring
The optimizer iterates through every 30-minute slot in the week and assigns a "confidence score" based on user state (energy/stress) and task requirements.

```python
# Pseudo-code logic from optimize_schedule_with_ml
for day in week:
    for slot in day_slots(30_min_intervals):
        # 1. Check Hard Constraints (Morning/Evening, Conflicts)
        if has_conflict(slot): continue
        
        # 2. Calculate Predicted State
        current_energy = predict_energy(slot, previous_tasks)
        current_stress = predict_stress(slot, previous_tasks)
        
        # 3. Score Slot (Delegated to ScheduleOptimizer model)
        score = optimizer.score(task, energy=current_energy, stress=current_stress)
        
        # 4. Keep Best Slot
        if score > best_score:
            best_slot = slot
```

### 2. Simulation Engine (`routers/simulation.py`)
This module allows running longitudinal simulations (e.g., 30 days) to test how a user persona reacts to different productivity strategies.

#### Simulation Loop
The `run_enhanced_simulation` function manages the daily loop of interaction:

```python
def run_enhanced_simulation(user_persona, days, db):
    for day in range(days):
        # 1. Advance User State
        user.next_day()
        context = user.get_context() # e.g. {stress: high, energy: low}
        
        # 2. Select Strategy (via OnlineCoordinator)
        strategy = coordinator.select_strategy(context, available_strategies)
        
        # 3. User Reaction (Simulated)
        outcome, reward = user.react_to_strategy(strategy)
        
        # 4. Learning Update
        coordinator.log_outcome(strategy, outcome)
```

## 🗄️ Database Models (`db_models.py`)

The application uses a relational schema. Key models include:

- **Account**: User credentials and ML preferences (work hours, energy patterns).
- **Task**: The core unit of work. Contains ML metadata (`energy_required`, `focus_required`).
- **ScheduleItem**: A placed instance of a task on a specific date/time, linked to a logic `placement_reason`.
- **UserMLWeights**: Stores personalized weightings for the recommendation engine (e.g., how much this user cares about 'flow' vs 'stress').

```python
class ScheduleItem(Base):
    # ...
    placement_reason = Column(Text) # "ML Score: 0.85 | Fits energy pattern"
    confidence_score = Column(Float)
    status = Column(String) # scheduled, completed, skipped
```
