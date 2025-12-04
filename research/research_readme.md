# Research Data Bank (`research/`)

This directory contains the core psychological "DNA" of the application. Each file is a machine-readable JSON module representing a specific research paper or behavioral theory.

## File Format

Each JSON file follows a strict schema:
*   **Metadata:** `id`, `title`, `authors`, `year`, `core_concept`.
*   **Mechanisms:** A list of psychological principles explaining *why* it works.
*   **Actionable Strategies:** A list of generalized templates that the app can use.

### Example Strategy Template
```json
{
  "name": "If-Then Trigger Template",
  "logic": "IF [User_Detected_Trigger] THEN [User_Selected_Micro_Action]",
  "tags": ["initiation", "trigger", "automation"]
}
```

## Included Research Modules

1.  **Gollwitzer (1999):** Implementation Intentions (Triggers).
2.  **Fogg (2009):** Behavior Model (Ability/Simplicity).
3.  **Loewenstein (1994):** Information Gap Theory (Curiosity).
4.  **Barkley (1997):** ADHD Executive Scaffolding.
5.  **Sirois (2014):** Self-Compassion & Procrastination.
6.  **Lally (2010):** Habit Formation (Consistency).
7.  **Kang (2009):** Epistemic Curiosity (Dopamine).
8.  **Ryan & Deci (2000):** Self-Determination Theory (Autonomy).
9.  **Rubinstein (2001):** Task Switching Costs.
10. **Csikszentmihalyi (1990):** Flow State.
11. **Zeigarnik (1927):** Unfinished Tasks.
12. **Sweller (1988):** Cognitive Load Theory.
13. **Bandura (1977):** Self-Efficacy.
