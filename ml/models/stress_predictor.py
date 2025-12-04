from .base_model import BaseModel

class StressPredictor(BaseModel):
    """
    Expert Model: Stress & Self-Compassion (Sirois, 2014).
    Focus: Detects high stress/burnout and prioritizes regulation strategies.
    Logic: If context.stress is high, boost 'Retention/Reflection' strategies.
    """
    def __init__(self):
        super().__init__("stress_predictor")
        
    def predict(self, context_vector, available_strategies):
        # context_vector: [Time..., Energy, Stress]
        # Stress is the last element
        stress_level = context_vector[-1] 
        
        scores = {}
        for strat in available_strategies:
            name = strat["name"]
            tags = [t.lower() for t in strat.get("tags", [])]
            
            score = 0.0
            
            # If stress is high (> 0.7), MASSIVELY boost 'retention', 'emotion', 'reflection'
            if stress_level > 0.7:
                if any(t in tags for t in ["retention", "emotion", "reflection", "self-compassion"]):
                    score = 0.9
                else:
                    score = 0.1 # Penalize high-effort tasks
            
            # If stress is low, this model stays quiet (neutral score)
            else:
                score = 0.3
                
            scores[name] = score
        return scores

    def update(self, context_vector, strategy_vector, reward):
        # This model is rule-based mostly, but could learn which regulation strategies work best
        pass
