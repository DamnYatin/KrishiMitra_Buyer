"""
File: distance_model.py
Purpose: Data access and management methods for geographical distances between mandis/villages.
Inputs:  Origin ID, Destination ID, Distance in kilometers
Outputs: Distance dictionaries containing source, destination, and distance in km
Usage:   from models.distance_model import DistanceModel
         dist = DistanceModel.get_distance(from_id=1, to_id=2)
         DistanceModel.set_distance(from_id=1, to_id=2, distance_km=145.0)
"""

from database.db_connection import query_db, execute_db

class DistanceModel:
    """Distance Data Access Model"""

    @staticmethod
    def get_all():
        """Retrieve all stored distance pairs."""
        query = """
        SELECT d.id, d.from_mandi_id_or_village, m1.name as from_name,
               d.to_mandi_id, m2.name as to_name, d.distance_km
        FROM distances d
        JOIN mandis m1 ON d.from_mandi_id_or_village = m1.id
        JOIN mandis m2 ON d.to_mandi_id = m2.id
        ORDER BY m1.name, m2.name;
        """
        return query_db(query)

    @staticmethod
    def get_distance(from_id, to_id):
        """
        Retrieve stored distance between two mandis (checking both directions).
        """
        if from_id == to_id:
            return 0.0
        query = """
        SELECT distance_km FROM distances
        WHERE (from_mandi_id_or_village = ? AND to_mandi_id = ?)
           OR (from_mandi_id_or_village = ? AND to_mandi_id = ?)
        LIMIT 1;
        """
        row = query_db(query, (from_id, to_id, to_id, from_id), one=True)
        return row["distance_km"] if row else None

    @staticmethod
    def set_distance(from_id, to_id, distance_km):
        """Set or update distance between two mandis."""
        existing_query = """
        SELECT id FROM distances
        WHERE (from_mandi_id_or_village = ? AND to_mandi_id = ?)
           OR (from_mandi_id_or_village = ? AND to_mandi_id = ?)
        LIMIT 1;
        """
        row = query_db(existing_query, (from_id, to_id, to_id, from_id), one=True)
        if row:
            update_query = "UPDATE distances SET distance_km = ? WHERE id = ?;"
            return execute_db(update_query, (distance_km, row["id"]))
        else:
            insert_query = """
            INSERT INTO distances (from_mandi_id_or_village, to_mandi_id, distance_km)
            VALUES (?, ?, ?);
            """
            return execute_db(insert_query, (from_id, to_id, distance_km))

    @staticmethod
    def delete(distance_id):
        """Delete a distance record."""
        query = "DELETE FROM distances WHERE id = ?;"
        return execute_db(query, (distance_id,))
