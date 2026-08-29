"""
File: db_init.py
Purpose: Initializes SQLite database schema, creating tables for crops, mandis, prices,
         distances, transport rates, other costs, and users if they do not already exist.
Inputs:  db_path (optional str, defaults to Config.DB_PATH)
Outputs: Creates tables in SQLite database
Usage:   from database.db_init import init_db
         init_db()
"""

from database.db_connection import get_db_connection

def init_db(db_path=None):
    """Creates all required database tables if they do not already exist."""
    schema = """
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS mandis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        latitude REAL,
        longitude REAL
    );

    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        mandi_id INTEGER NOT NULL,
        price_per_quintal REAL NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
        FOREIGN KEY (mandi_id) REFERENCES mandis(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS distances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_mandi_id_or_village INTEGER NOT NULL,
        to_mandi_id INTEGER NOT NULL,
        distance_km REAL NOT NULL,
        FOREIGN KEY (from_mandi_id_or_village) REFERENCES mandis(id) ON DELETE CASCADE,
        FOREIGN KEY (to_mandi_id) REFERENCES mandis(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS transport_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rate_per_km_per_quintal REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS other_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mandi_id INTEGER NOT NULL UNIQUE,
        loading REAL DEFAULT 0,
        unloading REAL DEFAULT 0,
        market_charge REAL DEFAULT 0,
        FOREIGN KEY (mandi_id) REFERENCES mandis(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        home_mandi_id INTEGER,
        FOREIGN KEY (home_mandi_id) REFERENCES mandis(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        mandi_id INTEGER NOT NULL,
        price_per_quintal REAL NOT NULL,
        recorded_date DATE NOT NULL,
        FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
        FOREIGN KEY (mandi_id) REFERENCES mandis(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT NOT NULL,
        farmer_phone TEXT,
        crop_id INTEGER NOT NULL,
        crop_name TEXT NOT NULL,
        quantity_quintal REAL NOT NULL,
        price_per_quintal REAL NOT NULL,
        mandi_id INTEGER,
        location_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        posted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
        FOREIGN KEY (mandi_id) REFERENCES mandis(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS deal_inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deal_id INTEGER NOT NULL,
        buyer_name TEXT,
        buyer_phone TEXT,
        inquired_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE CASCADE
    );
    """

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(schema)
        
if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
