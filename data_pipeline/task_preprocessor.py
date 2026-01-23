"""
Enhanced task preprocessor for ML models.
Extracts rich features from tasks for better ML understanding.
"""
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

class TaskPreprocessor:
    """
    Preprocesses tasks into rich feature vectors for ML models.
    Extracts semantic, temporal, and contextual features.
    """
    
    def __init__(self):
        # Category encodings
        self.categories = ["work", "personal", "health", "daily", "learning", "other"]
        
        # Time-of-day encodings
        self.time_periods = ["morning", "afternoon", "evening", "night", "flexible"]
        
        # Urgency encodings
        self.urgency_levels = ["urgent", "important", "flexible"]
        
        # Difficulty encodings
        self.difficulty_levels = ["very_low", "low", "medium", "high", "very_high"]
        
    def extract_task_features(self, task: Dict[str, Any], current_time: datetime = None) -> np.ndarray:
        """
        Extract comprehensive feature vector from a task.
        Returns a rich feature vector for ML models.
        """
        if current_time is None:
            current_time = datetime.now()
        
        title = (task.get("title") or task.get("name") or "").lower()
        category = (task.get("category") or "other").lower()
        tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task.get("tags") or [])]
        
        # 1. Category encoding (one-hot)
        category_vec = [0.0] * len(self.categories)
        if category in self.categories:
            category_idx = self.categories.index(category)
            category_vec[category_idx] = 1.0
        else:
            category_vec[-1] = 1.0  # "other"
        
        # 2. Time preference encoding (one-hot)
        time_pref = self._infer_time_preference(title, tags)
        time_vec = [0.0] * len(self.time_periods)
        if time_pref in self.time_periods:
            time_idx = self.time_periods.index(time_pref)
            time_vec[time_idx] = 1.0
        else:
            time_vec[-1] = 1.0  # "flexible"
        
        # 3. Urgency encoding (one-hot)
        urgency = self._infer_urgency(title, tags, task.get("deadline"), current_time)
        urgency_vec = [0.0] * len(self.urgency_levels)
        if urgency in self.urgency_levels:
            urgency_idx = self.urgency_levels.index(urgency)
            urgency_vec[urgency_idx] = 1.0
        else:
            urgency_vec[-1] = 1.0  # "flexible"
        
        # 4. Difficulty encoding (one-hot)
        difficulty = task.get("difficulty", 3)
        difficulty_level = self._map_difficulty(difficulty)
        difficulty_vec = [0.0] * len(self.difficulty_levels)
        if difficulty_level in self.difficulty_levels:
            diff_idx = self.difficulty_levels.index(difficulty_level)
            difficulty_vec[diff_idx] = 1.0
        else:
            difficulty_vec[2] = 1.0  # "medium"
        
        # 5. Numeric features (normalized)
        priority = task.get("priority", 3) / 5.0  # Normalize to [0, 1]
        energy_required = task.get("energy_required", 0.5)  # Already [0, 1]
        focus_required = task.get("focus_required", 0.5)  # Already [0, 1]
        
        # Duration (normalized, assuming max 480 minutes = 8 hours)
        estimated_minutes = task.get("estimated_minutes", 30)
        duration_normalized = min(1.0, estimated_minutes / 480.0)
        
        # Deadline proximity (days until deadline, normalized)
        deadline_proximity = 1.0  # Default: no deadline
        if task.get("deadline"):
            try:
                deadline = task["deadline"]
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                
                if isinstance(deadline, datetime):
                    days_until = (deadline.date() - current_time.date()).days
                    if days_until < 0:
                        deadline_proximity = 0.0  # Overdue
                    elif days_until == 0:
                        deadline_proximity = 0.1  # Due today
                    elif days_until <= 1:
                        deadline_proximity = 0.2  # Due tomorrow
                    elif days_until <= 3:
                        deadline_proximity = 0.4  # Due soon
                    elif days_until <= 7:
                        deadline_proximity = 0.6  # Due this week
                    else:
                        deadline_proximity = 0.8  # Due later
            except:
                pass
        
        # Recurring task indicator
        is_recurring = 1.0 if (task.get("recurrence_pattern") and task.get("recurrence_pattern") != "none") else 0.0
        
        # Semantic tags (multi-hot encoding for common patterns)
        semantic_tags = self._extract_semantic_tags(title, category, tags)
        semantic_vec = [
            1.0 if "reading" in semantic_tags else 0.0,
            1.0 if "writing" in semantic_tags else 0.0,
            1.0 if "coding" in semantic_tags else 0.0,
            1.0 if "communication" in semantic_tags else 0.0,
            1.0 if "cooking" in semantic_tags else 0.0,
            1.0 if "cleaning" in semantic_tags else 0.0,
            1.0 if "exercise" in semantic_tags else 0.0,
            1.0 if "mindfulness" in semantic_tags else 0.0,
            1.0 if "shopping" in semantic_tags else 0.0,
            1.0 if "learning" in semantic_tags else 0.0
        ]
        
        # Combine all features
        feature_vector = np.array(
            category_vec +           # 6 features
            time_vec +               # 5 features
            urgency_vec +            # 3 features
            difficulty_vec +         # 5 features
            [priority,                # 1 feature
             energy_required,         # 1 feature
             focus_required,          # 1 feature
             duration_normalized,     # 1 feature
             deadline_proximity,     # 1 feature
             is_recurring] +          # 1 feature
            semantic_vec              # 10 features
        )  # Total: 34 features
        
        return feature_vector
    
    def _infer_time_preference(self, title: str, tags: List[str]) -> str:
        """Infer preferred time of day."""
        all_text = " ".join([title] + tags)
        
        morning_keywords = ["breakfast", "morning", "wake", "coffee", "meditation", "yoga", "exercise", "workout", "gym", "run", "jog", "journal"]
        afternoon_keywords = ["lunch", "afternoon", "meeting", "call", "conference", "review"]
        evening_keywords = ["dinner", "supper", "evening", "cook", "prep", "preparation", "relax", "wind down", "family time"]
        night_keywords = ["sleep", "bed", "night", "late", "midnight"]
        
        if any(kw in all_text for kw in morning_keywords):
            return "morning"
        elif any(kw in all_text for kw in afternoon_keywords):
            return "afternoon"
        elif any(kw in all_text for kw in evening_keywords):
            return "evening"
        elif any(kw in all_text for kw in night_keywords):
            return "night"
        
        return "flexible"
    
    def _infer_urgency(self, title: str, tags: List[str], deadline, current_time: datetime) -> str:
        """Infer urgency level."""
        all_text = " ".join([title] + tags)
        
        urgent_keywords = ["urgent", "asap", "immediately", "now", "critical", "emergency", "deadline", "due today", "overdue"]
        if any(kw in all_text for kw in urgent_keywords):
            return "urgent"
        
        if deadline:
            try:
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                
                if isinstance(deadline, datetime):
                    days_until = (deadline.date() - current_time.date()).days
                    if days_until < 0:
                        return "urgent"
                    elif days_until == 0:
                        return "urgent"
                    elif days_until <= 1:
                        return "important"
                    elif days_until <= 3:
                        return "important"
            except:
                pass
        
        return "flexible"
    
    def _map_difficulty(self, difficulty: int) -> str:
        """Map numeric difficulty to level."""
        if difficulty >= 5:
            return "very_high"
        elif difficulty >= 4:
            return "high"
        elif difficulty >= 3:
            return "medium"
        elif difficulty >= 2:
            return "low"
        else:
            return "very_low"
    
    def _extract_semantic_tags(self, title: str, category: str, tags: List[str]) -> List[str]:
        """Extract semantic meaning."""
        semantic = []
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
        
        for tag, keywords in patterns.items():
            if any(kw in all_text for kw in keywords):
                semantic.append(tag)
        
        return semantic
