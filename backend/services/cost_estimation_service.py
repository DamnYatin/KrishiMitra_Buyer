"""
File: cost_estimation_service.py
Purpose: Retrieves and calculates additional market costs (loading, unloading, and mandi cess/charges)
         for a candidate mandi.
Formula: Total Other Costs = (Loading + Unloading + Market Charges) x Quantity
Input:   mandi_id (int), quantity_quintal (float, default=1.0)
Output:  dict with itemized and aggregated other costs (per quintal and total)
Usage:   from services.cost_estimation_service import estimate_other_costs
         costs = estimate_other_costs(mandi_id=1, quantity_quintal=10)
"""

from models.cost_model import CostModel

def estimate_other_costs(mandi_id, quantity_quintal=1.0):
    """
    Looks up statutory and handling charges for a mandi and computes other costs.

    Parameters:
        mandi_id (int): ID of the mandi where produce will be sold.
        quantity_quintal (float): Total quantity in quintals (default: 1.0).

    Returns:
        dict: {
            "loading_per_qtl": float,
            "unloading_per_qtl": float,
            "market_charge_per_qtl": float,
            "per_quintal": float,
            "total": float
        }
    """
    try:
        qty = float(quantity_quintal) if quantity_quintal is not None and float(quantity_quintal) > 0 else 1.0
    except (ValueError, TypeError):
        qty = 1.0

    cost_data = CostModel.get_other_costs_by_mandi(mandi_id)
    loading = float(cost_data.get("loading", 0.0) or 0.0)
    unloading = float(cost_data.get("unloading", 0.0) or 0.0)
    market_charge = float(cost_data.get("market_charge", 0.0) or 0.0)

    per_quintal = round(loading + unloading + market_charge, 2)
    total_other = round(per_quintal * qty, 2)

    return {
        "loading_per_qtl": round(loading, 2),
        "unloading_per_qtl": round(unloading, 2),
        "market_charge_per_qtl": round(market_charge, 2),
        "per_quintal": per_quintal,
        "total": total_other
    }

if __name__ == "__main__":
    costs = estimate_other_costs(mandi_id=1, quantity_quintal=5)
    print("Estimated Other Costs:", costs)
