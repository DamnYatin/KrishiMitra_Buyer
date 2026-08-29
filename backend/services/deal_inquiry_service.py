"""
File: deal_inquiry_service.py
Purpose: Handles buyer's explicit "I'm Interested" action.
         Logs the inquiry and unlocks the farmer's contact phone number.
Inputs:  deal_id (int), buyer_name (str), buyer_phone (str)
Outputs: Dict containing farmer contact info and deal summary, or error if deal inactive
Usage:   from services.deal_inquiry_service import register_inquiry
         contact = register_inquiry(deal_id=1, buyer_name="Suresh Trader", buyer_phone="9988776655")
"""

from models.deal_model import DealModel

def register_inquiry(deal_id, buyer_name=None, buyer_phone=None):
    """
    Registers a buyer's intent to purchase and releases the farmer's contact number.
    """
    try:
        deal_id = int(deal_id)
    except (ValueError, TypeError):
        return {"status": "error", "message": "Invalid deal ID format."}

    deal = DealModel.get_deal_by_id(deal_id)
    if not deal:
        return {"status": "error", "message": "Deal listing not found."}

    if deal["status"] != "active":
        return {
            "status": "error",
            "message": f"This deal is no longer active (Status: {deal['status'].capitalize()})."
        }

    # Log the inquiry
    inquiry_id = DealModel.create_inquiry(
        deal_id=deal_id,
        buyer_name=(buyer_name or "").strip() or "Verified Buyer",
        buyer_phone=(buyer_phone or "").strip() or "N/A"
    )

    # Return contact details to the verified inquirer
    return {
        "status": "success",
        "message": "Interest registered! Farmer contact details unlocked.",
        "inquiry_id": inquiry_id,
        "farmer_name": deal["farmer_name"],
        "farmer_phone": deal["farmer_phone"] or "Contact via KrishiMitra Mandi Link",
        "deal_summary": {
            "id": deal["id"],
            "crop_name": deal["crop_name"],
            "quantity_quintal": deal["quantity_quintal"],
            "price_per_quintal": deal["price_per_quintal"],
            "total_value": round(deal["quantity_quintal"] * deal["price_per_quintal"], 2),
            "location": deal["location_name"]
        }
    }
