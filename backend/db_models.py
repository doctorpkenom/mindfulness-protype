"""
SQLAlchemy database models for persistent storage.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    """User/Persona model for storing simulated users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    base_stress = Column(Float, nullable=False)
    base_energy = Column(Float, nullable=False)
    resilience = Column(Float, default=0.3)
    
    # Relationships
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Interaction(Base):
    """Record of each user interaction with the system."""
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Context at time of interaction
    context = Column(JSON, nullable=False)  # {"stress": "high", "energy": "low", "time": "evening"}
    
    # Strategy presented
    strategy_name = Column(String(200), nullable=False)
    strategy_data = Column(JSON, nullable=False)  # Full strategy object
    
    # Outcome
    outcome = Column(String(50), nullable=False)  # "completed", "started", "ignored"
    completion_time = Column(Float, nullable=True)  # Time in seconds to complete
    
    # Feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 rating
    user_feedback = Column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="interactions")
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Simulation(Base):
    """Record of longitudinal simulations."""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Simulation parameters
    days = Column(Integer, default=30)
    
    # Results
    week_1_avg = Column(Float, nullable=False)
    week_4_avg = Column(Float, nullable=False)
    improvement = Column(Float, nullable=False)
    daily_completion_rates = Column(JSON, nullable=False)  # Array of daily rates
    
    # Metadata
    ml_model_weights = Column(JSON, nullable=True)  # Snapshot of model weights used
    
    # Relationship
    user = relationship("User", back_populates="simulations")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class ModelPerformance(Base):
    """Track ML model performance over time."""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    
    model_name = Column(String(100), nullable=False, index=True)
    
    # Performance metrics
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Training info
    training_samples = Column(Integer, nullable=False)
    training_duration = Column(Float, nullable=True)  # In seconds
    
    # Model weights snapshot
    weights = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class ResearchModule(Base):
    """Track which research modules are active and their usage."""
    __tablename__ = "research_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    module_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    
    # Usage statistics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_completion_time = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Full module data
    module_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemLog(Base):
    """System logs for debugging and monitoring."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    level = Column(String(20), nullable=False, index=True)  # "INFO", "WARNING", "ERROR", "DEBUG"
    component = Column(String(100), nullable=False, index=True)  # "ml_coordinator", "research_engine", etc.
    message = Column(Text, nullable=False)
    
    # Additional context
    context_data = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
