"""
File: price_model.py
Purpose: Data access and management methods for mandi crop price entities.
Inputs:  Crop ID, Mandi ID, price values, timestamps
Outputs: Price dictionaries with crop, mandi, price per quintal, and last updated timestamp
Usage:   from models.price_model import PriceModel
         prices = PriceModel.get_by_crop_id(1)
         PriceModel.upsert_price(crop_id=1, mandi_id=2, price=7250.0)
"""

from database.db_connection import query_db, execute_db

class PriceModel:
    """Mandi Crop Price Data Access Model"""

    @staticmethod
    def get_all():
        """Retrieve all active price listings with crop and mandi names."""
        query = """
        SELECT p.id, p.crop_id, c.name as crop_name, p.mandi_id, m.name as mandi_name,
               p.price_per_quintal, p.last_updated
        FROM prices p
        JOIN crops c ON p.crop_id = c.id
        JOIN mandis m ON p.mandi_id = m.id
        ORDER BY c.name, m.name;
        """
        return query_db(query)

    @staticmethod
    def get_by_crop_id(crop_id):
        """Retrieve current prices across all mandis for a specific crop."""
        query = """
        SELECT p.id, p.crop_id, c.name as crop_name, p.mandi_id, m.name as mandi_name,
               m.latitude, m.longitude, p.price_per_quintal, p.last_updated
        FROM prices p
        JOIN crops c ON p.crop_id = c.id
        JOIN mandis m ON p.mandi_id = m.id
        WHERE p.crop_id = ?
        ORDER BY p.price_per_quintal DESC;
        """
        return query_db(query, (crop_id,))

    @staticmethod
    def get_price(crop_id, mandi_id):
        """Retrieve price for a specific crop and mandi."""
        query = """
        SELECT id, crop_id, mandi_id, price_per_quintal, last_updated
        FROM prices
        WHERE crop_id = ? AND mandi_id = ?;
        """
        return query_db(query, (crop_id, mandi_id), one=True)

    @staticmethod
    def upsert_price(crop_id, mandi_id, price_per_quintal):
        """Insert or update mandi price for a crop."""
        existing = PriceModel.get_price(crop_id, mandi_id)
        if existing:
            query = """
            UPDATE prices 
            SET price_per_quintal = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?;
            """
            return execute_db(query, (price_per_quintal, existing["id"]))
        else:
            query = """
            INSERT INTO prices (crop_id, mandi_id, price_per_quintal)
            VALUES (?, ?, ?);
            """
            return execute_db(query, (crop_id, mandi_id, price_per_quintal))

    @staticmethod
    def get_price_history(crop_id, mandi_id=None, limit_days=7):
        """Retrieve historical price records for trend analytics."""
        if mandi_id:
            query = """
            SELECT ph.id, ph.crop_id, ph.mandi_id, m.name as mandi_name,
                   ph.price_per_quintal, ph.recorded_date
            FROM price_history ph
            JOIN mandis m ON ph.mandi_id = m.id
            WHERE ph.crop_id = ? AND ph.mandi_id = ?
            ORDER BY ph.recorded_date ASC
            LIMIT ?;
            """
            return query_db(query, (crop_id, mandi_id, limit_days))
        else:
            query = """
            SELECT ph.id, ph.crop_id, ph.mandi_id, m.name as mandi_name,
                   ph.price_per_quintal, ph.recorded_date
            FROM price_history ph
            JOIN mandis m ON ph.mandi_id = m.id
            WHERE ph.crop_id = ?
            ORDER BY ph.recorded_date ASC;
            """
            return query_db(query, (crop_id,))
