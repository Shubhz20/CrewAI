"""A tiny static topic-difficulty lookup tool used by the Diagnostic agent.

In production this would be replaced by RAG over a curriculum file or by an
external API. The shape is what matters: a CrewAI `@tool`-decorated callable
that returns a small JSON-serializable value.
"""

from __future__ import annotations

from crewai.tools import tool


# Difficulty is on a 1-5 scale (1 = trivial, 5 = expert-level).
_DIFFICULTY_TABLE: dict[str, int] = {
    # Maths
    "algebra": 2,
    "trigonometry": 3,
    "calculus": 4,
    "linear algebra": 4,
    "probability": 3,
    "statistics": 3,
    # Physics
    "mechanics": 3,
    "thermodynamics": 4,
    "electromagnetism": 5,
    "optics": 3,
    "modern physics": 4,
    # Chemistry
    "physical chemistry": 4,
    "organic chemistry": 4,
    "inorganic chemistry": 3,
    # CS / general
    "data structures": 3,
    "algorithms": 4,
    "operating systems": 4,
    "databases": 3,
    "computer networks": 3,
}


@tool("topic_difficulty_lookup")
def topic_difficulty_lookup(topic: str) -> int:
    """Return an estimated difficulty (1-5) for the given topic name.

    Falls back to 3 (medium) for unknown topics.
    """
    return _DIFFICULTY_TABLE.get(topic.strip().lower(), 3)
