"""
File: analytics_reports_service.py
Purpose: Generates price trend analytics, 7-day historical price movements, and market insights
         for agricultural commodities across regional mandis.
Inputs:  crop_id (int)
Outputs: dict with historical series per mandi, 7-day price changes, and high/low ranges
Usage:   from services.analytics_reports_service import get_crop_analytics
         analytics = get_crop_analytics(crop_id=1)
"""

from models.crop_model import CropModel
from models.mandi_model import MandiModel
from models.price_model import PriceModel

def get_crop_analytics(crop_id):
    """
    Retrieves 7-day price series and computes trend metrics for a crop across all mandis.

    Parameters:
        crop_id (int): Identifier of crop

    Returns:
        dict: Analytics payload including mandi-wise trends, summary stats, and market direction
    """
    crop = CropModel.get_by_id(crop_id)
    if not crop:
        return {"error": "Crop not found", "crop_id": crop_id}

    mandis = MandiModel.get_all()
    history_records = PriceModel.get_price_history(crop_id)

    # Group historical prices by mandi
    mandi_history = {m["id"]: [] for m in mandis}
    for record in history_records:
        m_id = record["mandi_id"]
        if m_id in mandi_history:
            mandi_history[m_id].append({
                "date": record["recorded_date"],
                "price": float(record["price_per_quintal"])
            })

    mandi_trends = []
    all_prices = []

    for mandi in mandis:
        m_id = mandi["id"]
        series = mandi_history.get(m_id, [])
        # Sort by date
        series.sort(key=lambda x: x["date"])
        prices = [s["price"] for s in series]
        all_prices.extend(prices)

        current_price = prices[-1] if prices else 0.0
        start_price = prices[0] if prices else current_price
        diff = round(current_price - start_price, 2)
        pct_change = round((diff / start_price * 100), 2) if start_price else 0.0

        if diff > 10:
            trend_direction = "up"
        elif diff < -10:
            trend_direction = "down"
        else:
            trend_direction = "stable"

        mandi_trends.append({
            "mandi_id": m_id,
            "mandi_name": mandi["name"],
            "current_price": current_price,
            "7_day_change": diff,
            "7_day_pct_change": pct_change,
            "trend_direction": trend_direction,
            "price_series": series
        })

    avg_price = round(sum(all_prices) / len(all_prices), 2) if all_prices else 0.0
    min_price = min(all_prices) if all_prices else 0.0
    max_price = max(all_prices) if all_prices else 0.0

    return {
        "crop_id": crop_id,
        "crop_name": crop["name"],
        "summary": {
            "average_price": avg_price,
            "min_price": min_price,
            "max_price": max_price,
            "spread": round(max_price - min_price, 2)
        },
        "mandi_trends": mandi_trends
    }

if __name__ == "__main__":
    report = get_crop_analytics(crop_id=1)
    print("Crop Analytics Summary:", report["summary"])
