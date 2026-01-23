from .base_model import BaseModel
import re
from typing import Dict, List, Any

class TaskAnalyzer(BaseModel):
    """
    Expert Model: Task Understanding & Semantic Analysis.
    Focus: Deep understanding of task semantics, category, urgency, and context.
    Logic: Analyzes task titles, categories, tags, and metadata to extract meaningful features.
    """
    def __init__(self):
        super().__init__("task_analyzer")
        
        # Task category patterns
        self.category_patterns = {
            "work": ["work", "project", "meeting", "deadline", "report", "presentation", "client", "email", "code", "design", "analysis", "review"],
            "personal": ["personal", "family", "friend", "hobby", "leisure", "entertainment", "reading", "gaming", "social"],
            "health": ["exercise", "workout", "gym", "run", "jog", "yoga", "meditation", "health", "fitness", "diet", "meal", "nutrition"],
            "daily": ["breakfast", "lunch", "dinner", "cook", "prep", "preparation", "grocery", "shopping", "clean", "laundry", "chore", "errand", "appointment"],
            "learning": ["learn", "study", "course", "tutorial", "practice", "reading", "research", "skill", "training", "education"]
        }
        
        # Time-of-day patterns
        self.time_patterns = {
            "morning": ["breakfast", "morning", "wake", "coffee", "meditation", "yoga", "exercise", "workout", "gym", "run", "jog", "journal"],
            "afternoon": ["lunch", "afternoon", "meeting", "call", "conference", "review"],
            "evening": ["dinner", "supper", "evening", "cook", "prep", "preparation", "relax", "wind down", "family time"],
            "night": ["sleep", "bed", "night", "late", "midnight"]
        }
        
        # Urgency indicators
        self.urgency_patterns = {
            "urgent": ["urgent", "asap", "immediately", "now", "critical", "emergency", "deadline", "due today", "overdue"],
            "important": ["important", "priority", "high priority", "must", "need", "required"],
            "flexible": ["whenever", "sometime", "optional", "nice to have", "low priority"]
        }
        
        # Difficulty indicators
        self.difficulty_patterns = {
            "very_high": ["complex", "difficult", "challenging", "hard", "intensive", "deep", "advanced"],
            "high": ["detailed", "thorough", "comprehensive", "analysis", "review", "design"],
            "medium": ["standard", "normal", "regular", "typical"],
            "low": ["quick", "simple", "easy", "basic", "light", "brief", "short"]
        }
        
    def extract_task_features(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive features from a task.
        """
        title = (task.get("title") or task.get("name") or "").lower()
        category = (task.get("category") or "").lower()
        tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in (task.get("tags") or [])]
        
        features = {
            "category": self._infer_category(title, category, tags),
            "time_preference": self._infer_time_preference(title, tags),
            "urgency": self._infer_urgency(title, tags, task.get("deadline")),
            "difficulty_level": self._infer_difficulty(title, task.get("difficulty"), tags),
            "duration_estimate": task.get("estimated_minutes", 30),
            "is_recurring": bool(task.get("recurrence_pattern") and task.get("recurrence_pattern") != "none"),
            "has_deadline": bool(task.get("deadline")),
            "priority": task.get("priority", 3),
            "energy_required": task.get("energy_required", 0.5),
            "focus_required": task.get("focus_required", 0.5),
            "semantic_tags": self._extract_semantic_tags(title, category, tags)
        }
        
        return features
    
    def _infer_category(self, title: str, category: str, tags: List[str]) -> str:
        """Infer task category from title, category, and tags."""
        # If category is explicitly set, use it
        if category and category in ["work", "personal", "health", "daily", "learning"]:
            return category
        
        # Check title and tags for category indicators
        all_text = " ".join([title] + tags)
        
        for cat, patterns in self.category_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                return cat
        
        # Default to "personal" if unclear
        return "personal"
    
    def _infer_time_preference(self, title: str, tags: List[str]) -> str:
        """Infer preferred time of day for task."""
        all_text = " ".join([title] + tags)
        
        for time_period, patterns in self.time_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                return time_period
        
        return "flexible"
    
    def _infer_urgency(self, title: str, tags: List[str], deadline) -> str:
        """Infer urgency level."""
        all_text = " ".join([title] + tags)
        
        # Check for explicit urgency indicators
        for urgency, patterns in self.urgency_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                return urgency
        
        # Check deadline proximity
        if deadline:
            from datetime import datetime
            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                except:
                    pass
            
            if isinstance(deadline, datetime):
                days_until = (deadline.date() - datetime.now().date()).days
                if days_until < 0:
                    return "urgent"
                elif days_until == 0:
                    return "urgent"
                elif days_until <= 1:
                    return "important"
                elif days_until <= 3:
                    return "important"
        
        return "flexible"
    
    def _infer_difficulty(self, title: str, difficulty: int, tags: List[str]) -> str:
        """Infer difficulty level."""
        # Use explicit difficulty if provided
        if difficulty:
            if difficulty >= 5:
                return "very_high"
            elif difficulty >= 4:
                return "high"
            elif difficulty >= 3:
                return "medium"
            else:
                return "low"
        
        # Infer from title and tags
        all_text = " ".join([title] + tags)
        
        for diff_level, patterns in self.difficulty_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                return diff_level
        
        return "medium"
    
    def _extract_semantic_tags(self, title: str, category: str, tags: List[str]) -> List[str]:
        """Extract semantic meaning from task."""
        semantic = []
        all_text = " ".join([title] + tags).lower()
        
        # Activity type
        if any(word in all_text for word in ["read", "reading", "book", "article"]):
            semantic.append("reading")
        if any(word in all_text for word in ["write", "writing", "draft", "document"]):
            semantic.append("writing")
        if any(word in all_text for word in ["code", "program", "develop", "debug"]):
            semantic.append("coding")
        if any(word in all_text for word in ["meet", "meeting", "call", "conference"]):
            semantic.append("communication")
        if any(word in all_text for word in ["cook", "prep", "meal", "dinner", "breakfast", "lunch"]):
            semantic.append("cooking")
        if any(word in all_text for word in ["clean", "organize", "tidy", "declutter"]):
            semantic.append("cleaning")
        if any(word in all_text for word in ["exercise", "workout", "gym", "run", "jog", "yoga"]):
            semantic.append("exercise")
        if any(word in all_text for word in ["meditation", "mindfulness", "reflect"]):
            semantic.append("mindfulness")
        if any(word in all_text for word in ["shop", "grocery", "buy", "purchase"]):
            semantic.append("shopping")
        if any(word in all_text for word in ["learn", "study", "practice", "tutorial"]):
            semantic.append("learning")
        
        return semantic
    
    def predict(self, context_vector, available_strategies):
        """
        Score tasks/strategies based on semantic understanding.
        """
        scores = {}
        
        # Extract context features
        try:
            if hasattr(context_vector, 'tolist'):
                ctx_list = context_vector.tolist()
            elif isinstance(context_vector, (list, tuple)):
                ctx_list = list(context_vector)
            else:
                ctx_list = [0.0, 0.0, 0.0, 0.0, 0.5, 0.5]
            
            # Ensure we have at least 6 elements [Morning, Afternoon, Evening, Night, Energy, Stress]
            while len(ctx_list) < 6:
                ctx_list.append(0.5)
            
            time_of_day = "flexible"
            if ctx_list[0] > 0.5:  # Morning
                time_of_day = "morning"
            elif ctx_list[1] > 0.5:  # Afternoon
                time_of_day = "afternoon"
            elif ctx_list[2] > 0.5:  # Evening
                time_of_day = "evening"
            elif ctx_list[3] > 0.5:  # Night
                time_of_day = "night"
            
            energy = max(0.0, min(1.0, float(ctx_list[-2]) if len(ctx_list) >= 2 else 0.5))
            stress = max(0.0, min(1.0, float(ctx_list[-1]) if len(ctx_list) > 0 else 0.5))
            
        except Exception as e:
            print(f"[TaskAnalyzer] Context error: {e}. Using defaults.")
            time_of_day = "flexible"
            energy = 0.5
            stress = 0.5
        
        # Score each strategy/task
        for strat in available_strategies:
            name = strat.get("name", "unknown")
            
            # Extract task features if this is a task
            if name.startswith("task_") or "task" in strat:
                task_data = strat if "task" in strat else {"title": name, "category": strat.get("category"), "tags": strat.get("tags", [])}
                features = self.extract_task_features(task_data)
            else:
                # For non-task strategies, use basic features
                features = {
                    "category": strat.get("category", "general"),
                    "time_preference": "flexible",
                    "urgency": "flexible",
                    "difficulty_level": "medium",
                    "priority": strat.get("priority", 3)
                }
            
            score = 0.3  # Lower base score - time matching is critical
            
            # Time-of-day matching (VERY strong boost/penalty)
            if features.get("time_preference") == time_of_day:
                score += 0.5  # HUGE boost for correct time
            elif features.get("time_preference") == "flexible":
                score += 0.2  # Flexible tasks can go anywhere, slight boost
            else:
                score -= 0.4  # STRONG penalty for wrong time
            
            # Category-energy matching (secondary to time matching)
            if features.get("category") == "work" and energy > 0.6:
                score += 0.1
            elif features.get("category") == "health" and energy > 0.5:
                score += 0.08
            elif features.get("category") == "daily" and energy < 0.4:
                score += 0.08  # Daily tasks when low energy
            
            # Urgency boost (important but time matching is more critical)
            if features.get("urgency") == "urgent":
                score += 0.2
            elif features.get("urgency") == "important":
                score += 0.12
            
            # Priority boost (moderate)
            priority = features.get("priority", 3)
            score += (priority / 5.0) * 0.15
            
            # Stress-aware scheduling (secondary consideration)
            if stress > 0.6:
                # High stress: prefer low-difficulty, non-work tasks
                if features.get("difficulty_level") in ["low", "medium"]:
                    score += 0.08
                if features.get("category") != "work":
                    score += 0.08
            else:
                # Low stress: can handle more challenging tasks
                if features.get("difficulty_level") == "high" and energy > 0.6:
                    score += 0.08
            
            scores[name] = max(0.0, min(1.0, score))
        
        return scores
    
    def update(self, context_vector, strategy_vector, reward):
        """Learn from task completion outcomes."""
        pass
