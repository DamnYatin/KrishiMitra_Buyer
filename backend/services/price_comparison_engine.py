"""
File: price_comparison_engine.py
Purpose: Aggregates and aligns prices across all candidate mandis for a chosen crop,
         matching each mandi with its distance from the farmer's home mandi.
Inputs:  crop_id (int), home_mandi_id (int)
Outputs: list of dicts with mandi details, gross mandi prices, and distances from origin
Usage:   from services.price_comparison_engine import get_aligned_mandi_prices
         candidate_list = get_aligned_mandi_prices(crop_id=1, home_mandi_id=1)
"""

from models.price_model import PriceModel
from models.mandi_model import MandiModel
from services.maps_distance_service import get_distance_km

def get_aligned_mandi_prices(crop_id, home_mandi_id):
    """
    Fetches all candidate mandi prices for a crop and pairs them with distance from home mandi.

    Parameters:
        crop_id (int): Selected crop ID
        home_mandi_id (int): Farmer's origin/home mandi ID

    Returns:
        list[dict]: List of candidate mandi listings with distance and price info
    """
    prices = PriceModel.get_by_crop_id(crop_id)
    aligned_results = []

    for item in prices:
        mandi_id = item["mandi_id"]
        distance_km, distance_source = get_distance_km(home_mandi_id, mandi_id)

        aligned_results.append({
            "mandi_id": mandi_id,
            "mandi_name": item["mandi_name"],
            "crop_id": crop_id,
            "crop_name": item["crop_name"],
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "mandi_price_per_qtl": float(item["price_per_quintal"]),
            "distance_km": distance_km,
            "distance_source": distance_source,
            "last_updated": item.get("last_updated")
        })

    return aligned_results

if __name__ == "__main__":
    candidates = get_aligned_mandi_prices(crop_id=1, home_mandi_id=1)
    print(f"Aligned {len(candidates)} mandis for comparison.")
