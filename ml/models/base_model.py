from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os

class BaseModel(ABC):
    """
    Abstract Base Class for all Expert Models in the ensemble.
    Enforces a standard interface for the Online Coordinator and Offline Controller.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.weights = {}
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.model_path = os.path.join(self.model_dir, f"{self.name}_weights.json")
        self.load()

    @abstractmethod
    def predict(self, context_vector: Any, available_strategies: List[Dict]) -> Dict[str, float]:
        """
        Given a context and list of strategies, return a dictionary of 
        {strategy_id: score} representing the model's recommendation confidence.
        """
        pass

    @abstractmethod
    def update(self, context_vector: Any, strategy_vector: Any, reward: float):
        """
        Update the model's internal state/weights based on the outcome.
        """
        pass

    def save(self):
        """Persist model weights to disk."""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        try:
            with open(self.model_path, 'w') as f:
                json.dump(self.weights, f)
            print(f"[{self.name}] Weights saved.")
        except Exception as e:
            print(f"[{self.name}] Error saving weights: {e}")

    def load(self):
        """Load model weights from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    self.weights = json.load(f)
                print(f"[{self.name}] Weights loaded.")
            except Exception as e:
                print(f"[{self.name}] Error loading weights: {e}")
                self.weights = {}
        else:
            print(f"[{self.name}] No existing weights found. Initializing fresh.")
            self.weights = {}
