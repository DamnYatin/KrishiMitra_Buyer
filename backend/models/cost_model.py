"""
File: cost_model.py
Purpose: Data access and management methods for other mandi costs (loading, unloading,
         market charges) and baseline transport rates per km per quintal.
Inputs:  Mandi ID, loading fee, unloading fee, market fee, transport rate
Outputs: Cost breakdown dictionaries and transport rates
Usage:   from models.cost_model import CostModel
         costs = CostModel.get_other_costs_by_mandi(1)
         rate = CostModel.get_transport_rate()
"""

from database.db_connection import query_db, execute_db
from config import Config

class CostModel:
    """Other Costs & Transport Rates Data Access Model"""

    @staticmethod
    def get_other_costs_by_mandi(mandi_id):
        """Retrieve loading, unloading, and market fees for a specific mandi."""
        query = """
        SELECT id, mandi_id, loading, unloading, market_charge
        FROM other_costs
        WHERE mandi_id = ?;
        """
        row = query_db(query, (mandi_id,), one=True)
        if row:
            return row
        return {"id": None, "mandi_id": mandi_id, "loading": 0.0, "unloading": 0.0, "market_charge": 0.0}

    @staticmethod
    def get_all_other_costs():
        """Retrieve other costs across all mandis."""
        query = """
        SELECT oc.id, oc.mandi_id, m.name as mandi_name, oc.loading, oc.unloading, oc.market_charge
        FROM other_costs oc
        JOIN mandis m ON oc.mandi_id = m.id
        ORDER BY m.name;
        """
        return query_db(query)

    @staticmethod
    def upsert_other_costs(mandi_id, loading=0.0, unloading=0.0, market_charge=0.0):
        """Insert or update loading, unloading, and market fees for a mandi."""
        existing = CostModel.get_other_costs_by_mandi(mandi_id)
        if existing and existing.get("id"):
            query = """
            UPDATE other_costs
            SET loading = ?, unloading = ?, market_charge = ?
            WHERE mandi_id = ?;
            """
            return execute_db(query, (loading, unloading, market_charge, mandi_id))
        else:
            query = """
            INSERT INTO other_costs (mandi_id, loading, unloading, market_charge)
            VALUES (?, ?, ?, ?);
            """
            return execute_db(query, (mandi_id, loading, unloading, market_charge))

    @staticmethod
    def get_transport_rate():
        """Retrieve current baseline transport rate per km per quintal."""
        query = "SELECT rate_per_km_per_quintal FROM transport_rates ORDER BY id DESC LIMIT 1;"
        row = query_db(query, one=True)
        if row and row.get("rate_per_km_per_quintal") is not None:
            return float(row["rate_per_km_per_quintal"])
        return Config.DEFAULT_TRANSPORT_RATE

    @staticmethod
    def set_transport_rate(rate_per_km_per_quintal):
        """Update or insert baseline transport rate."""
        query = "INSERT INTO transport_rates (rate_per_km_per_quintal) VALUES (?);"
        return execute_db(query, (rate_per_km_per_quintal,))
