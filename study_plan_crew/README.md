# Personalized Study Plan Generator (CrewAI)

A multi-agent pipeline that turns a student's goals, time budget, and self-assessed proficiency into an adaptive, prioritized, time-boxed study plan with built-in revision cycles.

Built with [CrewAI](https://docs.crewai.com).

## Pipeline at a glance

```
Input → 1. Profile Analyst → 2. Diagnostic → 3. Prioritizer →
4. Scheduler → 5. Strategist → 6. Adaptation → 7. Composer → 8. Reviewer → final_study_plan.md
```

See `DESIGN.md` for the full design write-up (agent specs, data contracts, sequencing, rationale).

## Project layout

```
study_plan_crew/
├── DESIGN.md                  # Full pipeline & agent design document
├── README.md                  # This file
├── requirements.txt
├── main.py                    # Entry point — runs the full crew
├── config/
│   ├── agents.yaml            # Declarative agent definitions
│   └── tasks.yaml             # Declarative task definitions
├── src/
│   ├── __init__.py
│   ├── crew.py                # StudyPlanCrew assembly
│   ├── agents.py              # Agent factory functions
│   ├── tasks.py               # Task factory functions
│   ├── models.py              # Pydantic data contracts
│   └── tools/
│       ├── __init__.py
│       └── topic_difficulty.py  # Optional helper tool
└── examples/
    ├── sample_input.json      # Example student profile
    └── sample_output.md       # Example generated plan
```

## Quickstart

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set your model key (CrewAI uses LiteLLM under the hood)
export OPENAI_API_KEY=sk-...
# or: export ANTHROPIC_API_KEY=...

# 3. Run with the bundled sample student
python main.py --input examples/sample_input.json --output my_plan.md
```

## Custom inputs

Pass any JSON file matching the `StudentProfile` schema in `src/models.py`:

```json
{
  "goal": "Pass JEE Advanced 2026",
  "deadline": "2026-05-25",
  "weekly_hours": 28,
  "daily_window": ["17:00", "22:00"],
  "learning_preference": "practice_heavy",
  "subjects": [
    {
      "name": "Physics",
      "topics": [
        {"name": "Mechanics", "self_rating": 4},
        {"name": "Electromagnetism", "self_rating": 2}
      ]
    }
  ],
  "constraints": ["No study on Sundays"]
}
```

## Eight agents, one plan

| # | Agent | One-line role |
|---|---|---|
| 1 | Profile Analyst | Normalize raw input into typed schema |
| 2 | Diagnostic Evaluator | Score each topic on strength / weakness / risk |
| 3 | Topic Prioritizer | Rank topics by importance × gap × deadline |
| 4 | Schedule Planner | Map ranked topics onto concrete time slots |
| 5 | Learning Strategist | Pick technique per session (theory / practice / spaced repetition) |
| 6 | Adaptation Designer | Define rules for missed sessions and re-planning |
| 7 | Plan Composer | Stitch everything into a clean Markdown plan |
| 8 | Plan Reviewer | Independently audit feasibility & coverage before delivery |

## Extending

- Swap the LLM by setting `model=` on each agent in `src/agents.py`.
- Add a calendar-export agent or a resource-recommender agent by inserting a new task in `src/tasks.py` and wiring its `context` to the previous outputs.
- Replace the static topic-difficulty map in `src/tools/topic_difficulty.py` with a RAG retriever over your curriculum.
