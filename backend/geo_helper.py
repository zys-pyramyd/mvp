from typing import Optional, Dict
import time
import math
import requests

class GeopyHelper:
    """
    Lightweight geocoding + distance helper using Geoapify.
    - If you pass a `db` (pymongo database object) to the constructor, results will be cached
      in a collection named 'geocode_cache' by default.
    - Use geocode_address to obtain {'latitude': float, 'longitude': float} or None.
    - Use distance_km(coord1, coord2) to compute geodesic distance in km.
    """
    def __init__(self, api_key: str, user_agent: str = "pyramyd_geocoder", db=None, cache_collection: str = "geocode_cache"):
        self.api_key = api_key
        self.db = db
        self.cache_collection_name = cache_collection
        self.base_url = "https://api.geoapify.com/v1/geocode/search"

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
        
        # Check cache first
        if coll:
            cached = coll.find_one({"address": key})
            if cached and cached.get("latitude") is not None and cached.get("longitude") is not None:
                return {"latitude": float(cached["latitude"]), "longitude": float(cached["longitude"])}

        # Call Geoapify API
        try:
            params = {
                "text": key,
                "apiKey": self.api_key,
                "limit": 1
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('features'):
                    # Geoapify returns [lon, lat]
                    lon = data['features'][0]['geometry']['coordinates'][0]
                    lat = data['features'][0]['geometry']['coordinates'][1]
                    
                    result = {"latitude": float(lat), "longitude": float(lon)}

                    # Save to cache
                    if coll:
                        coll.update_one(
                            {"address": key},
                            {"$set": {"address": key, "latitude": result["latitude"], "longitude": result["longitude"], "cached_at": time.time()}},
                            upsert=True
                        )
                    return result
            
            return None
        except Exception as e:
            print(f"Geocoding error for '{key}': {e}")
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

    def distance_km(self, coord_a: Dict[str, float], coord_b: Dict[str, float]) -> Optional[float]:
        """
        Compute driving distance in kilometers between coord_a and coord_b using Geoapify Routing API.
        coord_a and coord_b must be dicts with 'latitude' and 'longitude' floats.
        Returns float kilometers rounded to 2 decimals or None on error.
        """
        if not coord_a or not coord_b:
            return None
        
        try:
            lat1 = float(coord_a["latitude"])
            lon1 = float(coord_a["longitude"])
            lat2 = float(coord_b["latitude"])
            lon2 = float(coord_b["longitude"])
            
            # Construct waypoints string: lat1,lon1|lat2,lon2
            waypoints = f"{lat1},{lon1}|{lat2},{lon2}"
            
            routing_url = "https://api.geoapify.com/v1/routing"
            params = {
                "waypoints": waypoints,
                "mode": "drive",
                "apiKey": self.api_key
            }
            
            response = requests.get(routing_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('features'):
                    # Distance is in meters in properties
                    distance_meters = data['features'][0]['properties']['distance']
                    return round(distance_meters / 1000, 2)
            
            print(f"Routing API failed: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"Distance calculation error: {e}")
            return None
