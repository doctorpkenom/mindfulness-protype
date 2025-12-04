# Curiosity-Powered Distraction App (Prototype)

A scientifically-grounded "co-pilot" for focus, designed to harness curiosity rather than fight distraction. This project uses a **Research Data Bank** of behavioral psychology principles and an **Adaptive Machine Learning Ensemble** to generate personalized interventions for users.

## Project Architecture

The system is composed of four main layers:

1.  **Research Data Bank (`research/`)**: A collection of machine-readable JSON modules representing core psychological theories (e.g., Fogg Behavior Model, Flow State, Self-Determination Theory).
2.  **Strategy Engine (`processor/`)**: A Python engine that loads these research modules and generates "Composite Plans" (Trigger -> Action -> Retention). It includes an **Adaptation Layer** to handle specific user contexts (e.g., High Stress).
3.  **Data Pipeline (`data_pipeline/`)**: Utilities for cleaning and converting raw user context (Time, Energy, Stress) into numerical feature vectors.
4.  **ML Ensemble (`ml/`)**: A "Council of Experts" architecture where multiple specialized models (Habit Optimizer, Stress Predictor, etc.) vote on the best strategy for the user in real-time.

## Key Features

*   **Scientific Foundation:** 13+ core research papers digitized into actionable logic templates.
*   **Context-Aware:** Adapts strategies based on user energy, stress, and time of day.
*   **Ensemble Learning:** Uses a weighted voting system of specialized models to balance productivity (Flow) with well-being (Self-Compassion).
*   **Generalized Templates:** Strategies are abstract templates (e.g., `IF [Trigger] THEN [Action]`) that can be filled with specific user data.

## Setup & Usage

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Requires `numpy`)*

2.  **Run the ML Simulation:**
    To see the "Council of Experts" in action:
    ```bash
    python ml/online_coordinator.py
    ```

3.  **Run the Research Engine Test:**
    To verify the loading of research modules:
    ```bash
    python processor/test_engine.py
    ```

## Directory Structure

*   `research/`: JSON files containing the psychological "DNA" of the app.
*   `processor/`: Logic for parsing research and generating plans.
*   `ml/`: The Machine Learning brains (Coordinator + Expert Models).
*   `data_pipeline/`: Data preprocessing and feature engineering.
