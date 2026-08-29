"""
File: mandi_model.py
Purpose: Data access and management methods for Mandi (agricultural wholesale market) entities.
Inputs:  Mandi IDs, names, coordinates (latitude, longitude)
Outputs: Mandi dictionaries containing id, name, latitude, longitude
Usage:   from models.mandi_model import MandiModel
         mandis = MandiModel.get_all()
         mandi = MandiModel.get_by_id(1)
"""

from database.db_connection import query_db, execute_db

class MandiModel:
    """Mandi Data Access Model"""

    @staticmethod
    def get_all():
        """Retrieve all registered mandis."""
        query = "SELECT id, name, latitude, longitude FROM mandis ORDER BY id ASC;"
        return query_db(query)

    @staticmethod
    def get_by_id(mandi_id):
        """Retrieve a specific mandi by ID."""
        query = "SELECT id, name, latitude, longitude FROM mandis WHERE id = ?;"
        return query_db(query, (mandi_id,), one=True)

    @staticmethod
    def create(name, latitude=None, longitude=None):
        """Create a new mandi with geographic coordinates."""
        query = "INSERT INTO mandis (name, latitude, longitude) VALUES (?, ?, ?);"
        return execute_db(query, (name, latitude, longitude))

    @staticmethod
    def update(mandi_id, name, latitude=None, longitude=None):
        """Update a mandi's information."""
        query = "UPDATE mandis SET name = ?, latitude = ?, longitude = ? WHERE id = ?;"
        return execute_db(query, (name, latitude, longitude, mandi_id))

    @staticmethod
    def delete(mandi_id):
        """Delete a mandi by ID."""
        query = "DELETE FROM mandis WHERE id = ?;"
        return execute_db(query, (mandi_id,))
