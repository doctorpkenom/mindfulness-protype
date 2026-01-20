"""
Seed database with diverse test users and initial data for testing.
Run this script to populate the database with realistic personas.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.db_models import User, SystemLog, ResearchModule
from processor.research_engine import ResearchEngine
from datetime import datetime

def create_diverse_users():
    """Create a variety of user personas for testing."""
    personas = [
        {
            "name": "Stressed Executive",
            "base_stress": 0.8,
            "base_energy": 0.4,
            "resilience": 0.3,
            "description": "High-pressure job, constant meetings, low energy"
        },
        {
            "name": "Anxious Student",
            "base_stress": 0.7,
            "base_energy": 0.6,
            "resilience": 0.4,
            "description": "Exams approaching, moderate energy, building resilience"
        },
        {
            "name": "Balanced Professional",
            "base_stress": 0.4,
            "base_energy": 0.7,
            "resilience": 0.6,
            "description": "Good work-life balance, solid energy, high resilience"
        },
        {
            "name": "Burnt Out Creative",
            "base_stress": 0.9,
            "base_energy": 0.2,
            "resilience": 0.2,
            "description": "Extreme burnout, very low energy, needs recovery"
        },
        {
            "name": "Energetic Founder",
            "base_stress": 0.5,
            "base_energy": 0.9,
            "resilience": 0.7,
            "description": "High energy, moderate stress, resilient entrepreneur"
        },
        {
            "name": "Mindful Practitioner",
            "base_stress": 0.2,
            "base_energy": 0.8,
            "resilience": 0.8,
            "description": "Regular meditation practice, high resilience"
        },
        {
            "name": "Overwhelmed Parent",
            "base_stress": 0.6,
            "base_energy": 0.3,
            "resilience": 0.5,
            "description": "Juggling family and work, tired but resilient"
        },
        {
            "name": "Night Owl Developer",
            "base_stress": 0.5,
            "base_energy": 0.6,
            "resilience": 0.5,
            "description": "Late-night work sessions, moderate stats"
        },
        {
            "name": "Recovering Workaholic",
            "base_stress": 0.7,
            "base_energy": 0.5,
            "resilience": 0.4,
            "description": "Trying to improve work-life balance"
        },
        {
            "name": "Productivity Enthusiast",
            "base_stress": 0.3,
            "base_energy": 0.8,
            "resilience": 0.7,
            "description": "Loves optimization, high energy, low stress"
        }
    ]
    
    return personas

def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out to preserve data)
        print("Clearing existing data...")
        db.query(User).delete()
        db.query(SystemLog).delete()
        db.query(ResearchModule).delete()
        db.commit()
        
        # Create users
        print("\n👥 Creating diverse user personas...")
        personas = create_diverse_users()
        created_users = []
        
        for persona in personas:
            user = User(
                name=persona["name"],
                base_stress=persona["base_stress"],
                base_energy=persona["base_energy"],
                resilience=persona["resilience"]
            )
            db.add(user)
            created_users.append(persona)
            print(f"  ✓ Created: {persona['name']} - {persona['description']}")
        
        db.commit()
        print(f"\n✅ Created {len(created_users)} users")
        
        # Load and index research modules
        print("\n📚 Indexing research modules...")
        engine = ResearchEngine()
        
        for module in engine.modules:
            module_id = module.get("id")
            title = module.get("title")
            
            research_module = ResearchModule(
                module_id=module_id,
                title=title,
                times_used=0,
                success_rate=0.0,
                is_active=True,
                module_data=module
            )
            db.add(research_module)
            print(f"  ✓ Indexed: {title}")
        
        db.commit()
        print(f"\n✅ Indexed {len(engine.modules)} research modules")
        
        # Create initial system logs
        print("\n📝 Creating system logs...")
        logs = [
            SystemLog(
                level="INFO",
                component="system",
                message="Database seeded with test data",
                context_data={
                    "users_created": len(created_users),
                    "modules_indexed": len(engine.modules)
                }
            ),
            SystemLog(
                level="INFO",
                component="ml_coordinator",
                message="ML models initialized and ready",
                context_data={"models": 7}
            )
        ]
        
        for log in logs:
            db.add(log)
        
        db.commit()
        print(f"✅ Created {len(logs)} system logs")
        
        # Summary
        print("\n" + "="*60)
        print("🎉 DATABASE SEEDING COMPLETE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Users: {len(created_users)}")
        print(f"  • Research Modules: {len(engine.modules)}")
        print(f"  • Total Strategies: {len(engine.strategies)}")
        print(f"  • ML Models: 7 (Habit, Stress, Curiosity, Flow, Attention, Motivation, Zeigarnik)")
        print(f"\n💡 Next steps:")
        print(f"  1. Start backend: uvicorn backend.main:app --reload")
        print(f"  2. Start frontend: cd frontend && npm run dev")
        print(f"  3. Open browser: http://localhost:5173")
        print(f"  4. Explore the Dashboard to see analytics")
        print(f"  5. Run simulations to generate data")
        print()
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
