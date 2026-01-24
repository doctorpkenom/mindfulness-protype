# Mindfulness Productivity Assistant

**Overview**
The Mindfulness Productivity Assistant is an advanced, AI-powered system designed to optimize personal productivity while prioritizing mental well-being. Unlike traditional to-do lists that only focus on *what* needs to be done, this system understands *how* and *when* it should be done based on your energy, stress levels, and psychological needs.

## 🧠 Core Philosophy
The system integrates principles from 14+ psychological frameworks (e.g., **Flow State**, **Self-Determination Theory**, **Tiny Habits**) to create a "compassionate productivity" loop. It doesn't just push you to work harder; it helps you work smarter and recover better.

## 📚 Documentation Hub

Detailed documentation for each component can be found in their respective directories:

- **[Backend Documentation](backend/backend_readme.md)**: FastAPI architecture, Database Schema, and core API logic.
- **[Frontend Documentation](frontend/frontend_readme.md)**: React application structure, components, and state management.
- **[Machine Learning Models](ml/ml_readme.md)**: Deep dive into the "Council of Experts" ensemble model and Schedule Optimization algorithms.
- **[Data Pipeline](data_pipeline/data_pipeline_readme.md)**: How raw data is transformed into feature vectors for ML training.
- **[Research Engine](processor/processor_readme.md)**: The logic that adapts static research principles into dynamic intervention plans.
- **[psychological Frameworks](research/research_readme.md)**: Database of research papers and principles used by the system.
- **[Simulated Testing](simulated_testing/simulated_testing_readme.md)**: Tools for running longitudinal simulations with "User Personas".

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Setup
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🤖 Key Algorithms Snapshot

### 1. The Council of Experts (`ml/online_coordinator.py`)
A weighted ensemble voting system where different "Expert" models vote on the best strategy for the user.
- **StressPredictor**: Vetoes high-difficulty tasks when user is stressed.
- **FlowManager**: Matches task difficulty to user energy to induce flow.
- **HabitOptimizer**: Prioritizes consistency for recurring tasks.

### 2. Multi-Objective Schedule Optimization (`backend/routers/schedule.py`)
A complex algorithm that places tasks in the calendar by optimizing for:
- **Time Constraints**: (e.g., "Dinner" must be 5-9 PM).
- **Energy Matching**: High focus tasks during peak energy hours.
- **Psychological Safety**: Ensuring breaks and "retention" activities are scheduled when stress predicts a peak.

### 3. User Simulation (`simulated_testing/user_persona.py`)
A probabilistic simulation engine that models human fatigue and resistance, allowing us to "stress test" our AI strategies before deploying them to real users.
