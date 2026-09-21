"""
schema.py — JEVDecision Data Model & TypeSafe Question Definitions
===================================================================
Defines the typed editorial decision returned by TypeSafe System One (Jev),
along with deterministic hashing and question schemas.

Jev focuses solely on editorial meaning (purpose, emotion, intensity, emphasis)
and never dictates low-level rendering parameters (FFmpeg filters, zoom ratios,
coordinates, or filenames).

TypeSafe SDK v0.7.0 verified API:
  - Choice(instructions=str, criteria=dict[str, str])
  - Score(instructions=str, criteria=list[str])
  - Noul(instructions=str, criteria=dict[str, str])
  - TypeSafeClient(api_key=str, timeout=float)
  - client.system_one(state=dict, questions=dict, model=str) -> SystemOneResponse
  - SystemOneResponse.answers: dict[str, ChoiceAnswer | ScoreAnswer | NoulAnswer]
  - ChoiceAnswer.choice: str,  .confidence: float
  - ScoreAnswer.score: float (0..N prob-weighted avg),  .confidence: float
  - NoulAnswer.noul: float  (0..1 probability of True)
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from autoads_engine.scene_model import ScenePurpose, SceneEmotion

try:
    from typesafe_sdk import Choice, Noul, Score
    _SDK_AVAILABLE = True
except ImportError:
    Choice = None
    Noul = None
    Score = None
    _SDK_AVAILABLE = False


# ── Decision Model ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class JEVDecision:
    """
    Validated typed editorial decision for a single scene.

    Phase 1 contract:
      - Produced by JevPlanner.plan_scene() or JevFallback.for_scene()
      - Consumed only by Phase 2 Policy layer (not yet implemented)
      - Never directly modifies FFmpeg filters or ASS tags
    """
    scene_id: int
    raw_script: str
    purpose: ScenePurpose
    emotion: SceneEmotion
    intensity: float           # Normalized [0.0, 1.0]
    is_hook_or_climax: bool    # True if hook or final CTA climax
    emphasis_words: List[str]  # Verified focus words from the script
    editorial_cue: str         # Directing intention key
    model: str = "jev-latest"
    confidence: float = 1.0    # Aggregated model confidence [0.0, 1.0]
    decision_hash: str = ""    # Deterministic 16-char SHA-256 hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "raw_script": self.raw_script,
            "purpose": self.purpose.value,
            "emotion": self.emotion.value,
            "intensity": round(self.intensity, 3),
            "is_hook_or_climax": self.is_hook_or_climax,
            "emphasis_words": list(self.emphasis_words),
            "editorial_cue": self.editorial_cue,
            "model": self.model,
            "confidence": round(self.confidence, 3),
            "decision_hash": self.decision_hash,
        }

    def __repr__(self) -> str:
        return (
            f"JEVDecision(scene={self.scene_id} "
            f"purpose={self.purpose.value} "
            f"emotion={self.emotion.value} "
            f"intensity={self.intensity:.2f} "
            f"climax={self.is_hook_or_climax} "
            f"cue={self.editorial_cue} "
            f"hash={self.decision_hash} "
            f"model={self.model})"
        )


def compute_decision_hash(
    scene_id: int,
    raw_script: str,
    purpose: ScenePurpose,
    emotion: SceneEmotion,
    intensity: float,
    is_hook_or_climax: bool,
    emphasis_words: List[str],
    editorial_cue: str,
    model: str = "jev-latest",
) -> str:
    """
    Generates a deterministic 16-character hex hash from canonical JSON.

    Canonical field order is fixed via sort_keys=True.
    Emphasis words are sorted for order-independence.
    Intensity is rounded to 3 decimal places before hashing.

    Identical inputs  →  identical hash.
    Any field change  →  different hash.
    """
    canonical_payload = {
        "editorial_cue": editorial_cue.strip(),
        "emotion": emotion.value,
        "emphasis_words": sorted([w.strip() for w in emphasis_words if w.strip()]),
        "intensity": round(float(intensity), 3),
        "is_hook_or_climax": bool(is_hook_or_climax),
        "model": model.strip(),
        "purpose": purpose.value,
        "raw_script": raw_script.strip(),
        "scene_id": scene_id,
    }
    encoded = json.dumps(
        canonical_payload, sort_keys=True, ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


# ── Question Criteria & Rubrics ────────────────────────────────────────────

PURPOSE_RUBRIC = {
    ScenePurpose.HOOK.value: "Attention grabber, initial visual hook, first 3 seconds",
    ScenePurpose.PROBLEM.value: "Expresses frustration, skin trouble, or failure of existing products",
    ScenePurpose.AGITATION.value: "Amplifies pain points, worsening symptoms, crisis feeling",
    ScenePurpose.SOLUTION.value: "Introduces new alternative, discovery of novel mechanism",
    ScenePurpose.PRODUCT.value: "Explains formula, ingredients, patents, clinical action",
    ScenePurpose.PROOF.value: "Demonstrates Before & After result, clear visual evidence",
    ScenePurpose.BENEFIT.value: "Long-term positive outcome, daily confidence, smooth skin",
    ScenePurpose.OFFER.value: "Discount, bundle pricing, limited-time promotion",
    ScenePurpose.CTA.value: "Urges viewer to click link, swipe up, or order now",
}

EMOTION_RUBRIC = {
    SceneEmotion.CONFIDENT.value: "Self-assured, satisfied, authoritative recommendation",
    SceneEmotion.FRUSTRATED.value: "Annoyed with ineffective products, oily or damaged skin",
    SceneEmotion.SHOCKED.value: "Surprised reaction, disbelief, unexpected twist",
    SceneEmotion.WARM.value: "Friendly, empathetic, reassuring advice",
    SceneEmotion.HAPPY.value: "Delighted with clear skin, glowing mood, high energy",
    SceneEmotion.CURIOUS.value: "Inquisitive, explaining mechanism, scientific interest",
    SceneEmotion.URGENT.value: "Fear of missing out, immediate action required",
    SceneEmotion.NEUTRAL.value: "Informative, standard narrative delivery",
}

INTENSITY_LEVELS = [
    "Calm, subtle, slow explanatory pacing",
    "Moderate commercial rhythm, conversational",
    "High tension, snappy dynamic rhythm",
    "Maximum climax, intense urgency and impact",
]

EDITORIAL_CUE_RUBRIC = {
    "hook_attention": "Strong opening shock to stop scrolling",
    "empathize_pain": "Relatable problem presentation to build frustration",
    "amplify_crisis": "Dramatic tension before introducing solution",
    "satisfying_relief": "Pleasing visual transformation and relief",
    "scientific_clarity": "Credible ingredient explanation with focused clarity",
    "urgent_action": "High-conversion prompt compelling immediate click",
}


def build_jev_questions() -> Dict[str, Any]:
    """
    Constructs the TypeSafe System One question dictionary.

    Uses verified SDK v0.7.0 constructors:
      Choice(instructions=str, criteria=dict[str, str])
      Score(instructions=str, criteria=list[str])
      Noul(instructions=str, criteria=dict[str, str])
    """
    if not _SDK_AVAILABLE:
        raise RuntimeError(
            "typesafe_sdk is not installed. "
            "Install with: pip install typesafe-sdk"
        )

    return {
        "purpose": Choice(
            instructions=(
                "What is the primary narrative marketing purpose of this scene? "
                "Select the single best-matching purpose category."
            ),
            criteria=PURPOSE_RUBRIC,
        ),
        "emotion": Choice(
            instructions=(
                "What is the dominant emotional tone expressed or targeted in this scene? "
                "Select the single most prominent emotion."
            ),
            criteria=EMOTION_RUBRIC,
        ),
        "intensity": Score(
            instructions=(
                "How intense should the editing pace and visual energy be for this scene? "
                "0=calm, 3=maximum climax."
            ),
            criteria=INTENSITY_LEVELS,
        ),
        "is_hook_or_climax": Noul(
            instructions=(
                "Is this scene a critical retention hook (opening scene 1) "
                "or an urgent final CTA/offer climax? "
                "Answer true only for these two critical moments."
            ),
            criteria={"true": "Hook or climax moment", "false": "Body narrative or explanation"},
        ),
        "editorial_cue": Choice(
            instructions=(
                "Which directorial guidance best describes the intended editorial rhythm "
                "and visual emphasis for this scene?"
            ),
            criteria=EDITORIAL_CUE_RUBRIC,
        ),
    }
