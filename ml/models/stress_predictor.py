from .base_model import BaseModel

class StressPredictor(BaseModel):
    """
    Expert Model: Stress & Burnout Prevention (Sirois 2014 / Bandura 1977).
    Focus: Detects stress patterns and prioritizes self-compassion strategies.
    Logic: If user stress is high, veto productivity pushes and recommend regulation.
    Enhanced: Now tracks stress trends and adapts intervention intensity.
    """
    def __init__(self):
        super().__init__("stress_predictor")
        # Track stress history for trend analysis
        if "stress_history" not in self.weights:
            self.weights["stress_history"] = []
        if "strategy_effectiveness" not in self.weights:
            self.weights["strategy_effectiveness"] = {}
        
    def predict(self, context_vector, available_strategies):
        # context_vector: [Morning, Afternoon, Evening, Night, Energy, Stress]
        stress_level = context_vector[-1] if len(context_vector) > 0 else 0.5
        energy_level = context_vector[-2] if len(context_vector) > 1 else 0.5
        
        # Track stress history
        stress_history = self.weights.get("stress_history", [])
        stress_history.append(stress_level)
        if len(stress_history) > 10:
            stress_history = stress_history[-10:]
        self.weights["stress_history"] = stress_history
        
        # Detect stress trend
        trend = "stable"
        if len(stress_history) >= 3:
            recent_avg = sum(stress_history[-3:]) / 3
            older_avg = sum(stress_history[-6:-3]) / 3 if len(stress_history) >= 6 else recent_avg
            if recent_avg > older_avg + 0.15:
                trend = "increasing"
            elif recent_avg < older_avg - 0.15:
                trend = "decreasing"
        
        scores = {}
        strategy_effectiveness = self.weights.get("strategy_effectiveness", {})
        
        for strat in available_strategies:
            name = strat["name"]
            tags = [t.lower() for t in strat.get("tags", [])]
            difficulty = strat.get("difficulty", "Medium").lower()
            
            score = 0.2  # Base score
            
            # CRITICAL STRESS (>0.8) - Emergency intervention
            if stress_level > 0.8:
                if any(t in tags for t in ["retention", "emotion", "reflection", "self-compassion"]):
                    score = 0.95  # Critical priority
                else:
                    score = 0.05  # Veto almost everything else
            
            # HIGH STRESS (0.6-0.8) - Strong regulation focus
            elif stress_level > 0.6:
                if any(t in tags for t in ["retention", "emotion", "reflection", "self-compassion"]):
                    score = 0.8
                elif "productivity" in tags or "challenge" in tags:
                    score = 0.1  # Penalize demanding tasks
                elif difficulty in ["low", "very low"]:
                    score = 0.4  # Gentle tasks are okay
                else:
                    score = 0.2
            
            # MEDIUM STRESS (0.3-0.6) - Supportive scaffolding
            elif stress_level > 0.3:
                if "scaffolding" in tags or "support" in tags:
                    score = 0.6
                if difficulty == "low":
                    score += 0.2  # Easy wins build confidence
            
            # LOW STRESS but INCREASING TREND - Preventive care
            elif trend == "increasing":
                if any(t in tags for t in ["reflection", "mindfulness", "self-awareness"]):
                    score = 0.5  # Prevent burnout before it starts
            
            # Compound effect: Low energy + stress = extra careful
            if energy_level < 0.3 and stress_level > 0.4:
                if difficulty in ["high", "very high"]:
                    score *= 0.5  # Strongly penalize hard tasks
            
            # Learn from history - boost strategies that worked before
            effectiveness = strategy_effectiveness.get(name, 0.5)
            score += (effectiveness - 0.5) * 0.3
            
            scores[name] = max(0.0, min(1.0, score))
        
        return scores

    def update(self, context_vector, strategy_vector, reward):
        """Learn which strategies effectively reduce stress."""
        # In production, correlate strategy outcomes with subsequent stress levels
        pass
        
    def update_effectiveness(self, strategy_name, reduced_stress):
        """Track which strategies help reduce stress."""
        effectiveness = self.weights.get("strategy_effectiveness", {})
        current = effectiveness.get(strategy_name, 0.5)
        
        # Update effectiveness score
        if reduced_stress:
            effectiveness[strategy_name] = min(1.0, current + 0.1)
        else:
            effectiveness[strategy_name] = max(0.0, current - 0.05)
        
        self.weights["strategy_effectiveness"] = effectiveness
        self.save()
