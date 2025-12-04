import json
import os
from typing import List, Optional
from .user_persona import UserPersona

class UserManager:
    """
    Manages the database of simulated users.
    """
    def __init__(self, db_path="simulated_testing/users.json"):
        # Ensure path is absolute or relative to project root
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path
            
        self.users: List[UserPersona] = []
        self.load_users()

    def load_users(self):
        """Load users from JSON file."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.users = [UserPersona.from_dict(u) for u in data]
                print(f"[UserManager] Loaded {len(self.users)} users.")
            except Exception as e:
                print(f"[UserManager] Error loading users: {e}")
                self.users = []
        else:
            print("[UserManager] No user database found. Starting fresh.")
            self.users = []

    def save_users(self):
        """Save all users to JSON file."""
        try:
            data = [u.to_dict() for u in self.users]
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[UserManager] Saved {len(self.users)} users.")
        except Exception as e:
            print(f"[UserManager] Error saving users: {e}")

    def create_user(self, name, stress, energy, resilience=0.3) -> UserPersona:
        """Create and save a new user."""
        new_user = UserPersona(name, stress, energy, resilience)
        self.users.append(new_user)
        self.save_users()
        return new_user

    def get_user(self, name) -> Optional[UserPersona]:
        """Find a user by name."""
        for user in self.users:
            if user.name == name:
                return user
        return None
    
    def delete_user(self, name):
        """Delete a user by name."""
        self.users = [u for u in self.users if u.name != name]
        self.save_users()

    def get_all_users(self) -> List[UserPersona]:
        return self.users

if __name__ == "__main__":
    # Test
    mgr = UserManager()
    if not mgr.get_user("Test User"):
        mgr.create_user("Test User", 0.5, 0.5)
    print([u.name for u in mgr.get_all_users()])
