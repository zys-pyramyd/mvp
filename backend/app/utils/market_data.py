from app.api.deps import get_db
import re

async def get_market_estimate(commodity: str, unit: str) -> float:
    """
    Calculate the average market price for a given commodity and unit 
    based on active product listings.
    """
    db = get_db()
    
    # Case-insensitive regex search for the commodity in product titles
    query = {
        "title": {"$regex": commodity, "$options": "i"},
        "unit": unit,
        "quantity_available": {"$gt": 0} # Only consider active stock
    }
    
    products = list(db.products.find(query, {"price_per_unit": 1}))
    
    if not products:
        # Fallback pricing (Mock data for MVP if no products found)
        # In production, this might come from an external API or separate MarketLog
        fallback_prices = {
            "rice": 50000.0, # Per bag
            "tomatoes": 15000.0, # Per basket
            "maize": 25000.0, # Per bag
            "beans": 40000.0, # Per bag
            "yam": 2000.0, # Per tuber
            "palm oil": 25000.0, # Per jerrycan
        }
        
        for key, price in fallback_prices.items():
            if key in commodity.lower():
                return price
                
        return 0.0 # Unknown commodity
        
    # Calculate average
    total_price = sum(p["price_per_unit"] for p in products)
    avg_price = total_price / len(products)
    
    return round(avg_price, 2)
