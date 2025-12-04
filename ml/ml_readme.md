# Machine Learning Ensemble (`ml/`)

This directory contains the "Brain" of the application. It uses a **Council of Experts** architecture to make real-time decisions about which strategy to show the user.

## Architecture

### `online_coordinator.py` (The Coordinator)
The central controller.
1.  Receives the current User Context (Time, Energy, Stress).
2.  Queries each "Expert Model" for their vote.
3.  Aggregates the votes using a weighted sum.
4.  Selects the winning strategy.
5.  Distributes feedback (Success/Failure) back to the experts for learning.

### `models/` (The Council)
A collection of specialized models, each representing a different psychological priority:

*   **`habit_optimizer.py`:** Prioritizes consistency. Tracks streaks. (Based on Lally).
*   **`stress_predictor.py`:** Prioritizes well-being. Detects burnout. (Based on Sirois).
*   **`curiosity_tuner.py`:** Prioritizes engagement. Uses Thompson Sampling to explore new strategies. (Based on Loewenstein).
*   **`flow_manager.py`:** Prioritizes performance. Matches task difficulty to user energy. (Based on Csikszentmihalyi).

### `base_model.py`
The abstract base class defining the interface (`predict`, `update`, `save`, `load`) for all expert models.
