import json
import os
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime

class DataPreprocessor:
    """
    Responsible for cleaning, normalizing, and encoding data for the ML models.
    Converts raw JSON logs and strategies into efficient feature vectors.
    """
    
    def __init__(self):
        # Mappings for categorical data (One-Hot Encoding)
        self.context_tags = ["morning", "afternoon", "evening", "night", "tired", "energetic", "stressed", "bored"]
        self.strategy_tags = ["trigger", "ability", "motivation", "curiosity", "flow", "scaffolding", "retention"]
        
    def normalize_context(self, raw_context: Dict[str, Any]) -> np.ndarray:
        """
        Converts a user context dict (e.g., {'time': 'morning', 'energy': 'low'}) 
        into a normalized feature vector.
        Handles both string and numeric inputs for robustness.
        """
        # 1. Time Encoding (Simple 4-bin)
        time_vec = [0] * 4
        
        # Handle time_of_day if provided, otherwise use current time
        if "time_of_day" in raw_context:
            hour = int(raw_context["time_of_day"])
        else:
            hour = datetime.now().hour
            
        if 5 <= hour < 12: time_vec[0] = 1 # Morning
        elif 12 <= hour < 17: time_vec[1] = 1 # Afternoon
        elif 17 <= hour < 22: time_vec[2] = 1 # Evening
        else: time_vec[3] = 1 # Night
        
        # 2. State Encoding (Energy/Stress)
        # Handle both string and numeric inputs
        energy_input = raw_context.get("energy", 0.5)
        stress_input = raw_context.get("stress", 0.5)
        
        # Map string values to numeric
        energy_map = {"low": 0.0, "medium": 0.5, "high": 1.0}
        stress_map = {"low": 0.0, "medium": 0.5, "high": 1.0}
        
        if isinstance(energy_input, str):
            energy_val = energy_map.get(energy_input.lower(), 0.5)
        else:
            # Already numeric, just clamp to [0, 1]
            energy_val = max(0.0, min(1.0, float(energy_input)))
        
        if isinstance(stress_input, str):
            stress_val = stress_map.get(stress_input.lower(), 0.5)
        else:
            # Already numeric, just clamp to [0, 1]
            stress_val = max(0.0, min(1.0, float(stress_input)))
        
        # Combine
        # Vector: [Morning, Afternoon, Evening, Night, Energy, Stress]
        feature_vector = np.array(time_vec + [energy_val, stress_val])
        return feature_vector

    def encode_strategy(self, strategy: Dict[str, Any]) -> np.ndarray:
        """
        Converts a strategy dict into a feature vector based on its tags and difficulty.
        """
        # 1. Tag Encoding (Multi-hot)
        tag_vec = [0] * len(self.strategy_tags)
        s_tags = [t.lower() for t in strategy.get("tags", [])]
        
        for i, tag in enumerate(self.strategy_tags):
            # Check for partial matches (e.g., "trigger" matches "initiation/trigger")
            if any(tag in t for t in s_tags):
                tag_vec[i] = 1
                
        # 2. Difficulty Encoding
        diff_map = {"very low": 0.1, "low": 0.3, "medium": 0.5, "high": 0.8, "very high": 1.0}
        diff_val = diff_map.get(strategy.get("difficulty", "medium").lower(), 0.5)
        
        # Combine
        feature_vector = np.array(tag_vec + [diff_val])
        return feature_vector

    def process_interaction_log(self, log_entry: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Processes a single interaction log for training.
        Returns: (Context_Vector, Strategy_Vector, Reward)
        """
        context_vec = self.normalize_context(log_entry.get("context", {}))
        strategy_vec = self.encode_strategy(log_entry.get("strategy", {}))
        
        # Reward shaping
        # Did they finish? (1.0) Did they start but quit? (0.2) Did they ignore? (-0.5)
        outcome = log_entry.get("outcome", "ignored")
        reward = 0.0
        if outcome == "completed": reward = 1.0
        elif outcome == "started": reward = 0.2
        elif outcome == "ignored": reward = -0.1
        
        return context_vec, strategy_vec, reward

if __name__ == "__main__":
    # Test the preprocessor
    processor = DataPreprocessor()
    
    print("--- Testing Context Normalization ---")
    ctx = {"energy": "low", "stress": "high"}
    print(f"Context: {ctx}")
    print(f"Vector: {processor.normalize_context(ctx)}")
    
    print("\n--- Testing Strategy Encoding ---")
    strat = {"name": "Test", "tags": ["trigger", "automation"], "difficulty": "Low"}
    print(f"Strategy: {strat}")
    print(f"Vector: {processor.encode_strategy(strat)}")
