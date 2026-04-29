"""Task factory functions.

Each task pins:
  * a precise description (the prompt the agent will see)
  * `expected_output` (sets the bar for what 'done' looks like)
  * `output_pydantic` (auto-validates the hand-off)
  * `context` (explicit dependency wiring on previous tasks)
"""

from __future__ import annotations

from crewai import Task

from .models import (
    AdaptationRules,
    FinalStudyPlan,
    RankedTopicList,
    ReviewReport,
    SkillGapReport,
    StudentProfile,
    TechniqueMap,
    TimeGrid,
)


# ---------------------------------------------------------------------------
# 1. Profile interpretation
# ---------------------------------------------------------------------------

def make_interpret_task(agent, raw_input: str) -> Task:
    return Task(
        description=(
            "You are given the following raw student input:\n\n"
            f"---\n{raw_input}\n---\n\n"
            "Extract and normalize it into a StudentProfile. Specifically:\n"
            " 1. Identify the student's primary goal and any deadline.\n"
            " 2. List every subject and its topics.\n"
            " 3. Convert self-ratings to integers 0-5 (0 = no exposure, "
            "    5 = mastery).\n"
            " 4. Capture weekly_hours and the daily_window in 24h time.\n"
            " 5. Pick the closest learning_preference: practice_heavy, "
            "    theory_first, spaced_repetition, or mixed.\n"
            " 6. Record any constraints (rest days, work shifts, etc.).\n"
            "If a field is missing, infer a sensible default and note it in "
            "constraints."
        ),
        expected_output=(
            "A valid StudentProfile JSON object with no missing required fields."
        ),
        output_pydantic=StudentProfile,
        agent=agent,
    )


# ---------------------------------------------------------------------------
# 2. Diagnostic
# ---------------------------------------------------------------------------

def make_diagnostic_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Using the StudentProfile from the previous step, produce a "
            "SkillGapReport. For each (subject, topic):\n"
            " - Compare proficiency (self-rating) to a target_level appropriate "
            "   for the goal.\n"
            " - Compute gap_score = max(0, target_level - proficiency), "
            "   adjusted upward if the topic is foundational.\n"
            " - Classify risk as low/medium/high based on gap_score and "
            "   importance.\n"
            " - Add a one-sentence evidence_notes explaining the call.\n"
            "Finish with an overall_summary (max 4 sentences)."
        ),
        expected_output="A valid SkillGapReport JSON object.",
        output_pydantic=SkillGapReport,
        agent=agent,
        context=context,
    )


# ---------------------------------------------------------------------------
# 3. Prioritization
# ---------------------------------------------------------------------------

def make_prioritize_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Combine the StudentProfile and SkillGapReport to produce a "
            "RankedTopicList. Rules:\n"
            " - Higher rank for higher gap_score, higher importance for the "
            "   stated goal, and tighter deadlines.\n"
            " - Never rank a topic above its prerequisites.\n"
            " - Provide est_hours per topic, calibrated so the total respects "
            "   the student's available hours until deadline.\n"
            " - Add a one-sentence rationale per item explaining its rank."
        ),
        expected_output="A valid RankedTopicList JSON object, ordered by rank.",
        output_pydantic=RankedTopicList,
        agent=agent,
        context=context,
    )


# ---------------------------------------------------------------------------
# 4. Scheduling
# ---------------------------------------------------------------------------

def make_schedule_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Build a TimeGrid that distributes the ranked topics across "
            "concrete sessions from today until the deadline.\n"
            "Constraints:\n"
            " - Stay within daily_window and weekly_hours.\n"
            " - No single block longer than 90 minutes; insert short breaks.\n"
            " - Reserve at least one rest day per week unless the deadline "
            "   makes that impossible (note the trade-off if so).\n"
            " - Interleave revision sessions on an expanding schedule "
            "   (1d, 3d, 7d, 14d) for previously-studied topics.\n"
            " - Honour every constraint in StudentProfile.constraints."
        ),
        expected_output="A valid TimeGrid JSON object.",
        output_pydantic=TimeGrid,
        agent=agent,
        context=context,
    )


# ---------------------------------------------------------------------------
# 5. Strategy
# ---------------------------------------------------------------------------

def make_strategy_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Annotate every session in the TimeGrid with a learning method, a "
            "resources_hint, and an expected_outcome. Heuristics:\n"
            " - Weak topics (high gap): theory + worked examples first, then "
            "   guided practice.\n"
            " - Medium gap: mixed practice with active recall checkpoints.\n"
            " - Strong topics: timed practice and spaced retrieval.\n"
            " - Respect the student's learning_preference where it doesn't "
            "   contradict the gap-based heuristic.\n"
            "Output a TechniqueMap covering every session."
        ),
        expected_output="A valid TechniqueMap JSON object.",
        output_pydantic=TechniqueMap,
        agent=agent,
        context=context,
    )


# ---------------------------------------------------------------------------
# 6. Adaptation
# ---------------------------------------------------------------------------

def make_adaptation_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Design AdaptationRules so the plan can repair itself in the real "
            "world. Cover at minimum these triggers:\n"
            " - missed_session\n"
            " - low_quiz_score / failed self-check\n"
            " - ahead_of_schedule\n"
            " - unexpected_blocked_day (sickness, exam, family)\n"
            "For each trigger, specify a concrete action (e.g. 'shift forward "
            "1 day and compress weekend buffer'). End with a "
            "weekly_review_template the student can answer in <5 minutes."
        ),
        expected_output="A valid AdaptationRules JSON object.",
        output_pydantic=AdaptationRules,
        agent=agent,
        context=context,
    )


# ---------------------------------------------------------------------------
# 7. Plan composition
# ---------------------------------------------------------------------------

def make_compose_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Compose the final, student-facing study plan as Markdown. "
            "Required sections, in order:\n"
            " 1. Goal & constraints summary (1 paragraph).\n"
            " 2. Subjects & topics covered (table).\n"
            " 3. Prioritized topic list (ordered, with one-line rationale).\n"
            " 4. Daily / weekly schedule (calendar table with time slots).\n"
            " 5. Recommended techniques per topic.\n"
            " 6. Revision & reinforcement cycles (spacing schedule).\n"
            " 7. Adaptation playbook (the trigger → action table).\n"
            "Tone: encouraging, direct, no fluff. Keep it under ~1,500 words.\n"
            "Also produce a one-paragraph summary."
        ),
        expected_output="A FinalStudyPlan with both `markdown` and `summary`.",
        output_pydantic=FinalStudyPlan,
        agent=agent,
        context=context,
    )


# ---------------------------------------------------------------------------
# 8. Review
# ---------------------------------------------------------------------------

def make_review_task(agent, context: list[Task]) -> Task:
    return Task(
        description=(
            "Independently audit the FinalStudyPlan against the StudentProfile. "
            "Check:\n"
            " - Total scheduled hours <= available hours until deadline.\n"
            " - Every high-risk topic has at least 3 sessions including 1 "
            "   revision pass.\n"
            " - All prerequisites scheduled before their dependents.\n"
            " - At least one revision pass per topic.\n"
            " - All StudentProfile.constraints respected.\n"
            "If any check fails, set verdict='revise', list the issues, and "
            "produce a corrected final_plan_markdown that fixes them. "
            "Otherwise verdict='pass' and return the plan unchanged."
        ),
        expected_output="A valid ReviewReport JSON object.",
        output_pydantic=ReviewReport,
        agent=agent,
        context=context,
    )
