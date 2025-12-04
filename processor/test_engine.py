import sys
import os
import json

# Add the current directory to the path so we can import the engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research_engine import ResearchEngine

def test_research_engine():
    print("=== 1. INITIALIZING ENGINE ===")
    engine = ResearchEngine()
    
    # Check if modules were loaded
    if not engine.modules:
        print("[FAIL] No modules loaded!")
        return
    else:
        print(f"[PASS] Successfully loaded {len(engine.modules)} research modules.")
        print(f"[PASS] Extracted {len(engine.strategies)} total strategies.")

    print("\n=== 2. VERIFYING DATA ACCESS ===")
    # Let's try to find a specific strategy to prove we are reading the JSONs correctly
    target_tag = "curiosity"
    print(f"Searching for strategies with tag: '{target_tag}'...")
    results = engine.get_strategies_by_tag(target_tag)
    
    if results:
        print(f"[PASS] Found {len(results)} strategies. First match:")
        print(f"  - Name: {results[0]['name']}")
        print(f"  - Source: {results[0]['source_title']}")
        print(f"  - Logic: {results[0]['logic']}")
    else:
        print(f"[FAIL] Could not find any strategies with tag '{target_tag}'.")

    print("\n=== 3. TESTING PLAN GENERATION (NORMAL) ===")
    print("Generating a standard plan...")
    plan_normal = engine.generate_composite_plan()
    print(json.dumps(plan_normal, indent=2))

    print("\n=== 4. TESTING PLAN GENERATION (ADAPTED) ===")
    print("Generating a plan for context: {'stress': 'high', 'energy': 'low'}...")
    context = {"stress": "high", "energy": "low"}
    plan_adapted = engine.generate_composite_plan(user_context=context)
    print(json.dumps(plan_adapted, indent=2))

    # Verification Logic
    has_emergency_step = any(step.get("phase") == "Emergency Regulation" for step in plan_adapted["steps"])
    has_adaptation_note = "adaptation_note" in plan_adapted
    
    if has_emergency_step and has_adaptation_note:
        print("\n[PASS] Adaptation logic verified: Emergency step added and adaptation note present.")
    else:
        print("\n[FAIL] Adaptation logic failed. Check rules.")

if __name__ == "__main__":
    test_research_engine()
