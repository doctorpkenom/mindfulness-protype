# ML Architecture Implementation Plan

## Goal
Create a self-improving system where a real-time "Online Model" interacts with the user, while a background "Offline Model" simulates and refines strategies based on accumulated data.

## Architecture Overview

## Architecture Overview (Ensemble Approach)

### 1. Online Layer (The "Coordinator")
*   **File:** `ml/online_coordinator.py`
*   **Role:** The single point of contact for the App.
*   **Function:** It receives the user context and asks the "Council of Models" for the best strategy. It uses a weighted voting system (Ensemble) to make the final decision.

### 2. Offline Layer (The "Council")
Instead of one big model, we have specialized "Expert Models" running in the background.

*   **File:** `ml/offline_controller.py` (Orchestrates the training of all experts)
*   **Directory:** `ml/models/` (Contains the individual expert files)

#### The Expert Models (in `ml/models/`):
1.  **`habit_optimizer.py`**: Specializes in Lally's research. Tracks consistency and streaks.
2.  **`stress_predictor.py`**: Specializes in Sirois/Bandura. Predicts burnout and suggests regulation.
3.  **`curiosity_tuner.py`**: Specializes in Loewenstein/Kang. Optimizes "Curiosity Bites" and dopamine.
4.  **`flow_manager.py`**: Specializes in Csikszentmihalyi. Adjusts difficulty to maintain Flow.

### 3. Data Flow
1.  **Live:** User drifts -> `online_coordinator` queries the Experts -> Experts vote -> Best Strategy selected.
2.  **Background:** `offline_controller` wakes up periodically -> Feeds historical data to each Expert -> Experts refine their internal logic -> Updated weights saved.

## Proposed File Structure
*   `ml/`
    *   `online_coordinator.py`
    *   `offline_controller.py`
    *   `models/`
        *   `base_model.py` (Template for all experts)
        *   `habit_optimizer.py`
        *   `stress_predictor.py`
        *   `curiosity_tuner.py`
        *   `flow_manager.py`
    *   `data/` (Logs and weights)
