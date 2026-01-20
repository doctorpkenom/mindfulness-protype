from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.models import UserCreate, UserResponse
from backend.database import get_db
from backend.db_models import User as DBUser, SystemLog

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Get all users from database."""
    users = db.query(DBUser).all()
    return [
        UserResponse(
            name=user.name,
            base_stress=user.base_stress,
            base_energy=user.base_energy,
            resilience=user.resilience
        )
        for user in users
    ]

@router.get("/{name}", response_model=UserResponse)
def get_user(name: str, db: Session = Depends(get_db)):
    """Get a specific user by name."""
    user = db.query(DBUser).filter(DBUser.name == name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        name=user.name,
        base_stress=user.base_stress,
        base_energy=user.base_energy,
        resilience=user.resilience
    )

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    existing = db.query(DBUser).filter(DBUser.name == user.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    db_user = DBUser(
        name=user.name,
        base_stress=user.stress,
        base_energy=user.energy,
        resilience=user.resilience
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log creation
    log = SystemLog(
        level="INFO",
        component="user_manager",
        message=f"Created new user: {user.name}",
        context_data={"user_id": db_user.id, "name": user.name}
    )
    db.add(log)
    db.commit()
    
    return UserResponse(
        name=db_user.name,
        base_stress=db_user.base_stress,
        base_energy=db_user.base_energy,
        resilience=db_user.resilience
    )

@router.delete("/{name}")
def delete_user(name: str, db: Session = Depends(get_db)):
    """Delete a user."""
    user = db.query(DBUser).filter(DBUser.name == name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log deletion
    log = SystemLog(
        level="INFO",
        component="user_manager",
        message=f"Deleted user: {name}",
        context_data={"user_id": user.id, "name": name}
    )
    db.add(log)
    
    db.delete(user)
    db.commit()
    
    return {"status": "deleted", "name": name}
