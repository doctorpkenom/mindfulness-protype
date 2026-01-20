# 🚀 Getting Started - Mindfulness Prototype v2.0

Welcome to the fully-fledged Mindfulness Prototype! This guide will help you get everything running.

---

## ⚡ Quick Start (5 Minutes)

### 1. Install Dependencies

**Python (Backend):**
```bash
pip install -r requirements.txt
```

**Node.js (Frontend):**
```bash
cd frontend
npm install
cd ..
```

### 2. Initialize Database with Test Data

```bash
python backend/seed_data.py
```

This creates:
- ✅ 10 diverse user personas
- ✅ 13 indexed research modules
- ✅ SQLite database with all tables
- ✅ Initial system logs

### 3. Start the Application

**Option A - Use the automated script (Recommended):**
```powershell
.\start_dev.ps1
```

**Option B - Manual start:**

Terminal 1 (Backend):
```bash
uvicorn backend.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### 4. Access the Application

Open your browser to: **http://localhost:5173**

You should see the beautiful dual-theme interface with the Dashboard as the default tab!

---

## 🎯 What You Can Do Now

### 🏠 Dashboard Tab
- View real-time analytics
- Monitor ML model performance (7 expert models)
- See interaction trends (30-day charts)
- Track top-performing strategies
- System health monitoring

### ▶️ Live Pilot Tab
- Select a user persona
- Set context (stress/energy levels)
- Trigger drift events
- See AI-generated intervention plans
- Watch the ML ensemble decision-making process

### 👥 User Manager Tab
- View all 10 pre-created personas
- Create new custom personas
- Adjust stress/energy/resilience parameters
- Delete users (database-backed)

### 🧪 Simulation Lab Tab
- Run 30-day longitudinal simulations
- See week-by-week improvement metrics
- View daily completion rate charts
- Track simulation history

### ⚙️ Debug & Settings Tab
- Test individual ML models
- View model weights in real-time
- Inspect system logs
- Test research engine
- Monitor database health
- System diagnostics

---

## 🧠 Understanding the ML Ensemble

### The 7 Expert Models

1. **Habit Optimizer** (Lally 2010)
   - Tracks consistency and streaks
   - Recommends strategies that build automaticity
   - Weight: 1.0

2. **Stress Predictor** (Sirois 2014 / Bandura 1977)
   - Detects stress patterns and trends
   - Prioritizes self-compassion when stress is high
   - Weight: 1.8 (highest - safety first!)

3. **Curiosity Tuner** (Loewenstein 1994)
   - Uses Thompson Sampling for exploration
   - Balances novelty vs. proven strategies
   - Weight: 1.0

4. **Flow Manager** (Csikszentmihalyi 1990)
   - Matches task difficulty to user energy
   - Optimizes for optimal challenge
   - Weight: 1.2

5. **Attention Manager** (Rubinstein 2001)
   - Minimizes context switching
   - Penalizes complex tasks when fatigued
   - Weight: 1.1

6. **Motivation Booster** (Ryan & Deci 2000 - SDT)
   - Prioritizes intrinsic motivation
   - Focuses on autonomy, competence, relatedness
   - Weight: 1.3

7. **Zeigarnik Tracker** (Zeigarnik 1927)
   - Leverages incomplete tasks for engagement
   - Recommends closure strategies
   - Weight: 0.9

### How Decisions Are Made

1. **User context** (stress, energy, time) is preprocessed
2. Each expert **votes** on available strategies
3. Votes are **weighted** based on expert trust levels
4. **Final decision** uses weighted sum voting
5. Outcome is **logged** to database for learning

---

## 📊 Database Structure

### Tables Created

- `users` - User personas with stress/energy profiles
- `interactions` - Every strategy interaction logged
- `simulations` - 30-day simulation results
- `model_performance` - ML model accuracy tracking
- `research_modules` - Indexed research with usage stats
- `system_logs` - Debugging and monitoring logs

### Viewing the Database

```bash
# SQLite browser (if installed)
sqlite3 mindfulness.db

# Or use any SQL client
# Database file: mindfulness.db (in project root)
```

---

## 🧪 Running Tests

### Comprehensive Test Suite

```bash
python run_tests.py
```

This runs:
- ✅ ML model functionality tests
- ✅ Research engine validation
- ✅ Database CRUD operations
- ✅ User persona simulation
- ✅ Ensemble consensus checks
- ✅ Accuracy benchmarks

Expected output: **100% tests passed**

### Individual Component Tests

```bash
# Test ML coordinator
python ml/online_coordinator.py

# Test research engine
python processor/test_engine.py

# Test data preprocessing
python data_pipeline/preprocessor.py
```

---

## 🎨 Theme System

### Switch Themes

Click the theme toggle button at the bottom of the sidebar:
- 🌙 **Dark Mode**: AMOLED black with purple/pink accents
- ☀️ **Light Mode**: Clean white with green/lilac accents

Your preference is saved to localStorage automatically!

---

## 📝 Typical Workflow

### 1. Explore the Data (Dashboard)
- Check analytics and model performance
- See which strategies are performing best
- Monitor system health

### 2. Test with Users (Live Pilot)
- Select a persona (e.g., "Stressed Executive")
- Set high stress, low energy
- Trigger a drift event
- Observe the AI's compassionate response

### 3. Run Simulations (Simulation Lab)
- Pick "Burnt Out Creative"
- Run a 30-day simulation
- Watch the improvement metrics
- See the learning curve

### 4. Debug & Optimize (Debug Tab)
- Test the Stress Predictor model
- Verify it prioritizes self-compassion
- Check system logs for issues
- View model weights evolution

### 5. Create Custom Personas (User Manager)
- Design your own test cases
- Adjust stress/energy parameters
- Run simulations to see outcomes

---

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Database URL (optional - defaults to SQLite)
export DATABASE_URL="postgresql://user:pass@localhost/mindfulness"

# API Port (optional - defaults to 8000)
export PORT=8000
```

### Model Weights

Model weights are saved in `ml/data/*.json`:
- `habit_optimizer_weights.json`
- `stress_predictor_weights.json`
- `curiosity_tuner_weights.json`
- `flow_manager_weights.json`
- `attention_manager_weights.json`
- `motivation_booster_weights.json`
- `zeigarnik_tracker_weights.json`

You can reset them by deleting these files - they'll regenerate with defaults.

### Research Modules

Research papers are in `research/*.json`. To add a new module:
1. Create `research/your_paper_YEAR.json`
2. Follow the existing schema
3. Restart the backend
4. It will auto-index on startup

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Clear node_modules
cd frontend
rm -rf node_modules
npm install
```

### Database errors
```bash
# Reset database
python backend/seed_data.py

# Or manually delete
rm mindfulness.db
python backend/seed_data.py
```

### API connection errors
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify frontend API_BASE_URL in `frontend/src/api.js`

---

## 📚 Project Structure

```
mindfulness-protype/
├── backend/           # FastAPI backend
│   ├── database.py   # SQLAlchemy config
│   ├── db_models.py  # Database models
│   ├── main.py       # FastAPI app
│   ├── models.py     # Pydantic schemas
│   ├── routers/      # API endpoints
│   └── seed_data.py  # Database seeding
├── frontend/         # React + Vite
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── contexts/    # Theme context
│   │   ├── api.js       # API client
│   │   └── App.jsx      # Main app
│   └── THEME_SYSTEM.md  # Theme docs
├── ml/               # Machine Learning
│   ├── models/       # 7 expert models
│   ├── data/         # Model weights
│   └── online_coordinator.py  # Ensemble
├── processor/        # Research Engine
│   ├── research_engine.py      # Core logic
│   ├── research_metadata.py    # ML integration
│   └── adaptation_rules.json   # Context rules
├── research/         # 13 research JSON files
├── data_pipeline/    # Data preprocessing
├── simulated_testing/  # User simulation
├── run_tests.py      # Test suite
└── GETTING_STARTED.md  # This file!
```

---

## 🎉 Next Steps

Now that everything is running:

1. **Explore the Interface**
   - Try all 5 tabs
   - Switch between themes
   - Test different personas

2. **Run Simulations**
   - Use all 10 pre-created personas
   - See which ones improve the most
   - Study the patterns

3. **Test the ML Models**
   - Use Debug tab to test each expert
   - Try extreme contexts (high stress + low energy)
   - Verify sensible recommendations

4. **Analyze the Data**
   - Dashboard shows real-time analytics
   - Check interaction trends
   - Monitor model accuracy

5. **Customize & Extend**
   - Add your own personas
   - Tweak model weights
   - Add new research modules

---

## 💡 Pro Tips

- **Best test scenario**: "Burnt Out Creative" persona with high stress context
- **Watch the logs**: Debug tab shows real-time system activity
- **Model weights evolve**: Run multiple simulations to see models learn
- **Research indexer**: Automatically categorizes strategies for ML
- **Ensemble consensus**: Stress Predictor has highest weight for safety

---

## 🚀 You're All Set!

Everything is working together:
- ✅ 7 ML expert models
- ✅ 13 research modules
- ✅ 10 diverse personas
- ✅ Full database persistence
- ✅ Beautiful dual-theme UI
- ✅ Comprehensive testing suite

**Start exploring and have fun building better focus habits!** 🧘‍♀️✨

---

*For detailed theme documentation, see `frontend/THEME_SYSTEM.md`*
*For architecture details, see `README.md`*
