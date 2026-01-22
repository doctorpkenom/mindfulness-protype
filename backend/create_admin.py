"""
Script to create an admin account.
Run this script to create an admin user with the default credentials.
"""
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.db_models import Account, UserMLWeights, SystemLog
from backend.auth import get_password_hash

def create_admin_account():
    """Create the admin account."""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    try:
        # Check if admin account already exists
        existing_admin = db.query(Account).filter(
            (Account.username == "admin") | (Account.email == "admin@admin.com")
        ).first()
        
        if existing_admin:
            print(f"Admin account already exists!")
            print(f"  Username: {existing_admin.username}")
            print(f"  Email: {existing_admin.email}")
            print(f"  Is Admin: {existing_admin.is_admin}")
            # Update to ensure it's an admin
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                db.commit()
                print("  Updated: Set is_admin to True")
            return
        
        # Create admin account
        hashed_password = get_password_hash("admin")
        admin_account = Account(
            email="admin@admin.com",
            username="admin",
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True
        )
        db.add(admin_account)
        db.commit()
        db.refresh(admin_account)
        
        # Create personalized ML weights for admin
        ml_weights = UserMLWeights(account_id=admin_account.id)
        db.add(ml_weights)
        
        # Log admin account creation
        log = SystemLog(
            level="INFO",
            component="admin_setup",
            message="Admin account created",
            context_data={"account_id": admin_account.id, "username": "admin"}
        )
        db.add(log)
        db.commit()
        
        print("Admin account created successfully!")
        print(f"  Username: admin")
        print(f"  Email: admin@admin.com")
        print(f"  Password: admin")
        print(f"  Is Admin: True")
        
    except Exception as e:
        print(f"Error creating admin account: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_account()
