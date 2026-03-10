from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.user import UserResponse
from app.utils.security import get_current_user_id
from app.limiter import limiter

router = APIRouter(prefix="/admin", tags=["Admin"])

def require_admin(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id

@router.get("/users")
def list_users(user_id: int = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": str(u.created_at)
        }
        for u in users
    ]

@router.put("/users/{target_id}/deactivate")
def deactivate_user(target_id: int, user_id: int = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    target.is_active = False
    db.commit()
    return {"message": f"User {target.username} deactivated"}

@router.put("/users/{target_id}/make-admin")
def make_admin(target_id: int, user_id: int = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.role = "admin"
    db.commit()
    return {"message": f"User {target.username} is now admin"}

@router.get("/stats")
def admin_stats(user_id: int = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_products": total_products,
        "active_products": active_products
    }