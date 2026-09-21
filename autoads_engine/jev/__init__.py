"""
autoads_engine.jev — TypeSafe / Jev Editorial Decision Layer
============================================================
Provides typed editorial decisions from TypeSafe System One (Jev).
Separates editorial meaning from FFmpeg rendering execution.
"""

from autoads_engine.jev.schema import (
    JEVDecision,
    compute_decision_hash,
    build_jev_questions,
    PURPOSE_RUBRIC,
    EMOTION_RUBRIC,
    INTENSITY_LEVELS,
    EDITORIAL_CUE_RUBRIC,
)
from autoads_engine.jev.client import JevClient
from autoads_engine.jev.decision import parse_and_validate
from autoads_engine.jev.fallback import JevFallback
from autoads_engine.jev.planner import JevPlanner

__all__ = [
    "JEVDecision",
    "compute_decision_hash",
    "build_jev_questions",
    "PURPOSE_RUBRIC",
    "EMOTION_RUBRIC",
    "INTENSITY_LEVELS",
    "EDITORIAL_CUE_RUBRIC",
    "JevClient",
    "parse_and_validate",
    "JevFallback",
    "JevPlanner",
]
