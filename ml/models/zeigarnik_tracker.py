from .base_model import BaseModel
import random

class ZeigarnikTracker(BaseModel):
    """
    Expert Model: Zeigarnik Effect (Zeigarnik 1927 - Unfinished Tasks).
    Focus: Leverages incomplete tasks to maintain engagement.
    Logic: Tracks partially completed strategies and recommends continuation.
    """
    def __init__(self):
        super().__init__("zeigarnik_tracker")
        # Weights: {strategy_name: incompletion_count}
        # Higher count = user tends to start but not finish this strategy
        
    def predict(self, context_vector, available_strategies):
        scores = {}
        
        for strat in available_strategies:
            name = strat["name"]
            tags = [t.lower() for t in strat.get("tags", [])]
            
            # Base score
            score = 0.4
            
            # Check if this strategy has incomplete history
            incompletion_count = self.weights.get(name, 0)
            
            if incompletion_count > 0:
                # Zeigarnik Effect: unfinished tasks create psychological tension
                # Recommend completing them to release tension
                score += min(0.5, incompletion_count * 0.15)
            
            # Strategies good for closure
            if "retention" in tags or "closure" in tags:
                score += 0.2
            
            # Micro-tasks are easier to complete (reduce Zeigarnik tension)
            if "simplicity" in tags or "ability" in tags:
                score += 0.15
            
            scores[name] = max(0.0, min(1.0, score))
        
        return scores

    def update(self, context_vector, strategy_vector, reward):
        """Track task completion patterns."""
        pass
        
    def update_completion(self, strategy_name, outcome):
        """Update incompletion tracking."""
        current = self.weights.get(strategy_name, 0)
        
        if outcome == "started":
            # User started but didn't complete - increment Zeigarnik tension
            self.weights[strategy_name] = current + 1
        elif outcome == "completed":
            # User completed - release tension
            self.weights[strategy_name] = max(0, current - 2)
        elif outcome == "ignored":
            # Neutral - slowly decay tension
            self.weights[strategy_name] = max(0, current - 0.5)
        
        self.save()
