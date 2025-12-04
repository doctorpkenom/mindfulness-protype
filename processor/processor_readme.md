# Strategy Processor (`processor/`)

This directory contains the logic for accessing and manipulating the Research Data Bank. It acts as the interface between the raw JSON data and the application logic.

## Key Files

### `research_engine.py`
The core class `ResearchEngine`.
*   **Loads Modules:** Scans the `research/` directory and validates JSON files.
*   **Retrieves Strategies:** Allows querying strategies by tag (e.g., `get_strategies_by_tag("curiosity")`).
*   **Generates Plans:** Creates composite interventions (Trigger + Action + Retention).
*   **Applies Adaptation:** Uses `adaptation_rules.json` to modify plans based on user context.

### `adaptation_rules.json`
A configuration file defining "Common Sense" heuristics.
*   **Fallback Logic:** What to do when the user is stressed or overwhelmed.
*   **Heuristics:** e.g., "If Energy is Low, reduce task duration by 50%."

### `test_engine.py`
A verification script to ensure the engine is loading modules and generating plans correctly.
