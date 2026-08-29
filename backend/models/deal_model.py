"""
File: deal_model.py
Purpose: Data access and CRUD operations for direct-sale deals and deal inquiries.
Inputs:  Deal/inquiry payload fields, deal IDs
Outputs: Dictionaries and lists of deal/inquiry records
Usage:   from models.deal_model import DealModel
         deal = DealModel.create_deal(...)
         deals = DealModel.get_active_deals()
"""

from database.db_connection import query_db, execute_db

class DealModel:
    """Encapsulates database operations for the Direct Marketplace module."""

    @staticmethod
    def create_deal(farmer_name, farmer_phone, crop_id, crop_name, quantity_quintal, price_per_quintal, mandi_id=None, location_name=""):
        """Creates a new direct-sale deal listing."""
        sql = """
        INSERT INTO deals (
            farmer_name, farmer_phone, crop_id, crop_name,
            quantity_quintal, price_per_quintal, mandi_id, location_name, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active');
        """
        deal_id = execute_db(
            sql,
            (farmer_name, farmer_phone, crop_id, crop_name, quantity_quintal, price_per_quintal, mandi_id, location_name)
        )
        return DealModel.get_deal_by_id(deal_id)

    @staticmethod
    def get_deal_by_id(deal_id):
        """Retrieves single deal record by ID, including total inquiry count."""
        sql = """
        SELECT d.*, 
               (SELECT COUNT(*) FROM deal_inquiries i WHERE i.deal_id = d.id) as inquiry_count
        FROM deals d 
        WHERE d.id = ?;
        """
        rows = query_db(sql, (deal_id,))
        return rows[0] if rows else None

    @staticmethod
    def get_active_deals(crop_filter=None, location_filter=None, sort_by="newest"):
        """
        Fetches all active deals matching optional crop and location filters.
        Note: The buyer feed service removes farmer_phone before returning to public clients.
        """
        sql = """
        SELECT d.id, d.farmer_name, d.farmer_phone, d.crop_id, d.crop_name,
               d.quantity_quintal, d.price_per_quintal, d.mandi_id, d.location_name,
               d.status, d.posted_at,
               (SELECT COUNT(*) FROM deal_inquiries i WHERE i.deal_id = d.id) as inquiry_count
        FROM deals d
        WHERE d.status = 'active'
        """
        params = []

        if crop_filter:
            sql += " AND (LOWER(d.crop_name) LIKE ? OR d.crop_id = ?)"
            params.extend([f"%{crop_filter.lower()}%", crop_filter if crop_filter.isdigit() else -1])

        if location_filter:
            sql += " AND LOWER(d.location_name) LIKE ?"
            params.append(f"%{location_filter.lower()}%")

        if sort_by == "price_high":
            sql += " ORDER BY d.price_per_quintal DESC, d.posted_at DESC"
        elif sort_by == "price_low":
            sql += " ORDER BY d.price_per_quintal ASC, d.posted_at DESC"
        else:  # newest
            sql += " ORDER BY d.posted_at DESC"

        return query_db(sql, tuple(params))

    @staticmethod
    def mark_deal_sold(deal_id):
        """Marks a deal as sold."""
        sql = "UPDATE deals SET status = 'sold' WHERE id = ?;"
        return execute_db(sql, (deal_id,))

    @staticmethod
    def delete_deal(deal_id):
        """Cancels/removes a deal listing."""
        sql = "UPDATE deals SET status = 'cancelled' WHERE id = ?;"
        return execute_db(sql, (deal_id,))

    @staticmethod
    def create_inquiry(deal_id, buyer_name=None, buyer_phone=None):
        """Logs a buyer's inquiry for a deal listing."""
        sql = """
        INSERT INTO deal_inquiries (deal_id, buyer_name, buyer_phone)
        VALUES (?, ?, ?);
        """
        inquiry_id = execute_db(sql, (deal_id, buyer_name or "Anonymous Buyer", buyer_phone or "N/A"))
        return inquiry_id

    @staticmethod
    def get_inquiries_for_deal(deal_id):
        """Retrieves list of all inquiries received for a specific deal."""
        sql = "SELECT * FROM deal_inquiries WHERE deal_id = ? ORDER BY inquired_at DESC;"
        return query_db(sql, (deal_id,))

    @staticmethod
    def get_farmer_deals(farmer_phone=None):
        """Fetches active and recently sold deals for the farmer's management dashboard."""
        if farmer_phone:
            sql = """
            SELECT d.*, 
                   (SELECT COUNT(*) FROM deal_inquiries i WHERE i.deal_id = d.id) as inquiry_count
            FROM deals d
            WHERE d.farmer_phone = ? AND d.status != 'cancelled'
            ORDER BY d.posted_at DESC;
            """
            return query_db(sql, (farmer_phone,))
        else:
            sql = """
            SELECT d.*, 
                   (SELECT COUNT(*) FROM deal_inquiries i WHERE i.deal_id = d.id) as inquiry_count
            FROM deals d
            WHERE d.status != 'cancelled'
            ORDER BY d.posted_at DESC
            LIMIT 15;
            """
            return query_db(sql)
