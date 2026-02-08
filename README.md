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
- **Python 3.10+** (with pip)
- **Node.js 18+** (with npm)
- **Git** (for cloning the repository)

### Installation & Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd mindfulness-protype
```

#### 2. Set Up Python Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

#### 4. Initialize Database
```bash
# Create database tables and seed with test data
python backend/seed_data.py
```

This will:
- Create SQLite database (`mindfulness.db`)
- Initialize all database tables
- Create 10 test user personas
- Load all research modules

#### 5. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### 6. Start the Application

**Option A - Automated Script (Recommended for Windows):**
```powershell
.\start_dev.ps1
```

**Option B - Manual Start:**

Terminal 1 (Backend):
```bash
# Make sure virtual environment is activated
uvicorn backend.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

#### 7. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Default Login Credentials

After running `seed_data.py`, you can log in with:
- **Email**: `admin@example.com`
- **Password**: `admin123`

Or create a new account through the registration page.

### Troubleshooting

**Database Issues:**
- If database errors occur, reset the database: `python backend/reset_db.py`
- Then re-seed: `python backend/seed_data.py`

**Port Already in Use:**
- Backend uses port 8000, frontend uses port 5173
- Change ports in `start_dev.ps1` or command line if needed

**Import Errors:**
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip list`
- Check Python version: `python --version` (should be 3.10+)

For more detailed setup instructions, see `GETTING_STARTED.md` and `START_HERE.md`.

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
