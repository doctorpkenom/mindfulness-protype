"""
Research Module Metadata and ML Integration Layer.
Provides enhanced categorization and feature extraction for ML models.
"""
import json
import os
from typing import List, Dict, Any, Optional

class ResearchMetadata:
    """Enhanced metadata for research modules to improve ML integration."""
    
    # Strategy effectiveness categories based on research quality
    EVIDENCE_STRENGTH = {
        "high": ["fogg_2009", "csikszentmihalyi_1990", "ryan_deci_2000", "lally_2010"],
        "medium": ["gollwitzer_1999", "loewenstein_1994", "bandura_1977", "sirois_2014"],
        "emerging": ["kang_2009", "rubinstein_2001", "sweller_1988", "zeigarnik_1927"]
    }
    
    # Context suitability mapping
    CONTEXT_SUITABILITY = {
        "high_stress": {
            "recommended": ["sirois_2014", "bandura_1977"],
            "avoid": ["csikszentmihalyi_1990", "sweller_1988"]
        },
        "low_energy": {
            "recommended": ["fogg_2009", "gollwitzer_1999"],
            "avoid": ["csikszentmihalyi_1990"]
        },
        "high_energy": {
            "recommended": ["csikszentmihalyi_1990", "ryan_deci_2000"],
            "avoid": []
        },
        "boredom": {
            "recommended": ["loewenstein_1994", "kang_2009", "ryan_deci_2000"],
            "avoid": []
        }
    }
    
    # ML feature importance for each research module
    ML_FEATURES = {
        "fogg_2009": {
            "primary_tags": ["ability", "simplicity", "prompt"],
            "ml_weight": 1.0,
            "difficulty_modifier": -0.3,  # Reduces difficulty
            "energy_threshold": 0.3  # Works best when energy < 0.3
        },
        "csikszentmihalyi_1990": {
            "primary_tags": ["flow", "engagement", "challenge"],
            "ml_weight": 1.2,
            "difficulty_modifier": 0.0,
            "energy_threshold": 0.6  # Requires energy > 0.6
        },
        "ryan_deci_2000": {
            "primary_tags": ["autonomy", "competence", "motivation"],
            "ml_weight": 1.3,
            "difficulty_modifier": 0.0,
            "stress_modifier": -0.2  # Reduces stress
        },
        "lally_2010": {
            "primary_tags": ["habit", "consistency", "repetition"],
            "ml_weight": 1.0,
            "streak_importance": 1.5,
            "consistency_threshold": 3  # Requires 3+ successful completions
        },
        "sirois_2014": {
            "primary_tags": ["self-compassion", "emotion", "reflection"],
            "ml_weight": 1.8,  # High importance for wellbeing
            "stress_threshold": 0.6,  # Activates when stress > 0.6
            "difficulty_modifier": -0.4
        },
        "loewenstein_1994": {
            "primary_tags": ["curiosity", "information-gap", "engagement"],
            "ml_weight": 1.1,
            "novelty_bonus": 0.3,
            "boredom_threshold": 0.5
        },
        "bandura_1977": {
            "primary_tags": ["self-efficacy", "scaffolding", "mastery"],
            "ml_weight": 1.2,
            "confidence_building": True,
            "failure_recovery": True
        },
        "gollwitzer_1999": {
            "primary_tags": ["trigger", "implementation", "intention"],
            "ml_weight": 1.1,
            "initiation_bonus": 0.4,
            "planning_importance": 1.3
        },
        "kang_2009": {
            "primary_tags": ["curiosity", "epistemic", "learning"],
            "ml_weight": 1.0,
            "learning_bonus": 0.2
        },
        "rubinstein_2001": {
            "primary_tags": ["attention", "task-switching", "focus"],
            "ml_weight": 1.1,
            "switching_penalty": -0.3
        },
        "sweller_1988": {
            "primary_tags": ["cognitive-load", "working-memory", "complexity"],
            "ml_weight": 1.0,
            "load_threshold": 0.7
        },
        "zeigarnik_1927": {
            "primary_tags": ["completion", "tension", "memory"],
            "ml_weight": 0.9,
            "completion_drive": 1.2
        },
        "fogg_2009_behavior": {  # Alias
            "primary_tags": ["behavior", "motivation", "ability", "prompt"],
            "ml_weight": 1.0
        }
    }
    
    @classmethod
    def get_module_ml_features(cls, module_id: str) -> Dict[str, Any]:
        """Get ML-specific features for a research module."""
        return cls.ML_FEATURES.get(module_id, {
            "primary_tags": [],
            "ml_weight": 1.0
        })
    
    @classmethod
    def get_evidence_strength(cls, module_id: str) -> str:
        """Get evidence strength rating for a module."""
        for strength, modules in cls.EVIDENCE_STRENGTH.items():
            if module_id in modules:
                return strength
        return "unknown"
    
    @classmethod
    def is_suitable_for_context(cls, module_id: str, context: Dict[str, Any]) -> bool:
        """Check if module is suitable for given context."""
        # Check stress
        if context.get("stress") == "high":
            if module_id in cls.CONTEXT_SUITABILITY["high_stress"]["avoid"]:
                return False
            if module_id in cls.CONTEXT_SUITABILITY["high_stress"]["recommended"]:
                return True
        
        # Check energy
        if context.get("energy") == "low":
            if module_id in cls.CONTEXT_SUITABILITY["low_energy"]["avoid"]:
                return False
            if module_id in cls.CONTEXT_SUITABILITY["low_energy"]["recommended"]:
                return True
        
        if context.get("energy") == "high":
            if module_id in cls.CONTEXT_SUITABILITY["high_energy"]["recommended"]:
                return True
        
        return True  # Default: suitable
    
    @classmethod
    def enhance_strategy(cls, strategy: Dict[str, Any], module_id: str) -> Dict[str, Any]:
        """Enhance strategy with ML metadata."""
        enhanced = strategy.copy()
        
        # Add ML features
        ml_features = cls.get_module_ml_features(module_id)
        enhanced["ml_weight"] = ml_features.get("ml_weight", 1.0)
        enhanced["evidence_strength"] = cls.get_evidence_strength(module_id)
        
        # Add difficulty modifiers
        if "difficulty_modifier" in ml_features:
            enhanced["difficulty_modifier"] = ml_features["difficulty_modifier"]
        
        # Add threshold information
        for key in ["energy_threshold", "stress_threshold", "boredom_threshold"]:
            if key in ml_features:
                enhanced[key] = ml_features[key]
        
        return enhanced


class ResearchIndexer:
    """
    Index and categorize research strategies for fast ML lookups.
    """
    def __init__(self, research_dir: str = "../research"):
        self.research_dir = research_dir
        self.tag_index = {}  # {tag: [strategy_ids]}
        self.difficulty_index = {}  # {difficulty: [strategy_ids]}
        self.module_index = {}  # {module_id: [strategy_ids]}
        self.strategy_lookup = {}  # {strategy_id: full_strategy}
        self._build_indices()
    
    def _build_indices(self):
        """Build all lookup indices."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        research_path = os.path.join(script_dir, self.research_dir)
        
        if not os.path.exists(research_path):
            print(f"Warning: Research directory not found: {research_path}")
            return
        
        strategy_counter = 0
        
        for filename in os.listdir(research_path):
            if not filename.endswith(".json"):
                continue
            
            filepath = os.path.join(research_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    module = json.load(f)
                
                module_id = module.get("id")
                if not module_id:
                    continue
                
                # Process each strategy
                for strategy in module.get("actionable_strategies", []):
                    strategy_id = f"{module_id}_{strategy_counter}"
                    strategy_counter += 1
                    
                    # Enhance with metadata
                    enhanced_strategy = ResearchMetadata.enhance_strategy(strategy, module_id)
                    enhanced_strategy["id"] = strategy_id
                    enhanced_strategy["source_id"] = module_id
                    enhanced_strategy["source_title"] = module.get("title")
                    
                    # Store in lookup
                    self.strategy_lookup[strategy_id] = enhanced_strategy
                    
                    # Index by tags
                    for tag in strategy.get("tags", []):
                        tag_lower = tag.lower()
                        if tag_lower not in self.tag_index:
                            self.tag_index[tag_lower] = []
                        self.tag_index[tag_lower].append(strategy_id)
                    
                    # Index by difficulty
                    difficulty = strategy.get("difficulty", "Medium").lower()
                    if difficulty not in self.difficulty_index:
                        self.difficulty_index[difficulty] = []
                    self.difficulty_index[difficulty].append(strategy_id)
                    
                    # Index by module
                    if module_id not in self.module_index:
                        self.module_index[module_id] = []
                    self.module_index[module_id].append(strategy_id)
                    
            except Exception as e:
                print(f"Error indexing {filename}: {e}")
        
        print(f"✅ Research indexed: {len(self.strategy_lookup)} strategies from {len(self.module_index)} modules")
    
    def get_strategies_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get strategies matching ANY of the given tags."""
        strategy_ids = set()
        for tag in tags:
            tag_lower = tag.lower()
            strategy_ids.update(self.tag_index.get(tag_lower, []))
        
        return [self.strategy_lookup[sid] for sid in strategy_ids]
    
    def get_strategies_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get strategies of specific difficulty."""
        strategy_ids = self.difficulty_index.get(difficulty.lower(), [])
        return [self.strategy_lookup[sid] for sid in strategy_ids]
    
    def get_optimal_strategies(self, context: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Get most suitable strategies for given context."""
        all_strategies = list(self.strategy_lookup.values())
        
        # Filter by context suitability
        suitable = [
            s for s in all_strategies
            if ResearchMetadata.is_suitable_for_context(s["source_id"], context)
        ]
        
        # Score by ML features and context match
        scored = []
        for strategy in suitable:
            score = strategy.get("ml_weight", 1.0)
            
            # Adjust for energy
            energy = context.get("energy", "medium")
            if "energy_threshold" in strategy:
                if energy == "low" and strategy["energy_threshold"] < 0.4:
                    score += 0.3
                elif energy == "high" and strategy["energy_threshold"] > 0.6:
                    score += 0.3
            
            # Adjust for stress
            stress = context.get("stress", "medium")
            if stress == "high" and strategy.get("stress_threshold", 1.0) > 0.6:
                score += 0.5
            
            scored.append((score, strategy))
        
        # Sort by score and return top N
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:limit]]
