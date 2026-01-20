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
*   **Modern Dual-Theme UI:** Beautiful dark mode (AMOLED black with purple/pink accents) and light mode (green/lilac palette) with smooth transitions.

## Setup & Usage

### Backend Setup

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Backend API:**
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```

### Frontend Setup

1.  **Install Node Dependencies:**
    ```bash
    cd frontend
    npm install
    ```

2.  **Run the Development Server:**
    ```bash
    npm run dev
    ```

3.  **Access the App:**
    Open your browser to `http://localhost:5173`

### Testing ML Components

*   **Run the ML Simulation:**
    ```bash
    python ml/online_coordinator.py
    ```

*   **Run the Research Engine Test:**
    ```bash
    python processor/test_engine.py
    ```

## Directory Structure

*   `research/`: JSON files containing the psychological "DNA" of the app.
*   `processor/`: Logic for parsing research and generating plans.
*   `ml/`: The Machine Learning brains (Coordinator + Expert Models).
*   `data_pipeline/`: Data preprocessing and feature engineering.
*   `backend/`: FastAPI REST API with routers for users, research, and simulation.
*   `frontend/`: Modern React + Vite + TailwindCSS web interface with dual-theme support.
*   `simulated_testing/`: User persona simulation and testing framework.

## Tech Stack

**Backend:**
*   FastAPI (Python)
*   NumPy for ML operations
*   Pydantic for data validation

**Frontend:**
*   React 18 + Vite
*   TailwindCSS for styling
*   Recharts for data visualization
*   Lucide React for icons
*   Context API for theme management

**Machine Learning:**
*   Custom ensemble architecture
*   Thompson Sampling for exploration
*   Real-time adaptive learning
