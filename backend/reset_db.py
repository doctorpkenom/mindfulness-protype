"""
Reset database script - drops and recreates all tables.
Run this after adding new models to ensure tables are created.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import reset_db

if __name__ == "__main__":
    print("Resetting database...")
    reset_db()
    print("Done! All tables have been recreated.")
    print("You can now restart the backend server.")
