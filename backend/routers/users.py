from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import UserCreate, UserResponse

# Import existing logic
from simulated_testing.user_manager import UserManager

router = APIRouter()
manager = UserManager() # This loads from json automatically

@router.get("/", response_model=List[UserResponse])
def get_users():
    users = manager.get_all_users()
    return [UserResponse(
        name=u.name, 
        base_stress=u.base_stress, 
        base_energy=u.base_energy,
        resilience=u.resilience
    ) for u in users]

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    existing = manager.get_user(user.name)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = manager.create_user(user.name, user.stress, user.energy, user.resilience)
    return UserResponse(
        name=new_user.name,
        base_stress=new_user.base_stress,
        base_energy=new_user.base_energy,
        resilience=new_user.resilience
    )

@router.get("/{name}", response_model=UserResponse)
def get_user(name: str):
    user = manager.get_user(name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        name=user.name,
        base_stress=user.base_stress,
        base_energy=user.base_energy,
        resilience=user.resilience
    )
