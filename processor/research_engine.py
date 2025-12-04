import json
import os
from typing import List, Dict, Any, Optional

class ResearchEngine:
    def __init__(self, research_dir: str = "../research"):
        """
        Initialize the ResearchEngine.
        
        Args:
            research_dir (str): Path to the directory containing research JSON modules.
        """
        # Resolve absolute path relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.research_dir = os.path.join(script_dir, research_dir)
        self.modules: List[Dict[str, Any]] = []
        self.strategies: List[Dict[str, Any]] = []
        self._load_modules()

    def _load_modules(self):
        """
        Scans the research directory and loads all valid JSON files.
        """
        if not os.path.exists(self.research_dir):
            print(f"Warning: Research directory '{self.research_dir}' not found.")
            return

        print(f"Loading research from: {self.research_dir}")
        for filename in os.listdir(self.research_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.research_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        module = json.load(f)
                        self.modules.append(module)
                        # Flatten strategies for easier access
                        if "actionable_strategies" in module:
                            for strategy in module["actionable_strategies"]:
                                # Add source metadata to the strategy itself
                                strategy["source_id"] = module.get("id")
                                strategy["source_title"] = module.get("title")
                                self.strategies.append(strategy)
                        print(f"  [+] Loaded: {module.get('title', 'Unknown Title')}")
                except json.JSONDecodeError:
                    print(f"  [!] Error decoding JSON: {filename}")
                except Exception as e:
                    print(f"  [!] Error loading {filename}: {e}")
        
        print(f"Total modules loaded: {len(self.modules)}")
        print(f"Total strategies extracted: {len(self.strategies)}")

    def get_strategies_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Returns a list of strategies that match a specific tag (e.g., 'initiation', 'curiosity').
        """
        return [s for s in self.strategies if tag.lower() in [t.lower() for t in s.get("tags", [])]]

    def get_strategies_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        Returns a list of strategies matching a specific difficulty level (e.g., 'Low', 'Medium').
        """
        return [s for s in self.strategies if s.get("difficulty", "").lower() == difficulty.lower()]

    def generate_composite_plan(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates a 'scheme' or plan by combining bits and pieces from different research papers.
        
        Args:
            user_context (Dict): Placeholder for future user data (e.g., current state, goals).
        
        Returns:
            Dict: A structured plan containing a Trigger, Action, and Retention strategy.
        """
        # NOTE: In a real scenario, this would use logic or LLM to select the *best* combo based on context.
        # For now, we will construct a "Standard Intervention" using our known best-practices.
        
        # 1. Find a Trigger strategy (Gollwitzer)
        triggers = self.get_strategies_by_tag("trigger")
        selected_trigger = triggers[0] if triggers else None

        # 2. Find an Action strategy (Fogg - Ability/Simplicity)
        actions = self.get_strategies_by_tag("ability")
        selected_action = actions[0] if actions else None

        # 3. Find a Retention/Reflection strategy (Sirois - Self-Compassion)
        reflections = self.get_strategies_by_tag("retention")
        selected_reflection = reflections[0] if reflections else None

        plan = {
            "name": "Composite Intervention Plan",
            "rationale": "Combines Implementation Intentions for starting, Tiny Habits for ability, and Self-Compassion for retention.",
            "steps": []
        }

        if selected_trigger:
            plan["steps"].append({
                "phase": "Trigger",
                "strategy": selected_trigger["name"],
                "logic": selected_trigger["logic"],
                "source": selected_trigger["source_title"]
            })
        
        if selected_action:
            plan["steps"].append({
                "phase": "Action",
                "strategy": selected_action["name"],
                "logic": selected_action["logic"],
                "source": selected_action["source_title"]
            })

        if selected_reflection:
            plan["steps"].append({
                "phase": "Retention",
                "strategy": selected_reflection["name"],
                "logic": selected_reflection["logic"],
                "source": selected_reflection["source_title"]
            })

        return plan

if __name__ == "__main__":
    # Test the engine
    engine = ResearchEngine()
    
    print("\n--- Testing Strategy Retrieval ---")
    curiosity_strats = engine.get_strategies_by_tag("curiosity")
    print(f"Found {len(curiosity_strats)} curiosity strategies:")
    for s in curiosity_strats:
        print(f" - {s['name']} (from {s['source_id']})")

    print("\n--- Generating Composite Plan ---")
    # Simulating a request for a plan
    plan = engine.generate_composite_plan()
    print(json.dumps(plan, indent=2))
