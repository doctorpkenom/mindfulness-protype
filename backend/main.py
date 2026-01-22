import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add project root to sys.path to allow importing existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routers import users, research, simulation, analytics, debug, auth, tasks, schedule, timer
from backend.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown."""
    # Startup
    print("🚀 Starting Mindfulness Prototype Backend...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="Productivity Assistant API",
    version="3.0.0",
    description="AI-powered productivity assistant with ML-optimized task scheduling",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
# Authentication (public)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# User tasks and productivity (authenticated)
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
app.include_router(timer.router, prefix="/api/timer", tags=["Timer"])

# Legacy/Admin routers (for simulations and debugging)
app.include_router(users.router, prefix="/api/users", tags=["Users (Legacy)"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Productivity Assistant API v3.0.0",
        "features": ["ML-Optimized Scheduling", "Task Management", "Timer Tracking", "User Authentication", "Personalized Learning"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
