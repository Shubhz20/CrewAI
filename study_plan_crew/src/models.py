"""Pydantic data contracts shared between agents.

Each agent's task declares one of these as `output_pydantic` so CrewAI
validates the hand-off automatically — a bad output fails fast instead of
silently corrupting the rest of the chain.
"""

from __future__ import annotations

from datetime import date, time
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Student input — produced by Agent 1 (Profile Analyst)
# ---------------------------------------------------------------------------

LearningPreference = Literal[
    "practice_heavy",
    "theory_first",
    "spaced_repetition",
    "mixed",
]


class TopicInput(BaseModel):
    name: str
    self_rating: int = Field(ge=0, le=5, description="Self-assessed proficiency 0-5")
    notes: Optional[str] = None


class Subject(BaseModel):
    name: str
    topics: list[TopicInput]


class StudentProfile(BaseModel):
    goal: str
    deadline: Optional[date] = None
    weekly_hours: float = Field(gt=0)
    daily_window: tuple[time, time]
    learning_preference: LearningPreference = "mixed"
    subjects: list[Subject]
    constraints: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 2. Diagnostic — Agent 2
# ---------------------------------------------------------------------------

Risk = Literal["low", "medium", "high"]


class TopicDiagnosis(BaseModel):
    subject: str
    topic: str
    proficiency: int = Field(ge=0, le=5)
    target_level: int = Field(ge=0, le=5)
    gap_score: float = Field(ge=0, le=5)
    risk: Risk
    evidence_notes: str


class SkillGapReport(BaseModel):
    items: list[TopicDiagnosis]
    overall_summary: str


# ---------------------------------------------------------------------------
# 3. Prioritization — Agent 3
# ---------------------------------------------------------------------------


class RankedTopic(BaseModel):
    subject: str
    topic: str
    rank: int
    weight: float
    est_hours: float
    prerequisites: list[str] = Field(default_factory=list)
    rationale: str


class RankedTopicList(BaseModel):
    items: list[RankedTopic]


# ---------------------------------------------------------------------------
# 4. Scheduling — Agent 4
# ---------------------------------------------------------------------------

SessionType = Literal["study", "practice", "revision", "assessment", "buffer"]


class Session(BaseModel):
    date: date
    start: time
    end: time
    subject: str
    topic: str
    type: SessionType


class TimeGrid(BaseModel):
    sessions: list[Session]
    total_hours: float
    rest_days: list[date] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 5. Strategy — Agent 5
# ---------------------------------------------------------------------------


class AnnotatedSession(Session):
    method: str
    resources_hint: str
    expected_outcome: str


class TechniqueMap(BaseModel):
    annotated_sessions: list[AnnotatedSession]


# ---------------------------------------------------------------------------
# 6. Adaptation — Agent 6
# ---------------------------------------------------------------------------


class Trigger(BaseModel):
    when: str  # e.g. "missed_session", "low_quiz_score"
    action: str  # e.g. "shift forward 1 day", "add 30-min remediation block"
    notes: Optional[str] = None


class AdaptationRules(BaseModel):
    triggers: list[Trigger]
    weekly_review_template: str


# ---------------------------------------------------------------------------
# 7. Final plan — Agent 7
# ---------------------------------------------------------------------------


class FinalStudyPlan(BaseModel):
    markdown: str  # full rendered plan
    summary: str  # 1-paragraph TLDR


# ---------------------------------------------------------------------------
# 8. Review — Agent 8
# ---------------------------------------------------------------------------

Verdict = Literal["pass", "revise"]


class ReviewIssue(BaseModel):
    severity: Literal["info", "warning", "error"]
    message: str


class ReviewReport(BaseModel):
    verdict: Verdict
    issues: list[ReviewIssue] = Field(default_factory=list)
    final_plan_markdown: str
