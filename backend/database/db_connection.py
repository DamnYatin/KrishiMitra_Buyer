"""
File: db_connection.py
Purpose: Provides thread-safe SQLite database connection and cursor context management.
Inputs:  db_path (optional str, defaults to Config.DB_PATH)
Outputs: sqlite3.Connection with Row dictionary factory
Usage:   from database.db_connection import get_db_connection
         with get_db_connection() as conn:
             cursor = conn.cursor()
             cursor.execute("SELECT * FROM crops")
             rows = cursor.fetchall()
"""

import sqlite3
import os
from contextlib import contextmanager
from config import Config

def dict_factory(cursor, row):
    """Convert sqlite3 row tuple into a python dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@contextmanager
def get_db_connection(db_path=None):
    """
    Context manager for SQLite database connection.
    Ensures commit on success and rollback on failure, then automatically closes the connection.
    """
    if db_path is None:
        db_path = Config.DB_PATH

    # Ensure parent directory exists
    parent_dir = os.path.dirname(db_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def query_db(query, args=(), one=False, db_path=None):
    """
    Helper function to query database and return dictionary results.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), db_path=None):
    """
    Helper function to execute INSERT, UPDATE, DELETE queries.
    Returns the lastrowid.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return cursor.lastrowid
