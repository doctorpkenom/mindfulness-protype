import sys
import os
import shutil

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulated_testing.user_manager import UserManager
from simulated_testing.run_simulation import run_simulation

def test_backend():
    print("--- Testing Dashboard Backend ---")
    
    # 1. Setup Test DB
    test_db = "simulated_testing/test_users.json"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    mgr = UserManager(db_path=test_db)
    
    # 2. Test Create User
    print("Creating user...")
    user = mgr.create_user("Test Subject Alpha", 0.8, 0.2)
    assert user.name == "Test Subject Alpha"
    assert len(mgr.get_all_users()) == 1
    
    # 3. Test Persistence
    print("Testing persistence...")
    mgr2 = UserManager(db_path=test_db) # Reload
    loaded_user = mgr2.get_user("Test Subject Alpha")
    assert loaded_user is not None
    assert loaded_user.base_stress == 0.8
    
    # 4. Test Simulation
    print("Running simulation...")
    results = run_simulation(loaded_user)
    
    assert results["user_name"] == "Test Subject Alpha"
    assert len(results["daily_completion_rates"]) == 30
    assert "improvement" in results
    
    print(f"Simulation Success! Improvement: {results['improvement']:.2f}")
    
    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)
    print("--- Backend Verified ---")

if __name__ == "__main__":
    test_backend()
