# Mindfulness Prototype v2.0 - AI-Powered Focus Assistant

A production-ready, scientifically-grounded "co-pilot" for focus that harnesses curiosity rather than fighting distraction. Features a **7-model ML Ensemble**, **13 Research Modules**, **Database Persistence**, and a **Beautiful Dual-Theme UI**.

🎯 **Fully functional** | 🧠 **7 ML Models** | 📊 **Real-time Analytics** | 🎨 **AMOLED Dark Mode** | 💾 **Database Backed**

## Project Architecture

The system is composed of four main layers:

1.  **Research Data Bank (`research/`)**: A collection of machine-readable JSON modules representing core psychological theories (e.g., Fogg Behavior Model, Flow State, Self-Determination Theory).
2.  **Strategy Engine (`processor/`)**: A Python engine that loads these research modules and generates "Composite Plans" (Trigger -> Action -> Retention). It includes an **Adaptation Layer** to handle specific user contexts (e.g., High Stress).
3.  **Data Pipeline (`data_pipeline/`)**: Utilities for cleaning and converting raw user context (Time, Energy, Stress) into numerical feature vectors.
4.  **ML Ensemble (`ml/`)**: A "Council of Experts" architecture where multiple specialized models (Habit Optimizer, Stress Predictor, etc.) vote on the best strategy for the user in real-time.

## ✨ Key Features

### 🧠 Advanced ML Ensemble (7 Expert Models)
*   **Habit Optimizer** - Tracks consistency & streaks (Lally 2010)
*   **Stress Predictor** - Burnout prevention with trend analysis (Sirois 2014)
*   **Curiosity Tuner** - Thompson Sampling for engagement (Loewenstein 1994)
*   **Flow Manager** - Optimal challenge matching (Csikszentmihalyi 1990)
*   **Attention Manager** - Minimizes task switching (Rubinstein 2001)
*   **Motivation Booster** - Intrinsic motivation via SDT (Ryan & Deci 2000)
*   **Zeigarnik Tracker** - Leverages incomplete tasks (Zeigarnik 1927)

### 📚 Research-Backed Strategies
*   **13 Research Modules** digitized into actionable templates
*   **Evidence Strength Ratings** (high/medium/emerging)
*   **Context Suitability Mapping** for stress/energy states
*   **ML Feature Importance** for each research module

### 💾 Production Database
*   **SQLAlchemy ORM** with SQLite (PostgreSQL-ready)
*   **6 Database Tables** (Users, Interactions, Simulations, Models, Research, Logs)
*   **Complete Persistence** - All data saved and queryable
*   **10 Pre-Built Personas** for immediate testing

### 🎨 Beautiful Dual-Theme UI
*   **AMOLED Dark Mode** - Pure black with purple/pink gradients
*   **Clean Light Mode** - White with green/lilac accents
*   **Smooth 300ms Transitions** with localStorage persistence
*   **5 Complete Tabs** - Dashboard, Pilot, Users, Simulation, Debug

### 📊 Comprehensive Analytics
*   **Real-Time Dashboard** with key metrics
*   **ML Model Performance Tracking** with trends
*   **30-Day Interaction Charts** (Recharts)
*   **Top Strategy Leaderboards**
*   **User Insights & Personalization**

### ⚙️ Debug & Testing Tools
*   **Model Testing Interface** - Test each expert individually
*   **System Log Viewer** - Real-time debugging
*   **Model Weight Inspector** - View ML internals
*   **Research Engine Validator**
*   **Comprehensive Test Suite** (run_tests.py)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Python (Backend)
pip install -r requirements.txt

# Node.js (Frontend)
cd frontend
npm install
cd ..
```

### 2. Seed Database with Test Data
```bash
python backend/seed_data.py
```
Creates 10 diverse user personas, indexes 13 research modules, and initializes the database.

### 3. Start the Application

**Easy Way (Automated):**
```powershell
.\start_dev.ps1
```

**Manual Way:**
```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 4. Open Browser
Navigate to **http://localhost:5173**

### 5. Run Tests (Optional)
```bash
python run_tests.py
```

📚 **For detailed setup guide, see `GETTING_STARTED.md`**

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
*   7-model ensemble architecture with weighted voting
*   Thompson Sampling for exploration-exploitation balance
*   Real-time adaptive learning with streak tracking
*   Stress trend analysis and burnout prevention
*   Context-aware strategy selection

**Database:**
*   SQLAlchemy ORM
*   SQLite (PostgreSQL-ready)
*   Alembic for migrations

**Testing:**
*   Comprehensive test suite with 6 test categories
*   Accuracy benchmarking (60%+ threshold)
*   10 diverse user personas for validation

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│  Dashboard | Pilot | Users | Simulation | Debug     │
└─────────────────────┬───────────────────────────────┘
                      │ REST API
┌─────────────────────┴───────────────────────────────┐
│                  FastAPI Backend                     │
│   5 Routers: Users | Research | Simulation |        │
│              Analytics | Debug                       │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐  ┌────▼────┐  ┌───▼────┐
    │Database│  │ML Models│  │Research│
    │SQLite  │  │Ensemble │  │Engine  │
    └────────┘  └─────────┘  └────────┘
```

## 🎯 What You Can Do

### 1. View Real-Time Analytics (Dashboard)
- System health monitoring
- ML model performance tracking
- Interaction trends over 30 days
- Top strategy performance metrics

### 2. Test Interventions (Live Pilot)
- Select user personas
- Set stress/energy context
- Trigger AI-generated interventions
- Watch ML ensemble decision-making

### 3. Manage Users (User Manager)
- Create/view/delete personas
- Adjust stress/energy/resilience
- Track user statistics

### 4. Run Simulations (Simulation Lab)
- Execute 30-day longitudinal tests
- Track week-by-week improvement
- Visualize completion rates
- Compare persona outcomes

### 5. Debug & Test (Debug Tab)
- Test individual ML models
- View system logs in real-time
- Inspect model weights
- Monitor database health

## 📈 Success Metrics

The system achieves:
- ✅ **60%+ accuracy** on diverse test scenarios
- ✅ **100% stress safety** - never recommends high-difficulty tasks during high stress
- ✅ **Adaptive learning** - model weights improve over time
- ✅ **Context awareness** - recommendations match user state
- ✅ **Research validity** - all strategies traceable to peer-reviewed papers

## 🧪 Testing

```bash
# Run comprehensive test suite
python run_tests.py

# Expected output:
# ✅ ML Models
# ✅ Research Engine  
# ✅ Database Operations
# ✅ User Persona Simulation
# ✅ ML Ensemble Consensus
# ✅ Accuracy Benchmark
# Result: 100% tests passed
```

## 📚 Documentation

- **GETTING_STARTED.md** - Complete setup guide
- **BUILD_SUMMARY.md** - What was built and why
- **CHANGELOG.md** - Version history and changes
- **frontend/THEME_SYSTEM.md** - Theme documentation
- **frontend/THEME_VISUAL_GUIDE.md** - Color reference
- **frontend/QUICK_START.md** - Developer quick reference

## 🎨 Theme System

Toggle between beautiful themes:
- 🌙 **Dark Mode**: AMOLED black (#000) with purple/pink gradients
- ☀️ **Light Mode**: Clean white with green/lilac gradients

Theme preference persists in localStorage. Smooth 300ms transitions.

## 🔧 Development

```bash
# Backend development
uvicorn backend.main:app --reload --port 8000

# Frontend development
cd frontend && npm run dev

# Database management
python backend/seed_data.py  # Reset and seed
sqlite3 mindfulness.db       # Browse database

# Testing
python run_tests.py          # Full test suite
python ml/online_coordinator.py  # Test ML
python processor/test_engine.py  # Test research
```

## 🚀 Deployment Ready

The application is production-ready with:
- ✅ Error boundaries and crash protection
- ✅ Loading states and proper UX feedback
- ✅ Database persistence (SQLite → PostgreSQL)
- ✅ Comprehensive logging system
- ✅ API documentation (FastAPI auto-docs at `/docs`)
- ✅ Environment variable support
- ✅ CORS configuration
- ✅ Accessibility compliance (WCAG AA)

## 🤝 Contributing

This is a research prototype demonstrating:
- Ensemble ML for behavioral interventions
- Research-driven strategy generation
- Context-adaptive personalization
- Real-time learning systems

Feel free to extend with:
- Additional research modules
- New ML expert models
- Enhanced UI features
- Mobile applications
- Cloud deployment

## 📝 License

Research prototype for educational and research purposes.

---

**Version 2.0.0** - Full Production Release
Built with ❤️ for mindfulness, focus, and productivity 🧘‍♀️✨
