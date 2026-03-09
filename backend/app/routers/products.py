from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.product import Product, PriceHistory
from app.schemas.product import ProductCreate, ProductResponse, PriceHistoryResponse
from app.utils.security import get_current_user_id
from app.services.price_checker import check_all_prices

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/track", response_model=ProductResponse)
def track_product(product_data: ProductCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    new_product = Product(
        url=product_data.url,
        name=product_data.name,
        target_price=product_data.target_price,
        user_id=user_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/my-products", response_model=list[ProductResponse])
def get_my_products(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.user_id == user_id).all()
    return products


@router.get("/{product_id}/history", response_model=list[PriceHistoryResponse])
def get_price_history(product_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    history = db.query(PriceHistory).filter(PriceHistory.product_id == product_id).all()
    return history


@router.delete("/{product_id}")
def stop_tracking(product_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return {"message": "Tracking stopped"}

@router.post("/check-prices")
def trigger_price_check(user_id: int = Depends(get_current_user_id)):
    check_all_prices()
    return {"message": "Price check completed"}

@router.get("/dashboard/stats")
def get_dashboard(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    total_products = db.query(Product).filter(Product.user_id == user_id).count()
    active_products = db.query(Product).filter(Product.user_id == user_id, Product.is_active == True).count()

    deals = db.query(Product).filter(
        Product.user_id == user_id,
        Product.current_price != None,
        Product.target_price != None,
        Product.current_price <= Product.target_price
    ).all()

    biggest_drop = None
    products = db.query(Product).filter(Product.user_id == user_id, Product.current_price != None).all()
    for p in products:
        history = db.query(PriceHistory).filter(PriceHistory.product_id == p.id).order_by(PriceHistory.checked_at).all()
        if len(history) >= 2:
            first_price = history[0].price
            last_price = history[-1].price
            drop = first_price - last_price
            if biggest_drop is None or drop > biggest_drop["drop"]:
                biggest_drop = {
                    "name": p.name,
                    "drop": round(drop, 2),
                    "current": last_price,
                    "first_seen": str(history[0].checked_at),
                    "last_checked": str(history[-1].checked_at)
                }

    return {
        "total_products": total_products,
        "active_products": active_products,
        "deals_found": len(deals),
        "deals": [{"name": d.name, "price": d.current_price, "target": d.target_price} for d in deals],
        "biggest_drop": biggest_drop,
        "summary": f"{total_products} ürün takip ediliyor, {len(deals)} fırsat bulundu"
    }