# Data Pipeline Documentation

The `data_pipeline` directory is responsible for transforming raw data (logs, user contexts, task descriptions) into numeric feature vectors suitable for Machine Learning models.

## 📁 Project Structure

```
data_pipeline/
├── preprocessor.py       # Handles interaction logs and strategy encoding
├── task_preprocessor.py  # Handles task feature extraction
└── data_pipeline_readme.md
```

## ⚙️ Algorithms

### 1. Context & Strategy Normalization (`preprocessor.py`)
This module prepares data for the User Simulation loop and reinforcement learning.

#### Feature Vector Construction
The `normalize_context` function converts a dictionary like `{'energy': 'low', 'time': 'morning'}` into a fixed-size numpy array.
- **Time**: 4-bin One-Hot encoding (Morning, Afternoon, Evening, Night).
- **State**: Normalized float [0.0, 1.0] for Energy and Stress.

```python
def normalize_context(self, raw_context):
    # Time Encoding
    time_vec = [0] * 4
    if 5 <= hour < 12: time_vec[0] = 1 # Morning
    
    # State Encoding
    energy_map = {"low": 0.0, "medium": 0.5, "high": 1.0}
    # ...
    return np.array(time_vec + [energy_val, stress_val])
```

### 2. Task Feature Extraction (`task_preprocessor.py`)
This is a more advanced preprocessor designed for the Schedule Optimizer. It extracts **34 features** from a single task object.

#### Semantic Tagging
The system uses regex keyword matching to infer semantic meaning from task titles if explicit tags are missing.

```python
patterns = {
    "coding": ["code", "program", "develop", "debug"],
    "cooking": ["cook", "prep", "meal", "dinner"],
    # ...
}
```

#### Vector Layout (34 Dimensions)
The final vector is a concatenation of multiple one-hot and scalar fields:

| Index Range | Feature Group | Description |
|-------------|--------------|-------------|
| 0-5 | Category | One-hot (work, personal, etc.) |
| 6-10 | Time Pref | One-hot (morning, evening, etc.) |
| 11-13 | Urgency | One-hot (urgent, important, flexible) |
| 14-18 | Difficulty | One-hot (low to very_high) |
| 19-21 | Core Metrics | Priority, Energy Req, Focus Req (Scalars) |
| 22 | Duration | Normalized (mins / 480) |
| 23 | Deadline | Proximity score (0.0 to 1.0) |
| 24 | Recurring | Binary flag |
| 25-34 | Semantic | Multi-hot (coding, exercise, etc.) |

```python
# excerpt from extract_task_features
feature_vector = np.array(
    category_vec +           # 6 features
    time_vec +               # 5 features
    urgency_vec +            # 3 features
    difficulty_vec +         # 5 features
    [priority, energy_required, ...] + 
    semantic_vec              # 10 features
)
```
