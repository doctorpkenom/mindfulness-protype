# Research Data Documentation

The `research` directory acts as the "Knowledge Base" for the system. It contains JSON files, each representing a distinct psychological framework or study.

## 📚 Principles Included

The system currently integrates the following frameworks:

| Principle | Researcher | Focus | File |
|-----------|------------|-------|------|
| **Flow State** | Csikszentmihalyi (1990) | Optimal Experience | `csikszentmihalyi_1990_flow.json` |
| **Self-Compassion** | Sirois (2014) | Procrastination/Stress | `sirois_2014_self_compassion.json` |
| **Tiny Habits** | Fogg (2009) | Behavior Change | `fogg_2009_behavior_model.json` |
| **Imp. Intentions** | Gollwitzer (1999) | Goal Achievement | `gollwitzer_1999_implementation_intentions.json` |
| **Habit Formation** | Lally (2010) | Consistency | `lally_2010_habit_formation.json` |
| **Self-Efficacy** | Bandura (1977) | Confidence | `bandura_1977_self_efficacy.json` |
| **SDT** | Ryan & Deci (2000) | Motivation | `ryan_deci_2000_sdt.json` |
| ... | ... | ... | ... |

## 🧬 Data Schema

Each JSON file follows a strict schema to allow the `ResearchEngine` to parse and apply it.

```json
{
  "id": "sirois_2014_self_compassion",
  "title": "Procrastination and Stress: A Self-Compassion Perspective",
  "author": "Fuschia M. Sirois",
  "year": 2014,
  "core_proposition": "Procrastination is often a failure of self-regulation caused by...",
  "actionable_strategies": [
    {
      "name": "Neutral Observation",
      "logic": "Observe the feeling of resistance without judgment.",
      "tags": ["retention", "emotion", "mindfulness", "reflection"],
      "difficulty": "Low"
    }
  ]
}
```

- **actionable_strategies**: The list of tools the AI can "prescribe" to the user.
- **tags**: Used by the `ResearchEngine` to categorize strategies (e.g., `trigger`, `ability`, `retention`).
