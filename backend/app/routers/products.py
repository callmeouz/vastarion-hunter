from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.product import Product, PriceHistory, Tag, ProductTag
from app.schemas.product import ProductCreate, ProductResponse, PriceHistoryResponse, TagCreate, TagResponse
from app.utils.security import get_current_user_id
from app.services.price_checker import check_all_prices
import redis
import json

router = APIRouter(prefix="/products", tags=["Products"])

redis_client = redis.from_url("redis://redis:6379/0")


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
    cache_key = f"dashboard:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        print(f" Dashboard cache hit for user {user_id}")
        return json.loads(cached)

    print(f" Dashboard cache miss for user {user_id}")

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

    result = {
        "total_products": total_products,
        "active_products": active_products,
        "deals_found": len(deals),
        "deals": [{"name": d.name, "price": d.current_price, "target": d.target_price} for d in deals],
        "biggest_drop": biggest_drop,
        "summary": f"{total_products} products tracked, {len(deals)} deals found"
    }

    redis_client.setex(cache_key, 300, json.dumps(result, default=str))

    return result

@router.post("/tags", response_model=TagResponse)
def create_tag(tag_data: TagCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    existing = db.query(Tag).filter(Tag.name == tag_data.name, Tag.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = Tag(name=tag_data.name, user_id=user_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.get("/tags", response_model=list[TagResponse])
def get_my_tags(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return db.query(Tag).filter(Tag.user_id == user_id).all()

@router.post("/{product_id}/tags/{tag_id}")
def add_tag_to_product(product_id: int, tag_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    existing = db.query(ProductTag).filter(ProductTag.product_id == product_id, ProductTag.tag_id == tag_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already added to this product")
    
    product_tag = ProductTag(product_id=product_id, tag_id=tag_id)
    db.add(product_tag)
    db.commit()
    return {"message": f"Tag '{tag.name}' added to '{product.name}'"}

@router.delete("/{product_id}/tags/{tag_id}")
def remove_tag_from_product(product_id: int, tag_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    product_tag = db.query(ProductTag).filter(ProductTag.product_id == product_id, ProductTag.tag_id == tag_id).first()
    if not product_tag:
        raise HTTPException(status_code=404, detail="Tag not on this product")
    db.delete(product_tag)
    db.commit()
    return {"message": "Tag removed"}

@router.get("/by-tag/{tag_id}", response_model=list[ProductResponse])
def get_products_by_tag(tag_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    product_ids = db.query(ProductTag.product_id).filter(ProductTag.tag_id == tag_id).all()
    ids = [p[0] for p in product_ids]
    return db.query(Product).filter(Product.id.in_(ids), Product.user_id == user_id).all()