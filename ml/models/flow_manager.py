from .base_model import BaseModel

class FlowManager(BaseModel):
    """
    Expert Model: Flow State (Csikszentmihalyi, 1990).
    Focus: Matches task difficulty to user energy/skill.
    Logic: 
    - High Energy -> Recommend High Difficulty (Challenge)
    - Low Energy -> Recommend Low Difficulty (Relaxation/Scaffolding)
    """
    def __init__(self):
        super().__init__("flow_manager")
        
    def predict(self, context_vector, available_strategies):
        # context_vector: [Time..., Energy, Stress]
        # Energy is second to last
        energy_level = context_vector[-2]
        
        scores = {}
        for strat in available_strategies:
            name = strat["name"]
            difficulty = strat.get("difficulty", "Medium").lower()
            
            # Map difficulty to 0-1 scale
            diff_val = 0.5
            if difficulty == "very low": diff_val = 0.1
            elif difficulty == "low": diff_val = 0.3
            elif difficulty == "medium": diff_val = 0.5
            elif difficulty == "high": diff_val = 0.8
            elif difficulty == "very high": diff_val = 1.0
            
            # Calculate 'Flow Match': Minimize distance between Energy and Difficulty
            # If Energy is 0.8 and Difficulty is 0.8, Match is 1.0 (Perfect)
            # If Energy is 0.2 and Difficulty is 0.8, Match is low (Anxiety)
            dist = abs(energy_level - diff_val)
            match_score = 1.0 - dist 
            
            scores[name] = match_score
            
        return scores

    def update(self, context_vector, strategy_vector, reward):
        pass
