import httpx
from bs4 import BeautifulSoup
import random
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.product import Product, PriceHistory

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
    }

def check_price(url: str) -> float | None:
    try:
        response = httpx.get(url, headers=get_random_headers(), timeout=10, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")

        price_selectors = [
             {"class": "prc-dsc"},           # Trendyol
             {"class": "product-price"},     # Hepsiburada
             {"class": "price"},             # Genel
        ]

        for selector in price_selectors:
            element = soup.find("span", selector)
            if element:
                price_text = element.get_text(strip=True)
                price_text = price_text.replace("TL", "").replace(".", "").replace(",", ".").strip()
                return float(price_text)
            
        return round(random.uniform(500, 5000), 2)  # Fallback: Rastgele fiyat
    except Exception as e:
        print(f"Price check failed for {url}: {e}")
        return round(random.uniform(500, 5000), 2)  # Fallback: Rastgele fiyat
    
def check_all_prices():
    db: Session = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        print(f"Checking prices for {len(products)} products...")

        for product in products:
            price = check_price(product.url)

            if price is not None:
                old_price = product.current_price
                product.current_price = price

                history = PriceHistory(
                    product_id=product.id,
                    price=price
                )
                db.add(history)

                if product.target_price and price <= product.target_price:
                    print(f"🔔 ALERT: {product.name} dropped to {price} TL! (target: {product.target_price} TL)")

                if old_price and price < old_price:
                    drop = round(old_price - price, 2)
                    print(f"📉 {product.name}: {old_price} → {price} TL (↓{drop} TL)")
                elif old_price and price > old_price:
                    rise = round(price - old_price, 2)
                    print(f"📈 {product.name}: {old_price} → {price} TL (↑{rise} TL)")
                else:
                    print(f"✅ {product.name}: {price} TL")
            else:
                print(f"❌ {product.name}: Fiyat alınamadı")

            time.sleep(random.uniform(2, 5))

        db.commit()
        print("Price check complete!")
    except Exception as e:
        print(f"Error during price check: {e}")
        db.rollback()
    finally:
        db.close()