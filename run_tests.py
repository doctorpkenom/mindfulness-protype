"""
Comprehensive test suite for the Mindfulness Prototype.
Tests ML models, research engine, database operations, and API endpoints.
"""
import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml.online_coordinator import OnlineCoordinator
from processor.research_engine import ResearchEngine
from data_pipeline.preprocessor import DataPreprocessor
from backend.database import SessionLocal, init_db
from backend.db_models import User, Interaction
from simulated_testing.user_persona import UserPersona

def test_ml_models():
    """Test all ML models."""
    print("\n🧠 Testing ML Models...")
    print("="*60)
    
    coordinator = OnlineCoordinator()
    preprocessor = DataPreprocessor()
    
    # Test contexts
    test_contexts = [
        {"energy": "high", "stress": "low"},
        {"energy": "low", "stress": "high"},
        {"energy": "medium", "stress": "medium"},
        {"energy": "low", "stress": "low"},
        {"energy": "high", "stress": "high"}
    ]
    
    mock_strategies = [
        {"name": "Deep Work", "tags": ["productivity", "flow"], "difficulty": "High"},
        {"name": "Mindful Breathing", "tags": ["emotion", "reflection"], "difficulty": "Low"},
        {"name": "Quick Win", "tags": ["simplicity", "ability"], "difficulty": "Very Low"},
        {"name": "Learning Challenge", "tags": ["curiosity", "engagement"], "difficulty": "Medium"}
    ]
    
    passed = 0
    failed = 0
    
    for i, context in enumerate(test_contexts, 1):
        try:
            ctx_vec = preprocessor.normalize_context(context)
            chosen = coordinator.select_strategy(context, mock_strategies)
            
            print(f"\n  Test {i}: Energy={context['energy']}, Stress={context['stress']}")
            print(f"  ✓ Selected: {chosen['name']}")
            
            # Verify selection makes sense
            if context['stress'] == 'high' and chosen['name'] != 'Deep Work':
                print(f"    ✓ Good: Avoided high-difficulty task during high stress")
            
            passed += 1
            
        except Exception as e:
            print(f"  ❌ Test {i} failed: {e}")
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0

def test_research_engine():
    """Test research engine functionality."""
    print("\n📚 Testing Research Engine...")
    print("="*60)
    
    try:
        engine = ResearchEngine()
        
        print(f"  ✓ Loaded {len(engine.modules)} research modules")
        print(f"  ✓ Extracted {len(engine.strategies)} strategies")
        
        # Test strategy retrieval
        curiosity_strats = engine.get_strategies_by_tag("curiosity")
        print(f"  ✓ Found {len(curiosity_strats)} curiosity strategies")
        
        low_diff = engine.get_strategies_by_difficulty("low")
        print(f"  ✓ Found {len(low_diff)} low-difficulty strategies")
        
        # Test plan generation
        plan = engine.generate_composite_plan({"stress": "high", "energy": "low"})
        print(f"  ✓ Generated plan with {len(plan['steps'])} steps")
        
        if plan.get("adaptation_note"):
            print(f"  ✓ Adaptation applied for high stress context")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Research engine test failed: {e}")
        return False

def test_database_operations():
    """Test database CRUD operations."""
    print("\n💾 Testing Database Operations...")
    print("="*60)
    
    try:
        init_db()
        db = SessionLocal()
        
        # Test user creation
        test_user = User(
            name="Test User " + str(int(time.time())),
            base_stress=0.5,
            base_energy=0.6,
            resilience=0.5
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"  ✓ Created user: {test_user.name} (ID: {test_user.id})")
        
        # Test interaction logging
        interaction = Interaction(
            user_id=test_user.id,
            context={"stress": "medium", "energy": "medium"},
            strategy_name="Test Strategy",
            strategy_data={"name": "Test", "tags": ["test"]},
            outcome="completed"
        )
        db.add(interaction)
        db.commit()
        print(f"  ✓ Logged interaction for user")
        
        # Test retrieval
        user_check = db.query(User).filter(User.id == test_user.id).first()
        assert user_check is not None
        print(f"  ✓ Retrieved user from database")
        
        # Cleanup
        db.delete(interaction)
        db.delete(test_user)
        db.commit()
        print(f"  ✓ Cleaned up test data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        if 'db' in locals():
            db.close()
        return False

def test_user_persona_simulation():
    """Test user persona simulation logic."""
    print("\n👤 Testing User Persona Simulation...")
    print("="*60)
    
    try:
        # Create test persona
        persona = UserPersona(
            name="Test Persona",
            base_stress=0.6,
            base_energy=0.5,
            resilience=0.4
        )
        
        print(f"  ✓ Created persona: {persona.name}")
        
        # Test day progression
        for day in range(5):
            persona.next_day()
            context = persona.get_context()
            print(f"  Day {day+1}: Energy={context['energy']}, Stress={context['stress']}")
        
        # Test strategy reaction
        test_strategy = {
            "name": "Easy Task",
            "tags": ["simplicity"],
            "difficulty": "Low"
        }
        
        outcome, reward = persona.react_to_strategy(test_strategy)
        print(f"  ✓ Strategy reaction: {outcome} (reward: {reward})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Persona simulation test failed: {e}")
        return False

def test_ml_ensemble_consensus():
    """Test that ML ensemble reaches reasonable consensus."""
    print("\n🎯 Testing ML Ensemble Consensus...")
    print("="*60)
    
    try:
        coordinator = OnlineCoordinator()
        
        # Extreme high stress scenario - all models should agree
        high_stress_context = {"energy": "low", "stress": "high"}
        ctx_vec = coordinator.preprocessor.normalize_context(high_stress_context)
        
        strategies = [
            {"name": "Deep Work Marathon", "tags": ["productivity"], "difficulty": "Very High"},
            {"name": "Gentle Breathing", "tags": ["emotion", "reflection"], "difficulty": "Low"}
        ]
        
        chosen = coordinator.select_strategy(high_stress_context, strategies)
        
        if chosen["name"] == "Gentle Breathing":
            print(f"  ✓ Ensemble correctly chose low-stress strategy for high-stress context")
            return True
        else:
            print(f"  ⚠️  Warning: Ensemble chose '{chosen['name']}' for high-stress context")
            return False
            
    except Exception as e:
        print(f"  ❌ Ensemble consensus test failed: {e}")
        return False

def run_accuracy_benchmark():
    """Run a comprehensive accuracy benchmark."""
    print("\n📊 Running Accuracy Benchmark...")
    print("="*60)
    
    try:
        coordinator = OnlineCoordinator()
        engine = ResearchEngine()
        
        # Create diverse scenarios
        scenarios = [
            {
                "context": {"energy": "low", "stress": "high"},
                "expected_tags": ["emotion", "reflection", "simplicity"],
                "avoid_tags": ["productivity", "challenge"]
            },
            {
                "context": {"energy": "high", "stress": "low"},
                "expected_tags": ["flow", "engagement", "challenge"],
                "avoid_tags": []
            },
            {
                "context": {"energy": "medium", "stress": "medium"},
                "expected_tags": ["ability", "scaffolding"],
                "avoid_tags": []
            }
        ]
        
        correct = 0
        total = len(scenarios)
        
        for i, scenario in enumerate(scenarios, 1):
            strategies = engine.strategies[:20]  # Sample strategies
            chosen = coordinator.select_strategy(scenario["context"], strategies)
            
            chosen_tags = [t.lower() for t in chosen.get("tags", [])]
            
            # Check if chosen strategy has expected characteristics
            has_expected = any(tag in chosen_tags for tag in scenario["expected_tags"])
            avoids_bad = not any(tag in chosen_tags for tag in scenario["avoid_tags"])
            
            if has_expected and avoids_bad:
                correct += 1
                print(f"  ✓ Scenario {i}: Correct selection")
            else:
                print(f"  ⚠️  Scenario {i}: Suboptimal selection")
        
        accuracy = (correct / total) * 100
        print(f"\n  Accuracy: {accuracy:.1f}% ({correct}/{total})")
        
        return accuracy >= 60.0  # 60% threshold
        
    except Exception as e:
        print(f"  ❌ Accuracy benchmark failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 MINDFULNESS PROTOTYPE - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all tests
    results["ML Models"] = test_ml_models()
    results["Research Engine"] = test_research_engine()
    results["Database Operations"] = test_database_operations()
    results["User Persona Simulation"] = test_user_persona_simulation()
    results["ML Ensemble Consensus"] = test_ml_ensemble_consensus()
    results["Accuracy Benchmark"] = run_accuracy_benchmark()
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! System is ready for use.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Review errors above.")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
