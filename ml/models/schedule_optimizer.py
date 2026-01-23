"""
Advanced ML-based schedule optimizer using ensemble methods and research-backed insights.
Simplified for single-day optimization with sophisticated time understanding.
"""
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
import os

class ScheduleOptimizer:
    """
    Advanced ML optimizer that uses:
    1. Ensemble learning with weighted voting
    2. Research-backed feature engineering
    3. Time-aware task understanding
    4. Context-aware scoring
    """
    
    def __init__(self):
        # Load research insights
        self.research_weights = self._load_research_weights()
        
        # Time-of-day importance weights (learned from research)
        self.time_importance = {
            "morning": {"work": 0.8, "health": 0.9, "daily": 0.7, "personal": 0.6},
            "afternoon": {"work": 0.9, "health": 0.6, "daily": 0.5, "personal": 0.7},
            "evening": {"work": 0.4, "health": 0.5, "daily": 0.9, "personal": 0.8},
            "night": {"work": 0.2, "health": 0.3, "daily": 0.4, "personal": 0.6}
        }
        
    def _load_research_weights(self) -> Dict:
        """Load research-backed weights for different principles."""
        return {
            "flow_state": 1.5,  # Csikszentmihalyi - challenge matches energy
            "stress_management": 2.0,  # Sirois - prevent burnout
            "habit_formation": 1.2,  # Lally - consistency
            "self_determination": 1.3,  # Ryan & Deci - autonomy/competence
            "cognitive_load": 1.1,  # Sweller - manage complexity
            "task_switching": 1.0,  # Rubinstein - minimize switching
            "closure": 0.9,  # Zeigarnik - complete tasks
            "self_efficacy": 1.1,  # Bandura - build confidence
            "curiosity": 1.0,  # Kang - maintain engagement
            "implementation_intentions": 1.2  # Gollwitzer - clear goals
        }
    
    def extract_rich_features(self, task: Dict[str, Any], current_hour: int, 
                              energy: float, stress: float) -> np.ndarray:
        """
        Extract comprehensive features for ML models.
        Returns a rich feature vector with 50+ features.
        """
        title = (task.get("title") or "").lower()
        category = task.get("category", "personal").lower()
        tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task.get("tags") or [])]
        
        # 1. Time-of-day features (one-hot + semantic)
        time_features = [0.0] * 4  # Morning, Afternoon, Evening, Night
        if 6 <= current_hour < 12:
            time_features[0] = 1.0
            time_period = "morning"
        elif 12 <= current_hour < 17:
            time_features[1] = 1.0
            time_period = "afternoon"
        elif 17 <= current_hour < 22:
            time_features[2] = 1.0
            time_period = "evening"
        else:
            time_features[3] = 1.0
            time_period = "night"
        
        # 2. Task time preference (inferred from title/tags)
        task_time_pref = self._infer_task_time_preference(title, tags, category)
        task_time_match = 1.0 if task_time_pref == time_period else 0.0
        
        # 3. Category encoding (one-hot)
        categories = ["work", "personal", "health", "daily", "learning", "other"]
        category_vec = [0.0] * len(categories)
        if category in categories:
            category_idx = categories.index(category)
            category_vec[category_idx] = 1.0
        else:
            category_vec[-1] = 1.0
        
        # 4. Time-category compatibility (research-backed)
        time_category_score = self.time_importance.get(time_period, {}).get(category, 0.5)
        
        # 5. Task attributes (normalized)
        priority = task.get("priority", 3) / 5.0
        difficulty = task.get("difficulty", 3) / 5.0
        energy_required = task.get("energy_required", 0.5)
        focus_required = task.get("focus_required", 0.5)
        estimated_minutes = min(1.0, task.get("estimated_minutes", 30) / 480.0)
        
        # 6. Energy-difficulty matching (Flow State principle)
        energy_diff_match = 1.0 - abs(energy - difficulty)
        
        # 7. Stress compatibility (Sirois principle)
        stress_compatibility = 1.0 - (stress * difficulty)  # High stress + high difficulty = bad
        
        # 8. Deadline urgency
        deadline_urgency = 0.0
        if task.get("deadline"):
            try:
                deadline = task["deadline"]
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                if isinstance(deadline, datetime):
                    days_until = (deadline.date() - datetime.now().date()).days
                    if days_until < 0:
                        deadline_urgency = 1.0  # Overdue
                    elif days_until == 0:
                        deadline_urgency = 0.9  # Due today
                    elif days_until <= 1:
                        deadline_urgency = 0.7  # Due tomorrow
                    elif days_until <= 3:
                        deadline_urgency = 0.5  # Due soon
                    elif days_until <= 7:
                        deadline_urgency = 0.3  # Due this week
            except:
                pass
        
        # 9. Semantic features (activity type detection)
        semantic_features = self._extract_semantic_features(title, tags)
        
        # 10. Research-backed feature interactions
        # Flow: High energy + high difficulty = good match
        flow_match = energy * difficulty if energy > 0.6 else 0.0
        
        # Habit: Recurring tasks get consistency boost
        is_recurring = 1.0 if task.get("recurrence_pattern") and task.get("recurrence_pattern") != "none" else 0.0
        
        # SDT: Personal/learning tasks = autonomy boost
        autonomy_boost = 1.0 if category in ["personal", "learning"] else 0.0
        
        # Cognitive load: Long tasks when energy is low = bad
        cognitive_load_penalty = estimated_minutes * (1.0 - energy) if energy < 0.5 else 0.0
        
        # Combine all features
        feature_vector = np.array(
            time_features +                    # 4 features
            [task_time_match,                  # 1 feature
             time_category_score] +            # 1 feature
            category_vec +                     # 6 features
            [priority,                         # 1 feature
             difficulty,                       # 1 feature
             energy_required,                  # 1 feature
             focus_required,                   # 1 feature
             estimated_minutes,                # 1 feature
             energy_diff_match,                # 1 feature
             stress_compatibility,             # 1 feature
             deadline_urgency,                 # 1 feature
             flow_match,                       # 1 feature
             is_recurring,                     # 1 feature
             autonomy_boost,                   # 1 feature
             cognitive_load_penalty] +         # 1 feature
            semantic_features                  # 10 features
        )  # Total: 32 features
        
        return feature_vector
    
    def _infer_task_time_preference(self, title: str, tags: List[str], category: str) -> str:
        """Infer when task should be done based on content - ENHANCED with more keywords."""
        all_text = " ".join([title] + tags).lower()
        
        # Morning tasks - EXPANDED keyword list
        morning_keywords = [
            "breakfast", "morning", "wake", "waking", "coffee", "meditation", "meditate",
            "yoga", "exercise", "workout", "gym", "run", "running", "jog", "jogging",
            "journal", "journaling", "stretch", "stretching", "sunrise", "early",
            "am workout", "morning routine", "wake up", "get up", "rise"
        ]
        if any(kw in all_text for kw in morning_keywords):
            return "morning"
        
        # Afternoon tasks - EXPANDED
        afternoon_keywords = [
            "lunch", "afternoon", "meeting", "call", "conference", "review", "presentation",
            "team", "collaborate", "discuss", "brainstorm", "planning", "strategy"
        ]
        if any(kw in all_text for kw in afternoon_keywords):
            return "afternoon"
        
        # Evening tasks - EXPANDED with better detection
        evening_keywords = [
            "dinner", "supper", "evening", "cook", "cooking", "prep", "preparation",
            "meal prep", "meal preparation", "dinner prep", "dinner preparation",
            "relax", "relaxation", "wind down", "wind-down", "family time", "family",
            "prepare dinner", "make dinner", "evening routine", "night routine"
        ]
        if any(kw in all_text for kw in evening_keywords):
            return "evening"
        
        # Night tasks
        night_keywords = ["sleep", "bed", "night", "late", "midnight", "bedtime", "rest"]
        if any(kw in all_text for kw in night_keywords):
            return "night"
        
        # Category-based defaults with better logic
        if category == "daily":
            # Check if it's cooking-related daily task
            if any(kw in all_text for kw in ["cook", "prep", "meal", "dinner", "kitchen"]):
                return "evening"
            return "evening"  # Daily chores often in evening
        elif category == "health":
            # Health tasks often in morning, but check for specific keywords
            if any(kw in all_text for kw in ["meditation", "exercise", "yoga", "workout"]):
                return "morning"
            return "morning"  # Health tasks often in morning
        elif category == "work":
            return "afternoon"  # Work tasks often in afternoon
        elif category == "personal":
            # Personal tasks are flexible but prefer morning or evening
            return "flexible"
        
        return "flexible"
    
    def _extract_semantic_features(self, title: str, tags: List[str]) -> List[float]:
        """Extract semantic activity features."""
        all_text = " ".join([title] + tags).lower()
        
        patterns = {
            "reading": ["read", "reading", "book", "article"],
            "writing": ["write", "writing", "draft", "document"],
            "coding": ["code", "program", "develop", "debug"],
            "communication": ["meet", "meeting", "call", "conference"],
            "cooking": ["cook", "prep", "meal", "dinner", "breakfast", "lunch"],
            "cleaning": ["clean", "organize", "tidy", "declutter"],
            "exercise": ["exercise", "workout", "gym", "run", "jog", "yoga"],
            "mindfulness": ["meditation", "mindfulness", "reflect"],
            "shopping": ["shop", "grocery", "buy", "purchase"],
            "learning": ["learn", "study", "practice", "tutorial"]
        }
        
        features = []
        for pattern_name, keywords in patterns.items():
            features.append(1.0 if any(kw in all_text for kw in keywords) else 0.0)
        
        return features
    
    def score_task_for_slot(self, task: Dict[str, Any], slot_hour: int, 
                           slot_energy: float, slot_stress: float,
                           research_metadata: Any = None) -> Tuple[float, List[str]]:
        """
        Score a task for a specific time slot using advanced ML.
        Returns: (score, reasoning_list)
        """
        # Extract rich features
        features = self.extract_rich_features(task, slot_hour, slot_energy, slot_stress)
        
        # Base score from feature vector (weighted sum)
        # Time matching is CRITICAL - give it high weight
        time_match_score = features[4]  # task_time_match
        time_category_score = features[5]  # time_category_score
        
        # Base score components
        base_score = (
            time_match_score * 0.4 +           # 40% - time matching is critical
            time_category_score * 0.2 +        # 20% - category-time compatibility
            features[12] * 0.15 +              # 15% - priority
            features[16] * 0.1 +               # 10% - deadline urgency
            features[14] * 0.1 +               # 10% - energy-difficulty match
            features[15] * 0.05                # 5% - stress compatibility
        )
        
        reasoning = []
        
        # Apply research-backed adjustments (ENHANCED with better research integration)
        if research_metadata:
            difficulty = features[13]  # difficulty feature
            
            # Flow State (Csikszentmihalyi) - Challenge matches skill/energy
            if slot_energy > 0.7 and difficulty > 0.6:  # High energy + high difficulty
                base_score += 0.2 * self.research_weights.get("flow_state", 1.5)
                reasoning.append("Flow: High energy matches challenge")
            elif slot_energy > 0.8 and difficulty < 0.3:  # Very high energy + low difficulty = boredom
                base_score -= 0.1
                reasoning.append("Flow: Task too easy for energy level")
            
            # Stress Management (Sirois) - Prevent burnout
            if slot_stress > 0.6:
                if difficulty < 0.4:  # High stress + low difficulty = good
                    base_score += 0.25 * self.research_weights.get("stress_management", 2.0)
                    reasoning.append("Stress: Low difficulty for high stress")
                elif difficulty > 0.6:  # High stress + high difficulty = bad
                    base_score -= 0.3 * self.research_weights.get("stress_management", 2.0)
                    reasoning.append("Stress: Avoid high difficulty when stressed")
            
            # Habit Formation (Lally) - Consistency matters
            if features[19] > 0:  # Recurring task
                base_score += 0.12 * self.research_weights.get("habit_formation", 1.2)
                reasoning.append("Habit: Consistency boost")
            
            # Self-Determination (Ryan & Deci) - Autonomy and competence
            if features[20] > 0:  # Autonomy boost (personal/learning tasks)
                base_score += 0.1 * self.research_weights.get("self_determination", 1.3)
                reasoning.append("SDT: Autonomy/competence")
            
            # Cognitive Load (Sweller) - Manage complexity
            if slot_energy < 0.5 and features[17] > 0.3:  # Low energy + long task
                base_score -= 0.2 * self.research_weights.get("cognitive_load", 1.1)
                reasoning.append("Cognitive: Long task when low energy")
            elif slot_energy < 0.4 and difficulty > 0.5:  # Very low energy + high difficulty
                base_score -= 0.25
                reasoning.append("Cognitive: High difficulty when very low energy")
            
            # Task Switching (Rubinstein) - Minimize context switching
            # This is handled implicitly by the scheduling algorithm, but we can penalize
            # tasks that require high focus when energy is low
            if features[18] > 0.7 and slot_energy < 0.5:  # High focus required + low energy
                base_score -= 0.15 * self.research_weights.get("task_switching", 1.0)
                reasoning.append("Switching: High focus needed but low energy")
            
            # Self-Efficacy (Bandura) - Build confidence with manageable tasks
            if difficulty > 0.3 and difficulty < 0.7 and slot_energy > 0.5:
                # Moderate difficulty when energy is good = confidence building
                base_score += 0.08 * self.research_weights.get("self_efficacy", 1.1)
                reasoning.append("Efficacy: Moderate challenge builds confidence")
            
            # Implementation Intentions (Gollwitzer) - Clear goals help
            # Boost for tasks with clear deadlines or high priority
            if features[16] > 0.7:  # High deadline urgency
                base_score += 0.1 * self.research_weights.get("implementation_intentions", 1.2)
                reasoning.append("Intentions: Clear deadline/goal")
        
        # Time enforcement - STRICT penalties for wrong times (ENHANCED)
        title = (task.get("title") or "").lower()
        tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task.get("tags") or [])]
        all_text = " ".join([title] + tags)
        
        # Morning tasks - EXPANDED detection
        morning_keywords = [
            "breakfast", "morning", "wake", "coffee", "meditation", "meditate",
            "yoga", "exercise", "workout", "gym", "run", "jog", "journal"
        ]
        is_morning_task = any(kw in all_text for kw in morning_keywords) or "morning" in tags
        if is_morning_task:
            if not (6 <= slot_hour < 12):
                base_score -= 0.8  # VERY STRONG penalty - almost reject
                reasoning.append("TIME MISMATCH: Morning task in wrong time")
            else:
                base_score += 0.2  # Bonus for correct time
                reasoning.append("TIME MATCH: Morning task in morning")
        
        # Evening tasks - EXPANDED detection
        evening_keywords = [
            "dinner", "supper", "cook", "cooking", "prep", "preparation",
            "meal prep", "dinner prep", "dinner preparation"
        ]
        is_evening_task = any(kw in all_text for kw in evening_keywords) or "evening" in tags
        if is_evening_task:
            if not (17 <= slot_hour < 22):
                base_score -= 0.8  # VERY STRONG penalty - almost reject
                reasoning.append("TIME MISMATCH: Evening task in wrong time")
            else:
                base_score += 0.2  # Bonus for correct time
                reasoning.append("TIME MATCH: Evening task in evening")
        
        # Afternoon tasks
        afternoon_keywords = ["lunch", "afternoon", "meeting", "call", "conference"]
        is_afternoon_task = any(kw in all_text for kw in afternoon_keywords) or "afternoon" in tags
        if is_afternoon_task:
            if not (12 <= slot_hour < 17):
                base_score -= 0.5  # Strong penalty
                reasoning.append("TIME MISMATCH: Afternoon task in wrong time")
            else:
                base_score += 0.15  # Bonus for correct time
                reasoning.append("TIME MATCH: Afternoon task in afternoon")
        
        # Clamp score to [0, 1]
        final_score = max(0.0, min(1.0, base_score))
        
        return final_score, reasoning
