from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, ChangePassword
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user_id
from fastapi.security import OAuth2PasswordRequestForm
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.put("/change-password")
@limiter.limit("5/minute")
def change_password( request: Request, data: ChangePassword, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")
    
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong password")
    
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}