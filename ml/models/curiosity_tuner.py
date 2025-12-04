from .base_model import BaseModel
import random

class CuriosityTuner(BaseModel):
    """
    Expert Model: Curiosity & Information Gap (Loewenstein, 1994).
    Focus: Optimizes engagement through novelty.
    Logic: If user is bored (low energy/engagement), boost 'Curiosity' strategies.
    Also implements 'Thompson Sampling' for exploration (trying new things).
    """
    def __init__(self):
        super().__init__("curiosity_tuner")
        # Weights: {strategy_name: {alpha: 1, beta: 1}} (Beta distribution params)
        
    def predict(self, context_vector, available_strategies):
        scores = {}
        for strat in available_strategies:
            name = strat["name"]
            
            # Thompson Sampling: Sample from Beta(alpha, beta)
            # This naturally balances exploration (low confidence) and exploitation (high success)
            params = self.weights.get(name, {"alpha": 1, "beta": 1})
            sample_score = random.betavariate(params["alpha"], params["beta"])
            
            # Boost if tags include 'curiosity' or 'novelty'
            tags = [t.lower() for t in strat.get("tags", [])]
            if "curiosity" in tags or "novelty" in tags:
                sample_score += 0.2
                
            scores[name] = sample_score
        return scores

    def update(self, context_vector, strategy_vector, reward):
        # We need the strategy name. Assuming it's passed or looked up.
        # For prototype, we'll add a helper method.
        pass

    def update_outcome(self, strategy_name, success):
        params = self.weights.get(strategy_name, {"alpha": 1, "beta": 1})
        if success:
            params["alpha"] += 1
        else:
            params["beta"] += 1
        self.weights[strategy_name] = params
        self.save()
