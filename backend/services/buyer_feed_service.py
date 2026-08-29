"""
File: buyer_feed_service.py
Purpose: Powers the Buyer Marketplace feed. Fetches active deals, applies filters/sorting,
         and formats human-readable relative timestamps.
Security: Deliberately strips 'farmer_phone' from every deal card to protect farmers from spam.
Inputs:  crop_filter (str), location_filter (str), sort_by (str)
Outputs: List of deal dictionaries without phone numbers
Usage:   from services.buyer_feed_service import get_buyer_feed
         deals = get_buyer_feed(crop_filter="Wheat", sort_by="price_high")
"""

from datetime import datetime
from models.deal_model import DealModel

def format_posted_ago(posted_at_str):
    """Formats timestamp into human-readable relative time (e.g. '10m ago', '2h ago', 'Just now')."""
    if not posted_at_str:
        return "Recently"
    try:
        # Handles SQLite timestamps: 'YYYY-MM-DD HH:MM:SS'
        dt = datetime.fromisoformat(posted_at_str.replace("Z", ""))
        delta = datetime.utcnow() - dt
        seconds = delta.total_seconds()

        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    except Exception:
        return "Recently"

def get_buyer_feed(crop_filter=None, location_filter=None, sort_by="newest"):
    """
    Retrieves filtered and sorted active deals for the Buyer Marketplace.
    Strips farmer_phone to prevent indiscriminate cold-calling and scraping.
    """
    raw_deals = DealModel.get_active_deals(
        crop_filter=crop_filter,
        location_filter=location_filter,
        sort_by=sort_by
    )

    feed = []
    for d in raw_deals:
        feed.append({
            "id": d["id"],
            "crop_id": d["crop_id"],
            "crop_name": d["crop_name"],
            "quantity_quintal": d["quantity_quintal"],
            "price_per_quintal": d["price_per_quintal"],
            "total_deal_value": round(d["quantity_quintal"] * d["price_per_quintal"], 2),
            "location_name": d["location_name"],
            "farmer_name": d["farmer_name"],
            # farmer_phone is deliberately excluded here!
            "inquiry_count": d.get("inquiry_count", 0),
            "posted_at": d["posted_at"],
            "posted_ago": format_posted_ago(d["posted_at"]),
            "status": d["status"]
        })

    return feed
