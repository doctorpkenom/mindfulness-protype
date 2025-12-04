# Data Pipeline (`data_pipeline/`)

This directory handles the transformation of raw application data into numerical formats suitable for the Machine Learning models.

## Key Files

### `preprocessor.py`
The `DataPreprocessor` class.

*   **Context Normalization:** Converts a user context dictionary (e.g., `{"time": "morning", "stress": "high"}`) into a normalized NumPy feature vector.
    *   *Time:* One-Hot Encoded (Morning, Afternoon, Evening, Night).
    *   *State:* Normalized Floats (0.0 to 1.0) for Energy and Stress.

*   **Strategy Encoding:** Converts a strategy dictionary into a feature vector.
    *   *Tags:* Multi-Hot Encoding based on known strategy tags.
    *   *Difficulty:* Normalized Float (0.0 to 1.0).

*   **Reward Shaping:** Converts interaction outcomes into scalar rewards.
    *   `completed` = 1.0
    *   `started` = 0.2
    *   `ignored` = -0.1
