
from fastapi import APIRouter, Query
from typing import Optional
from app.api.deps import get_db
from app.models.common import (
    ProductCategory, ProcessingLevel,
    GrainsCerealsSubcategory, BeansLegumesSubcategory, FishMeatSubcategory,
    SpicesVegetablesSubcategory, TubersRootsSubcategory, FlourFlakesSubcategory,
    DrinksBeverageSubcategory, SnacksConfectionariesSubcategory, SweetsSugarSubcategory,
    FruitsSubcategory, CashCropSubcategory, FeedsSubcategory, FarmInputsSubcategory,
    NIGERIAN_STATES
)

router = APIRouter()


def _label(value: str) -> str:
    return value.replace("_", " ").title()


# Categories that don't belong in the farm deals (farmer/agent) context.
# These are processed consumer goods — not raw agricultural produce.
BUSINESS_ONLY_CATEGORIES = {
    ProductCategory.DRINKS_BEVERAGE.value,
    ProductCategory.SNACKS_CONFECTIONARIES.value,
    ProductCategory.SWEETS_SUGAR.value,
}

# Categories that don't belong on the business/home marketplace either
# (purely raw agricultural — keeps home page clean).
FARM_ONLY_CATEGORIES = {
    ProductCategory.CASH_CROP.value,
    ProductCategory.FEEDS.value,
    ProductCategory.FARM_INPUTS.value,
}


# ---------------------------------------------------------------------------
# GET /api/categories
# Flat list consumed by the filter dropdown. Accepts optional ?platform= param
# so farm_deals excludes processed consumer goods.
# ---------------------------------------------------------------------------
@router.get("")
async def get_categories(platform: Optional[str] = Query(None)):
    """
    Return a flat list of product categories.
    Pass ?platform=farm_deals to exclude processed consumer goods
    (drinks, snacks, sweets) that are not relevant to farmers/agents.
    """
    result = []
    for cat in ProductCategory:
        if platform == "farm_deals" and cat.value in BUSINESS_ONLY_CATEGORIES:
            continue
        result.append({"value": cat.value, "name": _label(cat.value), "label": _label(cat.value)})
    return result


# ---------------------------------------------------------------------------
# GET /api/categories/dynamic
# Rich taxonomy used by the secondary category nav bar.
# Accepts optional ?platform= param for the same filtering.
# ---------------------------------------------------------------------------
@router.get("/dynamic")
async def get_dynamic_categories(platform: Optional[str] = Query(None)):
    """
    Return the full category taxonomy plus live locations and seller types.
    Pass ?platform=farm_deals to exclude processed consumer-goods categories.
    Pass ?platform=home to exclude farm-only categories from the business marketplace.
    """
    subcategory_map = {
        ProductCategory.GRAINS_CEREALS.value:          [s.value for s in GrainsCerealsSubcategory],
        ProductCategory.BEANS_LEGUMES.value:           [s.value for s in BeansLegumesSubcategory],
        ProductCategory.FISH_MEAT.value:               [s.value for s in FishMeatSubcategory],
        ProductCategory.SPICES_VEGETABLES.value:       [s.value for s in SpicesVegetablesSubcategory],
        ProductCategory.TUBERS_ROOTS.value:            [s.value for s in TubersRootsSubcategory],
        ProductCategory.FLOUR_FLAKES.value:            [s.value for s in FlourFlakesSubcategory],
        ProductCategory.DRINKS_BEVERAGE.value:         [s.value for s in DrinksBeverageSubcategory],
        ProductCategory.SNACKS_CONFECTIONARIES.value:  [s.value for s in SnacksConfectionariesSubcategory],
        ProductCategory.SWEETS_SUGAR.value:            [s.value for s in SweetsSugarSubcategory],
        ProductCategory.FRUITS.value:                  [s.value for s in FruitsSubcategory],
        ProductCategory.CASH_CROP.value:               [s.value for s in CashCropSubcategory],
        ProductCategory.FEEDS.value:                   [s.value for s in FeedsSubcategory],
        ProductCategory.FARM_INPUTS.value:             [s.value for s in FarmInputsSubcategory],
        ProductCategory.OTHER.value:                   [],
    }

    categories_dict = {}
    for cat in ProductCategory:
        # Apply platform-based exclusions
        if platform == "farm_deals" and cat.value in BUSINESS_ONLY_CATEGORIES:
            continue

        subcats = subcategory_map.get(cat.value, [])
        categories_dict[cat.value] = {
            "name": _label(cat.value),
            "value": cat.value,
            "subcategories": {
                s: {"name": _label(s), "value": s}
                for s in subcats
            },
        }

    processing_levels = [
        {"value": pl.value, "label": _label(pl.value)}
        for pl in ProcessingLevel
    ]

    # Pull live distinct locations and seller_types from the products collection
    locations = []
    seller_types = []
    try:
        db = get_db()
        if db is not None:
            raw_locations = db.products.distinct("location")
            locations = sorted([loc for loc in raw_locations if loc])
            raw_seller_types = db.products.distinct("seller_type")
            seller_types = sorted([st for st in raw_seller_types if st])
    except Exception:
        locations = NIGERIAN_STATES
        seller_types = ["farmer", "agent", "business"]

    return {
        "categories": categories_dict,
        "processing_levels": processing_levels,
        "locations": locations,
        "seller_types": seller_types,
    }
