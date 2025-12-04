import sys
import os
import json
import numpy as np

# Add parent dir to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.models.habit_optimizer import HabitOptimizer
from ml.models.stress_predictor import StressPredictor
from ml.models.curiosity_tuner import CuriosityTuner
from ml.models.flow_manager import FlowManager
from data_pipeline.preprocessor import DataPreprocessor

class OnlineCoordinator:
    """
    The 'Boss'. Receives user context, queries the Council of Experts, 
    and uses a weighted voting system to select the best strategy.
    """
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        
        # The Council
        self.experts = [
            HabitOptimizer(),
            StressPredictor(),
            CuriosityTuner(),
            FlowManager()
        ]
        
        # How much we trust each expert (could be learned over time)
        self.expert_weights = {
            "habit_optimizer": 1.0,
            "stress_predictor": 1.5, # Safety first
            "curiosity_tuner": 1.0,
            "flow_manager": 1.2
        }

    def select_strategy(self, user_context, available_strategies):
        """
        Main entry point.
        1. Preprocess Context
        2. Ask each Expert for scores
        3. Aggregate scores
        4. Return best strategy
        """
        # 1. Preprocess
        ctx_vec = self.preprocessor.normalize_context(user_context)
        
        # 2. Gather Votes
        final_scores = {s["name"]: 0.0 for s in available_strategies}
        
        print("\n--- Council Deliberation ---")
        for expert in self.experts:
            votes = expert.predict(ctx_vec, available_strategies)
            weight = self.expert_weights.get(expert.name, 1.0)
            
            print(f"[{expert.name}] (Weight: {weight})")
            # Sort top 3 for debug
            top_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)[:2]
            for name, score in top_votes:
                print(f"  - Recommends '{name}': {score:.2f}")
                
            # Weighted Sum
            for name, score in votes.items():
                final_scores[name] += score * weight

        # 3. Select Winner
        best_strategy_name = max(final_scores, key=final_scores.get)
        best_strategy = next(s for s in available_strategies if s["name"] == best_strategy_name)
        
        print(f"\n>>> FINAL DECISION: {best_strategy_name} (Score: {final_scores[best_strategy_name]:.2f})")
        return best_strategy

    def log_outcome(self, strategy_name, success):
        """
        Feedback loop. Tell the experts what happened so they can learn.
        """
        print(f"\n[Feedback] User {'completed' if success else 'failed'} {strategy_name}")
        for expert in self.experts:
            if hasattr(expert, "update_streak"):
                expert.update_streak(strategy_name, success)
            if hasattr(expert, "update_outcome"):
                expert.update_outcome(strategy_name, success)

if __name__ == "__main__":
    # Integration Test
    coordinator = OnlineCoordinator()
    
    # Mock Data
    mock_context = {"energy": "low", "stress": "high"} # Should trigger StressPredictor
    
    # Load some real strategies from the research folder (mocking the loading part)
    # In real app, ResearchEngine provides this list
    mock_strategies = [
        {"name": "Visual Timer", "tags": ["scaffolding"], "difficulty": "Low"},
        {"name": "Deep Work Session", "tags": ["productivity"], "difficulty": "High"},
        {"name": "Neutral Reflection", "tags": ["retention", "emotion"], "difficulty": "Low"},
        {"name": "Curiosity Quiz", "tags": ["curiosity"], "difficulty": "Medium"}
    ]
    
    print(f"User Context: {mock_context}")
    chosen = coordinator.select_strategy(mock_context, mock_strategies)
    
    # Simulate feedback
    coordinator.log_outcome(chosen["name"], True)
