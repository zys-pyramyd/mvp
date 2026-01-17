import os
import requests
import logging
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)

GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY')

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles.
    return c * r

def get_coordinates(address: str):
    """
    Geocode address to (lat, lon) using Geoapify
    """
    if not GEOAPIFY_API_KEY:
        logger.warning("GEOAPIFY_API_KEY not set. Returning None.")
        return None

    try:
        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": address,
            "apiKey": GEOAPIFY_API_KEY,
            "limit": 1
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['features']:
                props = data['features'][0]['properties']
                return (props['lat'], props['lon'])
    except Exception as e:
        logger.error(f"Geocoding Error: {e}")
    
    return None

def get_distance_km(origin: str, destination: str) -> float:
    """
    Get distance between two addresses in KM.
    """
    # Mock for Development if no Key
    if not GEOAPIFY_API_KEY:
        # Fallback Logic: Simple string matching for known routes
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Lagos -> Ibadan
        if ("lagos" in origin_lower and "ibadan" in dest_lower) or ("ibadan" in origin_lower and "lagos" in dest_lower):
            return 130.0
        # Lagos -> Abuja
        if ("lagos" in origin_lower and "abuja" in dest_lower) or ("abuja" in origin_lower and "lagos" in dest_lower):
            return 750.0
            
        logger.warning("Geoapify Key missing and route unknown. Defaulting to 50km.")
        return 50.0

    coords_origin = get_coordinates(origin)
    coords_dest = get_coordinates(destination)
    
    if coords_origin and coords_dest:
        return haversine(coords_origin[1], coords_origin[0], coords_dest[1], coords_dest[0])
    
    return 50.0 # Default fallback
