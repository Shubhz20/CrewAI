"""Top-level crew assembly.

`StudyPlanCrew(raw_input).run()` returns the validated, reviewed plan.
"""

from __future__ import annotations

from crewai import Crew, Process

from .agents import (
    make_adaptation_designer,
    make_diagnostic_evaluator,
    make_learning_strategist,
    make_plan_composer,
    make_plan_reviewer,
    make_profile_analyst,
    make_schedule_planner,
    make_topic_prioritizer,
)
from .tasks import (
    make_adaptation_task,
    make_compose_task,
    make_diagnostic_task,
    make_interpret_task,
    make_prioritize_task,
    make_review_task,
    make_schedule_task,
    make_strategy_task,
)


class StudyPlanCrew:
    """Eight-agent CrewAI pipeline that turns student input into a study plan."""

    def __init__(self, raw_input: str, *, verbose: bool = True) -> None:
        self.raw_input = raw_input
        self.verbose = verbose

        # ---- Agents -----------------------------------------------------
        self.profile_analyst = make_profile_analyst()
        self.diagnostic = make_diagnostic_evaluator()
        self.prioritizer = make_topic_prioritizer()
        self.scheduler = make_schedule_planner()
        self.strategist = make_learning_strategist()
        self.adapter = make_adaptation_designer()
        self.composer = make_plan_composer()
        self.reviewer = make_plan_reviewer()

        # ---- Tasks (with explicit context wiring) -----------------------
        self.t_interpret = make_interpret_task(self.profile_analyst, raw_input)
        self.t_diagnose = make_diagnostic_task(
            self.diagnostic,
            context=[self.t_interpret],
        )
        self.t_prioritize = make_prioritize_task(
            self.prioritizer,
            context=[self.t_interpret, self.t_diagnose],
        )
        self.t_schedule = make_schedule_task(
            self.scheduler,
            context=[self.t_interpret, self.t_prioritize],
        )
        self.t_strategy = make_strategy_task(
            self.strategist,
            context=[self.t_diagnose, self.t_schedule],
        )
        self.t_adapt = make_adaptation_task(
            self.adapter,
            context=[self.t_schedule, self.t_strategy],
        )
        self.t_compose = make_compose_task(
            self.composer,
            context=[
                self.t_interpret,
                self.t_diagnose,
                self.t_prioritize,
                self.t_schedule,
                self.t_strategy,
                self.t_adapt,
            ],
        )
        self.t_review = make_review_task(
            self.reviewer,
            context=[self.t_interpret, self.t_compose],
        )

        # ---- Crew -------------------------------------------------------
        self.crew = Crew(
            agents=[
                self.profile_analyst,
                self.diagnostic,
                self.prioritizer,
                self.scheduler,
                self.strategist,
                self.adapter,
                self.composer,
                self.reviewer,
            ],
            tasks=[
                self.t_interpret,
                self.t_diagnose,
                self.t_prioritize,
                self.t_schedule,
                self.t_strategy,
                self.t_adapt,
                self.t_compose,
                self.t_review,
            ],
            process=Process.sequential,
            verbose=self.verbose,
        )

    def run(self):
        """Kick off the crew. Returns the final CrewAI output object."""
        return self.crew.kickoff()
