import random
import numpy as np

class UserPersona:
    """
    Simulates a specific user type with dynamic internal states.
    """
    def __init__(self, name, base_stress=0.5, base_energy=0.5, resilience=0.3):
        self.name = name
        self.base_stress = base_stress
        self.base_energy = base_energy
        self.resilience = resilience # Ability to bounce back
        
        # Dynamic States
        self.current_stress = base_stress
        self.current_energy = base_energy
        self.streak = 0
        
    def next_day(self):
        """Reset/Evolve state for a new day."""
        # Random fluctuation around base
        self.current_stress = max(0.0, min(1.0, self.base_stress + random.uniform(-0.2, 0.2)))
        self.current_energy = max(0.0, min(1.0, self.base_energy + random.uniform(-0.2, 0.2)))
        
    def get_context(self):
        """Return context dict for the ML model."""
        # Map 0-1 to low/medium/high
        e_label = "medium"
        if self.current_energy < 0.3: e_label = "low"
        elif self.current_energy > 0.7: e_label = "high"
        
        s_label = "medium"
        if self.current_stress < 0.3: s_label = "low"
        elif self.current_stress > 0.7: s_label = "high"
        
        return {
            "energy": e_label,
            "stress": s_label,
            # Time would be simulated in the main loop
        }

    def react_to_strategy(self, strategy):
        """
        Simulate the user's reaction (Success/Failure) to a specific strategy.
        Returns: (Outcome String, Reward Float)
        """
        strat_diff = strategy.get("difficulty", "Medium").lower()
        strat_tags = [t.lower() for t in strategy.get("tags", [])]
        
        # Probability of success
        prob_success = 0.5 # Base chance
        
        # 1. Energy vs Difficulty Check
        if strat_diff == "high":
            if self.current_energy < 0.4: prob_success -= 0.4 # Too hard for tired user
            elif self.current_energy > 0.7: prob_success += 0.2 # Good challenge
        elif strat_diff == "low":
            if self.current_energy < 0.4: prob_success += 0.3 # Easy is good when tired
            
        # 2. Stress vs Regulation Check
        if self.current_stress > 0.7:
            if "emotion" in strat_tags or "reflection" in strat_tags:
                prob_success += 0.4 # Exactly what they need
                self.current_stress -= 0.2 # Intervention helps reduce stress!
            elif "productivity" in strat_tags:
                prob_success -= 0.5 # Don't push me when I'm stressed!
                self.current_stress += 0.1 # Made it worse
                
        # 3. Curiosity/Novelty Check
        if "curiosity" in strat_tags:
            prob_success += 0.1 # Novelty bonus
            
        # Determine Outcome
        roll = random.random()
        if roll < prob_success:
            self.streak += 1
            self.current_energy = max(0, self.current_energy - 0.1) # Work costs energy
            return "completed", 1.0
        else:
            self.streak = 0
            return "ignored", -0.1
