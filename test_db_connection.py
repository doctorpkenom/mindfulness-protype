"""Quick test to verify SQLite database is working."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, init_db
from sqlalchemy import text, inspect

print("Testing SQLite database connection...")
print(f"Database file: {os.path.abspath('mindfulness.db')}")
print(f"File exists: {os.path.exists('mindfulness.db')}")

try:
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("[OK] Database connection successful")
    
    # Check tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"[OK] Found {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    print("\n[SUCCESS] SQLite is working! No database server needed.")
    print("SQLite is file-based - it uses mindfulness.db in your project folder.")
    
except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
    print("\nThis might mean:")
    print("1. The database file is locked (close any SQLite browsers)")
    print("2. There's a permission issue")
    print("3. SQLite module isn't working properly")
