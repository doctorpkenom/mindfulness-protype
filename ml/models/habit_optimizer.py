from .base_model import BaseModel
import random

class HabitOptimizer(BaseModel):
    """
    Expert Model: Habit Formation (Lally et al., 2010).
    Focus: Prioritizes consistency and repetition. 
    Logic: If a user has a streak with a strategy, keep recommending it to build automaticity.
    """
    def __init__(self):
        super().__init__("habit_optimizer")
        # Weights: {strategy_name: streak_count}
        
    def predict(self, context_vector, available_strategies):
        scores = {}
        for strat in available_strategies:
            name = strat["name"]
            # Base score
            score = 0.1
            
            # Boost if we have a streak (simulated by weights)
            streak = self.weights.get(name, 0)
            if streak > 0:
                # Logarithmic boost: big boost for starting, diminishing returns
                score += min(0.8, streak * 0.1) 
            
            scores[name] = score
        return scores

    def update(self, context_vector, strategy_vector, reward):
        # We need the strategy name to update the streak. 
        # In a real implementation, we'd pass the name or ID.
        # For this prototype, we'll assume the 'strategy_vector' contains the name or we handle it in the coordinator.
        pass 
        
    def update_streak(self, strategy_name, success):
        """Specific method for this expert to track streaks."""
        current = self.weights.get(strategy_name, 0)
        if success:
            self.weights[strategy_name] = current + 1
        else:
            # Lally: "Missing one opportunity does not materially affect the habit."
            # So we don't reset to 0, maybe just decrement slightly or stay same.
            self.weights[strategy_name] = max(0, current - 1)
        self.save()
