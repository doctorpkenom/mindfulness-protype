import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path to allow importing existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routers import users, research, simulation

app = FastAPI(title="Curiosity Co-Pilot API", version="0.1.0")

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Curiosity Co-Pilot Backend Running"}
