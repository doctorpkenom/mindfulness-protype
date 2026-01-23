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
        """
        Predicts flow scores for strategies based on energy-difficulty matching.
        Enhanced with robust error handling and research-backed adjustments.
        """
        # Robust context vector handling
        try:
            # Handle numpy arrays, lists, or other iterables
            if hasattr(context_vector, 'tolist'):
                ctx_list = context_vector.tolist()
            elif isinstance(context_vector, (list, tuple)):
                ctx_list = list(context_vector)
            else:
                ctx_list = [0.0, 0.0, 0.0, 0.0, 0.5, 0.5]  # Default fallback
            
            # Ensure we have at least 6 elements [Morning, Afternoon, Evening, Night, Energy, Stress]
            while len(ctx_list) < 6:
                ctx_list.append(0.5)  # Default to medium
            
            # Energy is second to last (index -2)
            energy_level = float(ctx_list[-2]) if len(ctx_list) >= 2 else 0.5
            energy_level = max(0.0, min(1.0, energy_level))  # Clamp to [0, 1]
            
        except (IndexError, ValueError, TypeError) as e:
            print(f"[FlowManager] Context vector error: {e}. Using default energy=0.5")
            energy_level = 0.5
        
        scores = {}
        for strat in available_strategies:
            try:
                name = strat.get("name", "unknown")
                difficulty = strat.get("difficulty", "Medium")
                
                # Handle both string and numeric difficulty
                if isinstance(difficulty, (int, float)):
                    diff_val = max(0.0, min(1.0, float(difficulty) / 5.0))  # Scale 1-5 to 0-1
                else:
                    difficulty_lower = str(difficulty).lower()
                    # Map difficulty to 0-1 scale
                    diff_val = 0.5  # Default
                    if "very low" in difficulty_lower: diff_val = 0.1
                    elif difficulty_lower == "low": diff_val = 0.3
                    elif difficulty_lower == "medium": diff_val = 0.5
                    elif difficulty_lower == "high": diff_val = 0.8
                    elif "very high" in difficulty_lower: diff_val = 1.0
                
                # Calculate 'Flow Match': Minimize distance between Energy and Difficulty
                # If Energy is 0.8 and Difficulty is 0.8, Match is 1.0 (Perfect)
                # If Energy is 0.2 and Difficulty is 0.8, Match is low (Anxiety)
                dist = abs(energy_level - diff_val)
                match_score = 1.0 - dist
                
                # Research enhancement: Csikszentmihalyi flow theory
                # Perfect match (within 0.1) gets bonus
                if dist < 0.1:
                    match_score = min(1.0, match_score + 0.1)
                
                scores[name] = max(0.0, min(1.0, match_score))
                
            except Exception as e:
                print(f"[FlowManager] Error processing strategy {strat.get('name', 'unknown')}: {e}")
                scores[strat.get("name", "unknown")] = 0.5  # Default score on error
            
        return scores

    def update(self, context_vector, strategy_vector, reward):
        pass
