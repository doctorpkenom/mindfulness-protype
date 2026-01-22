"""
Authentication router for login, signup, and user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.database import get_db
from backend.db_models import Account, UserMLWeights, SystemLog
from backend.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.models import Token, UserSignup
from pydantic import BaseModel
from datetime import datetime

class UserInfoResponse(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/signup", response_model=Token, status_code=201)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """Create a new user account."""
    # Check if email already exists
    existing_email = db.query(Account).filter(Account.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(Account).filter(Account.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new account
    hashed_password = get_password_hash(user_data.password)
    account = Account(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_admin=False,
        is_active=True
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # Create personalized ML weights for this user
    ml_weights = UserMLWeights(account_id=account.id)
    db.add(ml_weights)
    
    # Log account creation
    log = SystemLog(
        level="INFO",
        component="auth",
        message=f"New account created: {account.username}",
        context_data={"account_id": account.id, "email": account.email}
    )
    db.add(log)
    db.commit()
    
    # Create access token (sub must be a string for JWT)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(account.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    # Find user by username or email
    account = db.query(Account).filter(
        (Account.username == form_data.username) | (Account.email == form_data.username)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, account.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not account.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")
    
    # Update last login
    account.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token (sub must be a string for JWT)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(account.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInfoResponse)
def get_current_user_info(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current user information."""
    import sys
    
    # Debug: Print headers for troubleshooting (flush immediately)
    print(f"[DEBUG /api/auth/me] All headers: {dict(request.headers)}", flush=True)
    
    # Manually extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    
    print(f"[DEBUG /api/auth/me] Authorization header present: {auth_header is not None}", flush=True)
    if auth_header:
        print(f"[DEBUG /api/auth/me] Authorization header preview: {auth_header[:50]}...", flush=True)
    else:
        print("[INFO /api/auth/me] No Authorization header - this is normal on first page load", flush=True)
    
    if not auth_header:
        print("[ERROR /api/auth/me] Missing Authorization header - returning 401", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth_header.startswith("Bearer "):
        print(f"[ERROR /api/auth/me] Invalid header format: {auth_header[:20]}...", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.replace("Bearer ", "").strip()
    
    if not token:
        print("[ERROR /api/auth/me] Token is empty after extraction", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"[DEBUG /api/auth/me] Token extracted, length: {len(token)}", flush=True)
    
    # Decode and validate token
    from backend.auth import jwt, JWTError, SECRET_KEY, ALGORITHM
    
    try:
        print(f"[DEBUG /api/auth/me] Attempting to decode token with SECRET_KEY length: {len(SECRET_KEY)}", flush=True)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        
        print(f"[DEBUG /api/auth/me] Token decoded successfully, user_id (string): {user_id_str}", flush=True)
        
        if not user_id_str:
            print("[ERROR /api/auth/me] Token payload missing 'sub' field", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert string user_id back to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            print(f"[ERROR /api/auth/me] Invalid user_id format: {user_id_str}", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID must be a number",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(Account).filter(Account.id == user_id).first()
        
        if not user:
            print(f"[ERROR /api/auth/me] User with ID {user_id} not found in database", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            print(f"[WARNING /api/auth/me] User {user_id} is inactive", flush=True)
            raise HTTPException(status_code=400, detail="Inactive user")
        
        print(f"[SUCCESS /api/auth/me] Successfully authenticated user: {user.username}", flush=True)
        return UserInfoResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
        
    except JWTError as e:
        print(f"[ERROR /api/auth/me] JWT decode error: {str(e)}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR /api/auth/me] Unexpected error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me/debug")
def debug_auth(request: Request):
    """Debug endpoint to check if token is being sent."""
    auth_header = request.headers.get("Authorization")
    all_headers = dict(request.headers)
    return {
        "has_auth_header": auth_header is not None,
        "auth_header_preview": auth_header[:50] + "..." if auth_header and len(auth_header) > 50 else auth_header,
        "auth_header_full": auth_header,
        "headers_keys": list(request.headers.keys()),
        "all_headers": all_headers
    }
