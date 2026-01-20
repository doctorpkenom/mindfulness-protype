from .base_model import BaseModel
import random

class MotivationBooster(BaseModel):
    """
    Expert Model: Intrinsic Motivation (Ryan & Deci 2000 - Self-Determination Theory).
    Focus: Identifies and recommends strategies that fulfill autonomy, competence, and relatedness.
    Logic: Tracks which strategy tags correlate with high user engagement.
    """
    def __init__(self):
        super().__init__("motivation_booster")
        # Weights: {tag: motivation_score}
        # Learns which tags lead to best intrinsic motivation
        
        # Initialize with SDT-aligned tags
        if not self.weights:
            self.weights = {
                "autonomy": 0.7,
                "competence": 0.7,
                "curiosity": 0.8,
                "flow": 0.8,
                "reflection": 0.6,
                "self-compassion": 0.6
            }
            self.save()
        
    def predict(self, context_vector, available_strategies):
        scores = {}
        
        for strat in available_strategies:
            name = strat["name"]
            tags = [t.lower() for t in strat.get("tags", [])]
            
            # Base motivation score
            score = 0.3
            
            # Boost based on learned tag preferences
            for tag in tags:
                if tag in self.weights:
                    score += self.weights[tag] * 0.2
            
            # SDT-specific boosts
            if "curiosity" in tags:
                score += 0.2  # Curiosity drives intrinsic motivation
            
            if "autonomy" in tags or "choice" in tags:
                score += 0.15  # Autonomy is core to SDT
            
            if "mastery" in tags or "competence" in tags:
                score += 0.15  # Competence fulfillment
            
            # Penalize purely extrinsic motivation strategies
            if "reward" in tags or "punishment" in tags:
                score -= 0.2
            
            scores[name] = max(0.0, min(1.0, score))
        
        return scores

    def update(self, context_vector, strategy_vector, reward):
        """Update motivation weights based on user engagement."""
        # Higher reward = strategy resonated with user's intrinsic motivation
        pass
        
    def update_tag_motivation(self, tags, success):
        """Update motivation scores for tags based on outcome."""
        adjustment = 0.05 if success else -0.03
        
        for tag in tags:
            tag_lower = tag.lower()
            current = self.weights.get(tag_lower, 0.5)
            self.weights[tag_lower] = max(0.0, min(1.0, current + adjustment))
        
        self.save()
