# Processor Documentation

The `processor` directory contains the **Research Engine**, which serves as the bridge between static psychological research and dynamic application logic.

## ⚙️ Components

### Research Engine (`research_engine.py`)
The `ResearchEngine` class is responsible for loading, indexing, and applying psychological principles.

#### 1. Dynamic Plan Generation (`generate_composite_plan`)
Constructs a "composite intervention" by chaining three distinct types of strategies (Trigger → Action → Retention) from the research database.

```python
def generate_composite_plan(self, user_context):
    # 1. Trigger (Start): Implementation Intentions (Gollwitzer)
    trigger = self.get_strategies_by_tag("trigger")[0]
    
    # 2. Action (Do): Tiny Habits (Fogg)
    action = self.get_strategies_by_tag("ability")[0]
    
    # 3. Retention (Keep): Self-Compassion (Sirois)
    reflection = self.get_strategies_by_tag("retention")[0]
    
    # ...
    return plan
```

#### 2. Heuristic Adaptation (`adapt_plan`)
Applies logic rules defined in `adaptation_rules.json` to modify the plan based on user context (e.g., Low Energy).

```python
# Pseudo-code for adaptation
if user_context["energy"] == "low":
    # Search for rule matching "User has low energy"
    # Apply modification (e.g., "Simplify action step")
```

## 📄 Adaptation Rules (`adaptation_rules.json`)
A JSON file defining "If-Then" rules for the engine.
- **Condition**: Natural language description of state.
- **Modification**: How to alter the strategy.
- **Source**: Which research principle justifies this change.
