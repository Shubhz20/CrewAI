# 🤖 CrewAI Projects

A collection of multi-agent AI pipelines built with [CrewAI](https://docs.crewai.com) — autonomous crews of specialized AI agents working together to solve complex, multi-step problems.

---

## 📁 Projects

### [`study_plan_crew/`](./study_plan_crew)

> **Personalized Study Plan Generator**

An 8-agent pipeline that transforms a student's goals, time availability, and self-assessed proficiency into a fully adaptive, time-boxed study plan with built-in revision cycles.

```
Input → Profile Analyst → Diagnostic → Prioritizer →
        Scheduler → Strategist → Adaptation → Composer → Reviewer → study_plan.md
```

**Key features:**

- Accepts a structured JSON student profile (goal, deadline, weekly hours, subjects & self-ratings)
- Generates topic-prioritized, day-wise schedules with recommended learning techniques
- Includes adaptation rules for missed sessions and auto re-planning
- Produces a clean, human-readable Markdown study plan
- Fully configurable via `config/agents.yaml` and `config/tasks.yaml`

📖 See [`study_plan_crew/README.md`](./study_plan_crew/README.md) for setup & usage.

---

## 🚀 Getting Started

Each project is self-contained with its own `requirements.txt`. To get started with any project:

```bash
# 1. Navigate to the project folder
cd study_plan_crew

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your LLM API key
export OPENAI_API_KEY=sk-...

# 4. Run the crew
python main.py --input examples/sample_input.json --output my_plan.md
```

---

## 🛠️ Tech Stack

| Tool                                                     | Purpose                                            |
| -------------------------------------------------------- | -------------------------------------------------- |
| [CrewAI](https://docs.crewai.com) `>=0.86.0`             | Multi-agent orchestration framework                |
| [Pydantic](https://docs.pydantic.dev) `>=2.7`            | Typed data contracts between agents                |
| [LiteLLM](https://docs.litellm.ai)                       | LLM provider abstraction (OpenAI, Anthropic, etc.) |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management                    |
| [PyYAML](https://pypi.org/project/PyYAML/)               | Declarative agent & task configuration             |

---

## 📄 License

MIT — feel free to fork, extend, and build your own crews.
