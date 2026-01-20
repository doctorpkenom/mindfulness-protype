from .base_model import BaseModel
import random

class AttentionManager(BaseModel):
    """
    Expert Model: Attention Management (Rubinstein 2001 - Task Switching Cost).
    Focus: Minimizes context switching and task fragmentation.
    Logic: Penalizes complex strategies when user shows signs of cognitive fatigue.
    """
    def __init__(self):
        super().__init__("attention_manager")
        # Weights: {strategy_name: switching_penalty}
        # Higher penalty = more context switching required
        
    def predict(self, context_vector, available_strategies):
        scores = {}
        
        # Extract context info (Time, Energy, Stress from vector)
        # context_vector: [Morning, Afternoon, Evening, Night, Energy, Stress]
        energy = context_vector[4] if len(context_vector) > 4 else 0.5
        stress = context_vector[5] if len(context_vector) > 5 else 0.5
        
        for strat in available_strategies:
            name = strat["name"]
            tags = [t.lower() for t in strat.get("tags", [])]
            difficulty = strat.get("difficulty", "Medium").lower()
            
            # Base score
            score = 0.5
            
            # Cognitive load assessment
            if energy < 0.3 or stress > 0.7:
                # User is tired or stressed - penalize complex/switching tasks
                if "productivity" in tags or "automation" in tags:
                    score -= 0.3  # These require focused attention
                if difficulty in ["high", "very high"]:
                    score -= 0.2
                    
                # Reward simple, single-focus tasks
                if "simplicity" in tags or "ability" in tags:
                    score += 0.4
                if difficulty in ["low", "very low"]:
                    score += 0.2
            else:
                # User has energy - can handle complexity
                if "flow" in tags or "engagement" in tags:
                    score += 0.3  # Challenge them to enter flow state
            
            # Penalize based on historical switching penalty
            penalty = self.weights.get(name, 0)
            score -= penalty * 0.1  # Each failed switch adds to penalty
            
            scores[name] = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        
        return scores

    def update(self, context_vector, strategy_vector, reward):
        """Update switching penalties based on outcomes."""
        # In a full implementation, track which strategies lead to task switching
        pass
        
    def update_switching_penalty(self, strategy_name, switched):
        """Track when a strategy led to task switching."""
        current = self.weights.get(strategy_name, 0)
        if switched:
            self.weights[strategy_name] = min(10, current + 1)
        else:
            # Successful focus - reduce penalty
            self.weights[strategy_name] = max(0, current - 0.5)
        self.save()
