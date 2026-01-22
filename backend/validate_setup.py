"""
Backend Setup Validation Script
Tests database connection, model imports, and table creation.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported."""
    print("[TEST] Testing imports...")
    try:
        from backend.database import Base, engine, init_db, get_db
        print("  [OK] Database module imported")
        
        from backend.db_models import (
            User, Interaction, Simulation, ModelPerformance,
            ResearchModule, SystemLog, Account, Task, Schedule,
            ScheduleItem, TimerSession, UserMLWeights
        )
        print("  [OK] All database models imported")
        
        from backend.auth import (
            verify_password, get_password_hash, create_access_token,
            get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
        )
        print("  [OK] Auth module imported")
        
        from backend.models import (
            Token, UserSignup, TaskCreate, TaskResponse,
            ScheduleOptimizeRequest, TimerStartRequest
        )
        print("  [OK] Pydantic models imported")
        
        from backend.routers import auth, tasks, schedule, timer
        print("  [OK] Router modules imported")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection."""
    print("\n[TEST] Testing database connection...")
    try:
        from backend.database import engine, get_db
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("  [OK] Database connection successful")
        return True
    except Exception as e:
        print(f"  [FAIL] Database connection failed: {e}")
        return False

def test_table_creation():
    """Test that all tables can be created."""
    print("\n[TEST] Testing table creation...")
    try:
        from backend.database import Base, engine, init_db
        from backend.db_models import (
            User, Interaction, Simulation, ModelPerformance,
            ResearchModule, SystemLog, Account, Task, Schedule,
            ScheduleItem, TimerSession, UserMLWeights
        )
        
        # Get all table names
        table_names = Base.metadata.tables.keys()
        expected_tables = {
            'users', 'interactions', 'simulations', 'model_performance',
            'research_modules', 'system_logs', 'accounts', 'tasks',
            'schedules', 'schedule_items', 'timer_sessions', 'user_ml_weights'
        }
        
        print(f"  📊 Found {len(table_names)} tables:")
        for table in sorted(table_names):
            print(f"     - {table}")
        
        missing = expected_tables - set(table_names)
        if missing:
            print(f"  [WARN] Missing tables: {missing}")
            print("  [INFO] Attempting to create tables...")
            init_db()
            # Re-check
            table_names = Base.metadata.tables.keys()
            missing = expected_tables - set(table_names)
            if missing:
                print(f"  [FAIL] Still missing: {missing}")
                return False
        
        print("  [OK] All expected tables found")
        return True
    except Exception as e:
        print(f"  [FAIL] Table creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """Test basic database operations."""
    print("\n[TEST] Testing database operations...")
    try:
        from backend.database import get_db
        from backend.db_models import Account, SystemLog
        from backend.auth import get_password_hash
        from datetime import datetime
        
        db = next(get_db())
        
        # Test Account creation
        test_email = "test@example.com"
        test_username = "testuser"
        
        # Check if test account exists
        existing = db.query(Account).filter(
            (Account.email == test_email) | (Account.username == test_username)
        ).first()
        
        if existing:
            print(f"  ℹ️  Test account already exists, skipping creation")
        else:
            test_account = Account(
                email=test_email,
                username=test_username,
                hashed_password=get_password_hash("testpass123"),
                is_admin=False,
                is_active=True
            )
            db.add(test_account)
            db.commit()
            db.refresh(test_account)
            print(f"  [OK] Created test account (ID: {test_account.id})")
            
            # Clean up
            db.delete(test_account)
            db.commit()
            print("  [OK] Cleaned up test account")
        
        # Test SystemLog creation
        test_log = SystemLog(
            level="INFO",
            component="validation",
            message="Test log entry from validation script",
            context_data={"test": True}
        )
        db.add(test_log)
        db.commit()
        db.refresh(test_log)
        print(f"  [OK] Created test log (ID: {test_log.id})")
        
        # Clean up
        db.delete(test_log)
        db.commit()
        print("  [OK] Cleaned up test log")
        
        db.close()
        return True
    except Exception as e:
        print(f"  [FAIL] Database operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_functions():
    """Test authentication functions."""
    print("\n[TEST] Testing auth functions...")
    try:
        from backend.auth import get_password_hash, verify_password
        
        test_password = "testpass123"
        hashed = get_password_hash(test_password)
        print("  [OK] Password hashing works")
        
        if verify_password(test_password, hashed):
            print("  [OK] Password verification works")
        else:
            print("  [FAIL] Password verification failed")
            return False
        
        if not verify_password("wrongpass", hashed):
            print("  [OK] Wrong password correctly rejected")
        else:
            print("  [FAIL] Wrong password incorrectly accepted")
            return False
        
        return True
    except Exception as e:
        print(f"  [FAIL] Auth functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Backend Setup Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Table Creation", test_table_creation()))
    results.append(("Database Operations", test_database_operations()))
    results.append(("Auth Functions", test_auth_functions()))
    
    print("\n" + "=" * 60)
    print("Validation Results")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("SUCCESS: All tests passed! Backend is ready.")
        return 0
    else:
        print("WARNING: Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
