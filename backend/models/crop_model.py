"""
File: crop_model.py
Purpose: Data access and management methods for agricultural crop entities.
Inputs:  Crop IDs, crop names, or database queries
Outputs: Crop dictionaries containing id and name
Usage:   from models.crop_model import CropModel
         crops = CropModel.get_all()
         crop = CropModel.get_by_id(1)
"""

from database.db_connection import query_db, execute_db

class CropModel:
    """Crop Data Access Model"""

    @staticmethod
    def get_all():
        """Retrieve all available crops."""
        query = "SELECT id, name FROM crops ORDER BY id ASC;"
        return query_db(query)

    @staticmethod
    def get_by_id(crop_id):
        """Retrieve a specific crop by ID."""
        query = "SELECT id, name FROM crops WHERE id = ?;"
        return query_db(query, (crop_id,), one=True)

    @staticmethod
    def create(name):
        """Create a new crop."""
        query = "INSERT INTO crops (name) VALUES (?);"
        return execute_db(query, (name,))

    @staticmethod
    def update(crop_id, name):
        """Update a crop's name."""
        query = "UPDATE crops SET name = ? WHERE id = ?;"
        return execute_db(query, (name, crop_id))

    @staticmethod
    def delete(crop_id):
        """Delete a crop by ID."""
        query = "DELETE FROM crops WHERE id = ?;"
        return execute_db(query, (crop_id,))
