"""
File: net_price_calculator.py
Purpose: Calculates net realized farmer return per quintal and total net earnings
         after deducting transport and other mandi handling costs.
Formula: Total Cost = Transport Cost + Other Costs (Loading + Unloading + Market Charges)
         Net Price = Mandi Price - Total Cost
Input:   mandi_price_per_qtl (float), transport_cost_per_qtl (float), other_costs_per_qtl (float), quantity_quintal (float, default=1.0)
Output:  dict with net_price_per_quintal (float), total_cost_per_quintal (float), total_net_return (float), etc.
Usage:   calculate_net_price(mandi_price_per_qtl=7250.0, transport_cost_per_qtl=116.0, other_costs_per_qtl=0.0, quantity_quintal=10)
"""

def calculate_net_price(mandi_price_per_qtl, transport_cost_per_qtl, other_costs_per_qtl, quantity_quintal=1.0):
    """
    Computes net price realized by farmer after all logistical and operational deductions.

    Parameters:
        mandi_price_per_qtl (float): Gross mandi listing price per quintal in INR.
        transport_cost_per_qtl (float): Calculated transport cost per quintal in INR.
        other_costs_per_qtl (float): Total handling and mandi fees per quintal in INR.
        quantity_quintal (float): Number of quintals sold (default: 1.0).

    Returns:
        dict: {
            "mandi_price_per_qtl": float,
            "transport_cost_per_qtl": float,
            "other_costs_per_qtl": float,
            "total_cost_per_qtl": float,
            "net_price_per_qtl": float,
            "quantity_quintal": float,
            "gross_mandi_revenue": float,
            "total_expenses": float,
            "total_net_return": float
        }
    """
    try:
        gross_price = float(mandi_price_per_qtl) if mandi_price_per_qtl is not None else 0.0
        transport_cost = float(transport_cost_per_qtl) if transport_cost_per_qtl is not None else 0.0
        other_cost = float(other_costs_per_qtl) if other_costs_per_qtl is not None else 0.0
        qty = float(quantity_quintal) if quantity_quintal is not None and float(quantity_quintal) > 0 else 1.0
    except (ValueError, TypeError):
        gross_price, transport_cost, other_cost, qty = 0.0, 0.0, 0.0, 1.0

    total_cost_per_qtl = round(transport_cost + other_cost, 2)
    net_price_per_qtl = round(gross_price - total_cost_per_qtl, 2)

    gross_revenue = round(gross_price * qty, 2)
    total_expenses = round(total_cost_per_qtl * qty, 2)
    total_net_return = round(net_price_per_qtl * qty, 2)

    return {
        "mandi_price_per_qtl": round(gross_price, 2),
        "transport_cost_per_qtl": round(transport_cost, 2),
        "other_costs_per_qtl": round(other_cost, 2),
        "total_cost_per_qtl": total_cost_per_qtl,
        "net_price_per_qtl": net_price_per_qtl,
        "quantity_quintal": round(qty, 2),
        "gross_mandi_revenue": gross_revenue,
        "total_expenses": total_expenses,
        "total_net_return": total_net_return
    }

if __name__ == "__main__":
    res = calculate_net_price(
        mandi_price_per_qtl=7250.0,
        transport_cost_per_qtl=116.0,
        other_costs_per_qtl=0.0,
        quantity_quintal=10
    )
    print("Net Price Calculation Example:", res)
