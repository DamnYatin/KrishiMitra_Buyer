"""
File: transport_cost_calculator.py
Purpose: Calculates per-quintal and total transport cost for a farmer shipping produce
         from their home mandi/village to a candidate mandi.
Formula: Transport Cost = Distance (km) x Rate (Rs/km/quintal) x Quantity (quintal)
Input:   distance_km (float), rate_per_km_per_quintal (float), quantity_quintal (float, default=1.0)
Output:  dict with per_quintal (float, INR) and total (float, INR)
Usage:   calculate_transport_cost(distance_km=145.0, rate_per_km_per_quintal=0.80, quantity_quintal=1.0)
"""

def calculate_transport_cost(distance_km, rate_per_km_per_quintal, quantity_quintal=1.0):
    """
    Calculates the transport cost based on distance, rate per km per quintal, and quantity.

    Parameters:
        distance_km (float): Distance in kilometers between origin and candidate mandi.
        rate_per_km_per_quintal (float): Transport freight rate in INR per km per quintal.
        quantity_quintal (float): Total quantity of crop in quintals (default: 1.0).

    Returns:
        dict: {
            "per_quintal": float (Transport cost for 1 quintal in INR),
            "total": float (Total transport cost for the specified quantity in INR),
            "distance_km": float,
            "rate_per_km_per_quintal": float,
            "quantity_quintal": float
        }
    """
    try:
        dist = float(distance_km) if distance_km is not None else 0.0
        rate = float(rate_per_km_per_quintal) if rate_per_km_per_quintal is not None else 0.0
        qty = float(quantity_quintal) if quantity_quintal is not None and float(quantity_quintal) > 0 else 1.0
    except (ValueError, TypeError):
        dist, rate, qty = 0.0, 0.0, 1.0

    per_quintal_cost = round(dist * rate, 2)
    total_cost = round(per_quintal_cost * qty, 2)

    return {
        "per_quintal": per_quintal_cost,
        "total": total_cost,
        "distance_km": round(dist, 2),
        "rate_per_km_per_quintal": round(rate, 4),
        "quantity_quintal": round(qty, 2)
    }

if __name__ == "__main__":
    result = calculate_transport_cost(distance_km=145.0, rate_per_km_per_quintal=0.80, quantity_quintal=10)
    print("Transport Cost Calculation Example:", result)
