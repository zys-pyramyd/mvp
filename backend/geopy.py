from typing import Optional, Dict
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

class GeopyHelper:
    """
    Lightweight geocoding + distance helper.
    - If you pass a `db` (pymongo database object) to the constructor, results will be cached
      in a collection named 'geocode_cache' by default.
    - Use geocode_address to obtain {'latitude': float, 'longitude': float} or None.
    - Use distance_km(coord1, coord2) to compute geodesic distance in km.
    """
    def __init__(self, user_agent: str = "pyramyd_geocoder", db=None, cache_collection: str = "geocode_cache"):
        # Nominatim is used by default; you can swap in another geocoder if desired.
        self.geolocator = Nominatim(user_agent=user_agent, timeout=10)
        self.db = db
        self.cache_collection_name = cache_collection

    def _get_cache_collection(self):
        if not self.db:
            return None
        return self.db[self.cache_collection_name]

    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Geocode an address string. Returns dict {'latitude': float, 'longitude': float} or None."""
        if not address or not address.strip():
            return None

        coll = self._get_cache_collection()
        key = address.strip()
        if coll:
            cached = coll.find_one({"address": key})
            if cached and cached.get("latitude") is not None and cached.get("longitude") is not None:
                return {"latitude": float(cached["latitude"]), "longitude": float(cached["longitude"])}

        try:
            loc = self.geolocator.geocode(key, timeout=10)
            if not loc:
                return None
            result = {"latitude": float(loc.latitude), "longitude": float(loc.longitude)}

            # Save to cache
            if coll:
                coll.update_one(
                    {"address": key},
                    {"$set": {"address": key, "latitude": result["latitude"], "longitude": result["longitude"], "cached_at": time.time()}},
                    upsert=True
                )
            return result
        except Exception:
            # Any geocoding exception => return None to allow fallback logic upstream
            return None

    def coords_from_location_dict(self, loc: Optional[dict]) -> Optional[Dict[str, float]]:
        """
        Accepts dict that may contain 'latitude' or 'lat' or 'longitude' or 'lng' or 'address'.
        Returns normalized {'latitude': float, 'longitude': float} or None.
        """
        if not loc:
            return None

        # If explicit numeric coords present, use them
        lat = loc.get("latitude") or loc.get("lat")
        lng = loc.get("longitude") or loc.get("lng")
        try:
            if lat is not None and lng is not None:
                return {"latitude": float(lat), "longitude": float(lng)}
        except Exception:
            # fallthrough to geocode by address
            pass

        # Try to build from address field
        address = loc.get("address") or loc.get("full_address") or loc.get("formatted_address")
        if address:
            return self.geocode_address(address)

        return None

    @staticmethod
    def distance_km(coord_a: Dict[str, float], coord_b: Dict[str, float]) -> Optional[float]:
        """
        Compute geodesic distance in kilometers between coord_a and coord_b.
        coord_a and coord_b must be dicts with 'latitude' and 'longitude' floats.
        Returns float kilometers rounded to 2 decimals or None on error.
        """
        if not coord_a or not coord_b:
            return None
        try:
            a = (float(coord_a["latitude"]), float(coord_a["longitude"]))
            b = (float(coord_b["latitude"]), float(coord_b["longitude"]))
            return round(geodesic(a, b).km, 2)
        except Exception:
            return None
