"""
File: admin_panel.py
Purpose: Administrative management controller providing CRUD operations for crops, mandis,
         transport freight rates, distances between markets, handling costs, and registered users.
Inputs:  Entity payload dictionaries, record IDs
Outputs: Success/error response dictionaries and lists of administrative records
Usage:   from admin.admin_panel import AdminController
         crops = AdminController.list_all_data()
         AdminController.update_transport_rate(0.85)
"""

from models.crop_model import CropModel
from models.mandi_model import MandiModel
from models.price_model import PriceModel
from models.distance_model import DistanceModel
from models.cost_model import CostModel
from database.db_connection import query_db, execute_db
from config import Config

class AdminController:
    """Administrative CRUD controller for system configuration."""

    @staticmethod
    def authenticate(username, password):
        """
        Validates admin login credentials against configuration.
        Returns auth token on match.
        """
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            return {
                "status": "success",
                "authenticated": True,
                "token": Config.ADMIN_AUTH_TOKEN,
                "username": Config.ADMIN_USERNAME,
                "message": "Authentication successful"
            }
        return {
            "status": "error",
            "authenticated": False,
            "message": "Invalid username or password"
        }

    @staticmethod
    def validate_token(token):
        """Validates provided authorization token."""
        return token == Config.ADMIN_AUTH_TOKEN

    @staticmethod
    def get_full_admin_overview():
        """Aggregates all administrative datasets for the admin dashboard."""
        return {
            "crops": CropModel.get_all(),
            "mandis": MandiModel.get_all(),
            "prices": PriceModel.get_all(),
            "distances": DistanceModel.get_all(),
            "transport_rate": CostModel.get_transport_rate(),
            "other_costs": CostModel.get_all_other_costs(),
            "users": query_db("SELECT u.id, u.name, u.phone, m.name as home_mandi_name FROM users u LEFT JOIN mandis m ON u.home_mandi_id = m.id;")
        }

    # --- Crops CRUD ---
    @staticmethod
    def add_crop(name):
        crop_id = CropModel.create(name)
        return {"status": "success", "id": crop_id, "message": "Crop created successfully"}

    @staticmethod
    def update_crop(crop_id, name):
        CropModel.update(crop_id, name)
        return {"status": "success", "message": "Crop updated successfully"}

    @staticmethod
    def delete_crop(crop_id):
        CropModel.delete(crop_id)
        return {"status": "success", "message": "Crop deleted successfully"}

    # --- Mandis CRUD ---
    @staticmethod
    def add_mandi(name, latitude, longitude):
        mandi_id = MandiModel.create(name, latitude, longitude)
        return {"status": "success", "id": mandi_id, "message": "Mandi created successfully"}

    @staticmethod
    def update_mandi(mandi_id, name, latitude, longitude):
        MandiModel.update(mandi_id, name, latitude, longitude)
        return {"status": "success", "message": "Mandi updated successfully"}

    @staticmethod
    def delete_mandi(mandi_id):
        MandiModel.delete(mandi_id)
        return {"status": "success", "message": "Mandi deleted successfully"}

    # --- Transport Rate CRUD ---
    @staticmethod
    def update_transport_rate(rate_per_km_per_quintal):
        CostModel.set_transport_rate(float(rate_per_km_per_quintal))
        return {"status": "success", "rate": float(rate_per_km_per_quintal), "message": "Transport rate updated"}

    # --- Distances CRUD ---
    @staticmethod
    def set_distance(from_id, to_id, distance_km):
        DistanceModel.set_distance(int(from_id), int(to_id), float(distance_km))
        return {"status": "success", "message": "Distance updated successfully"}

    @staticmethod
    def delete_distance(distance_id):
        DistanceModel.delete(int(distance_id))
        return {"status": "success", "message": "Distance record deleted"}

    # --- Other Costs CRUD ---
    @staticmethod
    def update_other_costs(mandi_id, loading, unloading, market_charge):
        CostModel.upsert_other_costs(int(mandi_id), float(loading), float(unloading), float(market_charge))
        return {"status": "success", "message": "Other costs updated successfully"}

    # --- Prices CRUD ---
    @staticmethod
    def update_price(crop_id, mandi_id, price_per_quintal):
        PriceModel.upsert_price(int(crop_id), int(mandi_id), float(price_per_quintal))
        return {"status": "success", "message": "Price updated successfully"}

if __name__ == "__main__":
    overview = AdminController.get_full_admin_overview()
    print("Admin Controller loaded. Found crops:", len(overview["crops"]))
