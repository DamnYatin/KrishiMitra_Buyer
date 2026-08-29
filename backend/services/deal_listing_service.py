"""
File: deal_listing_service.py
Purpose: Validates and creates a new direct-sale deal listing posted by a farmer.
Inputs:  farmer_name, farmer_phone, crop_id, quantity_quintal, price_per_quintal, mandi_id, location_name
Outputs: Dict representing the created deal record or structured validation error
Usage:   from services.deal_listing_service import create_deal_listing
         result = create_deal_listing("Ramesh Patil", "9876543210", 1, 10, 7200.0, 1, "Nagpur")
"""

from models.deal_model import DealModel
from models.crop_model import CropModel
from models.mandi_model import MandiModel

def create_deal_listing(farmer_name, farmer_phone, crop_id, quantity_quintal, price_per_quintal, mandi_id=None, location_name=""):
    """
    Validates farmer inputs and creates an active deal listing in the database.
    """
    farmer_name = (farmer_name or "").strip()
    if not farmer_name:
        return {"status": "error", "message": "Farmer name is required."}

    farmer_phone = (farmer_phone or "").strip()
    if farmer_phone:
        clean_phone = "".join(filter(str.isdigit, farmer_phone))
        if len(clean_phone) < 10:
            return {"status": "error", "message": "Please enter a valid 10-digit phone number."}
        farmer_phone = clean_phone[-10:]

    try:
        crop_id = int(crop_id)
        quantity_quintal = float(quantity_quintal)
        price_per_quintal = float(price_per_quintal)
    except (ValueError, TypeError):
        return {"status": "error", "message": "Invalid numeric crop, quantity, or price format."}

    if quantity_quintal <= 0:
        return {"status": "error", "message": "Quantity must be greater than zero."}

    if price_per_quintal <= 0:
        return {"status": "error", "message": "Asking price must be greater than zero."}

    # Resolve crop name
    crop = CropModel.get_by_id(crop_id)
    crop_name = crop["name"] if crop else f"Crop #{crop_id}"

    # Resolve location name if mandi_id is supplied
    if mandi_id:
        try:
            mandi_id = int(mandi_id)
            mandi = MandiModel.get_by_id(mandi_id)
            if mandi and not location_name:
                location_name = mandi["name"]
        except (ValueError, TypeError):
            mandi_id = None

    if not location_name:
        location_name = "Local Region"

    deal = DealModel.create_deal(
        farmer_name=farmer_name,
        farmer_phone=farmer_phone,
        crop_id=crop_id,
        crop_name=crop_name,
        quantity_quintal=quantity_quintal,
        price_per_quintal=price_per_quintal,
        mandi_id=mandi_id,
        location_name=location_name
    )

    return {
        "status": "success",
        "message": "Deal posted successfully to Buyer Marketplace!",
        "deal": deal
    }
