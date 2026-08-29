"""
File: maps_distance_service.py
Purpose: Resolves distance in kilometers between origin (home mandi/village) and candidate mandis.
         Pulls from stored distances table, falls back to Haversine GPS calculation, and includes
         a pluggable seam for Google Maps Distance Matrix API.
Inputs:  from_mandi_id (int), to_mandi_id (int), optional api_key (str)
Outputs: distance_km (float), source (str: 'database' | 'haversine' | 'google_maps')
Usage:   from services.maps_distance_service import get_distance_km
         dist, source = get_distance_km(from_mandi_id=1, to_mandi_id=2)
"""

import math
import requests
from models.distance_model import DistanceModel
from models.mandi_model import MandiModel
from config import Config

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes approximate road distance in km between two lat/lng coordinates
    using the Haversine formula multiplied by a road winding factor of 1.25.
    """
    R = 6371.0  # Earth radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    crow_flies_km = R * c
    
    # Road winding factor typically 1.2 - 1.3 for Indian highway networks
    road_km = crow_flies_km * 1.25
    return round(road_km, 1)

def get_distance_km(from_mandi_id, to_mandi_id):
    """
    Retrieves or calculates distance between two mandis using Google Maps Distance Matrix API,
    falling back to local database or Haversine GPS calculations.

    Parameters:
        from_mandi_id (int): ID of origin mandi
        to_mandi_id (int): ID of destination mandi

    Returns:
        tuple: (distance_km: float, source: str)
    """
    if from_mandi_id == to_mandi_id:
        return 0.0, "same_location"

    from_mandi = MandiModel.get_by_id(from_mandi_id)
    to_mandi = MandiModel.get_by_id(to_mandi_id)

    # 1. Check Google Maps Distance Matrix API if key is available
    if Config.GOOGLE_MAPS_API_KEY and from_mandi and to_mandi:
        lat1, lon1 = from_mandi.get("latitude"), from_mandi.get("longitude")
        lat2, lon2 = to_mandi.get("latitude"), to_mandi.get("longitude")
        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            try:
                maps_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
                params = {
                    "origins": f"{lat1},{lon1}",
                    "destinations": f"{lat2},{lon2}",
                    "mode": "driving",
                    "key": Config.GOOGLE_MAPS_API_KEY
                }
                res = requests.get(maps_url, params=params, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "OK" and data.get("rows"):
                        elem = data["rows"][0]["elements"][0]
                        if elem.get("status") == "OK" and "distance" in elem:
                            dist_km = round(elem["distance"]["value"] / 1000.0, 1)
                            DistanceModel.set_distance(from_mandi_id, to_mandi_id, dist_km)
                            return dist_km, "google_maps"
            except Exception:
                pass

    # 2. Check stored distance table
    stored_dist = DistanceModel.get_distance(from_mandi_id, to_mandi_id)
    if stored_dist is not None:
        return float(stored_dist), "database"

    # 3. Fallback to Haversine GPS calculation from coordinates
    from_mandi = MandiModel.get_by_id(from_mandi_id)
    to_mandi = MandiModel.get_by_id(to_mandi_id)

    if from_mandi and to_mandi:
        lat1, lon1 = from_mandi.get("latitude"), from_mandi.get("longitude")
        lat2, lon2 = to_mandi.get("latitude"), to_mandi.get("longitude")
        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            calc_dist = haversine_distance(lat1, lon1, lat2, lon2)
            # Cache computed distance in database for next time
            DistanceModel.set_distance(from_mandi_id, to_mandi_id, calc_dist)
            return calc_dist, "haversine"

    # Default fallback if coordinates unavailable
    return 100.0, "default_fallback"

if __name__ == "__main__":
    d, src = get_distance_km(1, 2)
    print(f"Distance between Mandi 1 and Mandi 2: {d} km (Source: {src})")
