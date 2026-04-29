# Personalized Study Plan Generator — CrewAI Multi-Agent Design

## 1. Problem Recap

Generic study schedules ignore individual goals, proficiency, time budgets, and learning preferences. We need a system that ingests a small, structured profile from a student and emits an **adaptive, prioritized, time-boxed study plan** with revision cycles and built-in flexibility.

The solution is structured as a **CrewAI pipeline of eight specialized agents** that operate in a sequential process, each consuming the previous agent's output and contributing one well-defined transformation.

---

## 2. System Architecture at a Glance

```
                ┌──────────────────────────────────────────┐
                │       Student Input (JSON / Form)        │
                │  goal • subjects • hours/day • deadline  │
                │  proficiency self-rating • preferences   │
                └──────────────────┬───────────────────────┘
                                   │
                                   ▼
 ┌──────────────────────┐   1. Input Interpreter Agent
 │ structured_profile   │ ◄─ normalizes raw inputs → typed schema
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   2. Diagnostic Agent
 │ skill_gap_report     │ ◄─ scores topics on strength / weakness / risk
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   3. Prioritization Agent
 │ ranked_topic_list    │ ◄─ orders topics by importance × difficulty × deadline
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   4. Scheduling Agent
 │ time_grid            │ ◄─ allocates topics to days / sessions
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   5. Strategy Agent
 │ technique_map        │ ◄─ assigns pedagogy (spaced rep, practice, theory…)
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   6. Adaptation Agent
 │ adaptation_rules     │ ◄─ defines re-planning triggers & make-up logic
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   7. Plan Composer Agent
 │ final_study_plan.md  │ ◄─ merges everything into a human-readable plan
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐   8. QA / Reviewer Agent  (validation gate)
 │ validated_plan       │ ◄─ checks feasibility, balance, completeness
 └──────────────────────┘
```

CrewAI process: `Process.sequential`. Each task has explicit `context=[previous_task]` so the data contract is enforced.

---

## 3. Agent Catalog

Each agent is specified with **role, goal, backstory, inputs, outputs, tools, and an example output schema**.

### Agent 1 — Input Interpreter (`profile_analyst`)

| Field | Value |
|---|---|
| **Role** | Student Profile Analyst |
| **Goal** | Convert free-form student inputs into a clean, validated profile schema. |
| **Backstory** | A meticulous academic advisor who has interviewed thousands of students. Excellent at disambiguating vague statements like "I'm okay at calculus" into measurable proficiency levels. |
| **Inputs** | Raw student form / JSON / chat transcript. |
| **Outputs** | `StudentProfile` Pydantic object: `goal`, `deadline`, `subjects[]`, `topics_per_subject[]`, `weekly_hours`, `daily_window`, `learning_preference`, `constraints[]`. |
| **Tools** | None required (LLM reasoning only). Optional: a `unit_normalizer` tool for time conversions. |
| **Why first** | Every downstream agent assumes a typed contract. Garbage-in here corrupts the whole pipeline. |

### Agent 2 — Diagnostic Agent (`diagnostic_evaluator`)

| Field | Value |
|---|---|
| **Role** | Diagnostic Evaluator |
| **Goal** | Identify strengths, weaknesses, and knowledge gaps per topic. |
| **Backstory** | A learning scientist who builds skill-maps. Cross-references self-reported proficiency against the topic's intrinsic difficulty and the student's goal. |
| **Inputs** | `StudentProfile`. |
| **Outputs** | `SkillGapReport`: per topic → `{proficiency: 0-5, target_level: 0-5, gap_score, risk: low/med/high, evidence_notes}`. |
| **Tools** | `topic_difficulty_lookup` (static map or RAG over a curriculum file). |
| **Note** | Includes a "confidence calibration" pass — students often overrate familiar topics and underrate fundamentals. |

### Agent 3 — Prioritization Agent (`topic_prioritizer`)

| Field | Value |
|---|---|
| **Role** | Curriculum Prioritizer |
| **Goal** | Produce a ranked study order using importance × gap × deadline pressure × prerequisite ordering. |
| **Backstory** | A chess-coach-meets-curriculum-designer. Knows that some topics unlock others, and that high-yield topics deserve early time. |
| **Inputs** | `StudentProfile`, `SkillGapReport`. |
| **Outputs** | `RankedTopicList`: ordered list with each item carrying `weight`, `est_hours`, `prerequisites[]`, `rationale`. |
| **Tools** | `prerequisite_graph` (optional DAG resolver). |
| **Algorithm sketch** | `score = (gap × goal_weight × yield) / max(1, days_to_deadline)`, then topologically sort under prerequisite constraints. |

### Agent 4 — Scheduling Agent (`schedule_planner`)

| Field | Value |
|---|---|
| **Role** | Time-Grid Planner |
| **Goal** | Map ranked topics onto concrete day/time slots within the student's available window. |
| **Backstory** | A productivity coach obsessed with realistic pacing — leaves buffers, respects breaks, avoids cramming. |
| **Inputs** | `RankedTopicList`, `StudentProfile.weekly_hours`, `daily_window`, `deadline`. |
| **Outputs** | `TimeGrid`: list of `Session(date, start, end, topic, type=study/practice/revision)`. |
| **Rules** | (a) no session > 90 min without a break, (b) at least one rest day per week unless deadline forces otherwise, (c) revision sessions interleaved at expanding intervals (1d, 3d, 7d, 14d). |

### Agent 5 — Strategy Agent (`learning_strategist`)

| Field | Value |
|---|---|
| **Role** | Learning Methods Specialist |
| **Goal** | Pair each topic + session with the most effective learning technique given the student's preference. |
| **Backstory** | A pedagogy researcher fluent in active recall, spaced repetition, Feynman technique, problem sets, mind maps, and theory-first vs. practice-first approaches. |
| **Inputs** | `TimeGrid`, `StudentProfile.learning_preference`, `SkillGapReport`. |
| **Outputs** | `TechniqueMap`: each session annotated with `method`, `resources_hint`, `expected_outcome`. |
| **Heuristics** | Weak topics → theory + worked examples first. Medium → mixed practice. Strong → timed practice + spaced recall. |

### Agent 6 — Adaptation Agent (`adaptation_designer`)

| Field | Value |
|---|---|
| **Role** | Plan Adaptation Designer |
| **Goal** | Build the rules that let the plan repair itself when the student misses a session, finishes early, or struggles unexpectedly. |
| **Backstory** | A systems engineer who treats study plans as control loops, not contracts. |
| **Inputs** | `TimeGrid`, `TechniqueMap`. |
| **Outputs** | `AdaptationRules`: triggers (`missed_session`, `low_quiz_score`, `ahead_of_schedule`) → actions (`shift_forward`, `add_remediation_block`, `compress_revision`). Includes a weekly check-in template. |
| **Why this matters** | Without this layer the plan is brittle. This is what makes it *adaptive*, not just personalized. |

### Agent 7 — Plan Composer (`plan_writer`)

| Field | Value |
|---|---|
| **Role** | Study-Plan Author |
| **Goal** | Merge all artifacts into one clear, motivating, copy-pasteable document. |
| **Backstory** | A technical writer who has produced study guides for top-tier exam prep companies. |
| **Inputs** | All previous outputs. |
| **Outputs** | `final_study_plan.md` containing: goal summary, weekly calendar table, daily breakdown, technique notes, revision schedule, adaptation playbook. |
| **Tools** | None — pure synthesis. |

### Agent 8 — QA / Reviewer (`plan_reviewer`)

| Field | Value |
|---|---|
| **Role** | Plan Quality Reviewer |
| **Goal** | Independently audit the final plan for feasibility, coverage, and balance before it ships to the student. |
| **Backstory** | A skeptical senior tutor who has rejected hundreds of bad study plans. |
| **Inputs** | `final_study_plan.md`, `StudentProfile`. |
| **Outputs** | `ReviewReport` with `verdict: pass/revise`, list of issues, and (if needed) a corrected plan. |
| **Checks** | Total scheduled hours ≤ available hours; every weak topic gets ≥ N sessions; all prerequisites scheduled before dependents; deadline respected; at least one revision pass per topic. |

---

## 4. Data Contracts (Pydantic)

```python
class StudentProfile(BaseModel):
    goal: str
    deadline: date | None
    weekly_hours: float
    daily_window: tuple[time, time]
    learning_preference: Literal["practice_heavy","theory_first","spaced_repetition","mixed"]
    subjects: list[Subject]              # Subject has topics[]
    constraints: list[str] = []

class SkillGapReport(BaseModel):
    items: list[TopicDiagnosis]          # proficiency, target, gap_score, risk

class RankedTopicList(BaseModel):
    items: list[RankedTopic]             # weight, est_hours, prereqs

class TimeGrid(BaseModel):
    sessions: list[Session]

class TechniqueMap(BaseModel):
    annotated_sessions: list[AnnotatedSession]

class AdaptationRules(BaseModel):
    triggers: list[Trigger]
    weekly_review_template: str
```

Each task's `output_pydantic` is set so CrewAI auto-validates the hand-off. A bad agent output fails fast instead of silently corrupting the chain.

---

## 5. Sequencing & Collaboration

The crew runs as `Process.sequential` because each step strictly depends on the previous one. CrewAI's `context=[…]` parameter on each task wires the dependency graph explicitly:

```python
diagnostic_task.context        = [interpret_task]
prioritize_task.context        = [interpret_task, diagnostic_task]
schedule_task.context          = [prioritize_task, interpret_task]
strategy_task.context          = [schedule_task, diagnostic_task]
adaptation_task.context        = [schedule_task, strategy_task]
compose_task.context           = [interpret_task, diagnostic_task, prioritize_task,
                                  schedule_task, strategy_task, adaptation_task]
review_task.context            = [compose_task, interpret_task]
```

If the reviewer returns `verdict=revise`, the orchestrator loops back to the **Scheduling Agent** with the reviewer's feedback in the task description — a lightweight feedback edge that keeps the system simple but self-correcting.

---

## 6. Output Format

The composed plan contains the seven required sections:

1. **Goal & Constraints summary** (1 paragraph).
2. **Subjects & topics covered** (table).
3. **Prioritized topic list** (ordered, with rationale per item).
4. **Daily / weekly schedule** (calendar table with time slots).
5. **Recommended techniques** (per topic, mapped to weakness type).
6. **Revision & reinforcement cycles** (1-day, 3-day, 7-day, 14-day spacing).
7. **Adaptation playbook** (what to do if you miss, struggle, or excel).

A sample fully-rendered plan lives in `examples/sample_output.md`.

---

## 7. Why this design works

- **Separation of concerns**: each agent has one job, which keeps prompts small, debuggable, and replaceable.
- **Explicit contracts**: Pydantic schemas turn a multi-agent chain into a typed pipeline — failures are localized.
- **Adaptive by construction**: Agent 6 makes the plan a control loop, not a static schedule.
- **Independent review**: Agent 8 catches the most common multi-agent failure mode — a confident-but-wrong final synthesis — before it reaches the student.
- **Extensible**: Adding a "resource recommender" or "calendar integration" agent only requires inserting another node; the rest of the graph is unaffected.
