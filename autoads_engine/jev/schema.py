"""
schema.py — JEVDecision Data Model & TypeSafe Question Definitions
===================================================================
Defines the typed editorial decision returned by TypeSafe System One (Jev),
along with deterministic hashing and question schemas.

Jev focuses solely on editorial meaning (purpose, emotion, intensity, emphasis)
and never dictates low-level rendering parameters (FFmpeg filters, zoom ratios,
coordinates, or filenames).
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from autoads_engine.scene_model import ScenePurpose, SceneEmotion

try:
    from typesafe_sdk import Choice, Noul, Score
except ImportError:
    Choice = None
    Noul = None
    Score = None


# ── Decision Model ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class JEVDecision:
    """
    Validated typed editorial decision for a single scene.
    """
    scene_id: int
    raw_script: str
    purpose: ScenePurpose
    emotion: SceneEmotion
    intensity: float                   # Normalized between 0.0 and 1.0
    is_hook_or_climax: bool            # True if hook or offer climax
    emphasis_words: List[str]          # High-priority focus words in the script
    editorial_cue: str                 # Human-readable directing intention
    model: str = "jev-latest"
    confidence: float = 1.0            # Aggregated model confidence
    decision_hash: str = ""            # Deterministic hash for caching

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
    Generates a deterministic 16-character SHA-256 hash representing the decision.
    """
    canonical_payload = {
        "scene_id": scene_id,
        "raw_script": raw_script.strip(),
        "purpose": purpose.value,
        "emotion": emotion.value,
        "intensity": round(float(intensity), 3),
        "is_hook_or_climax": bool(is_hook_or_climax),
        "emphasis_words": sorted([w.strip() for w in emphasis_words if w.strip()]),
        "editorial_cue": editorial_cue.strip(),
        "model": model.strip(),
    }
    encoded = json.dumps(canonical_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
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
    """
    if Choice is None or Noul is None or Score is None:
        raise RuntimeError("typesafe_sdk is not installed or available.")

    return {
        "purpose": Choice(
            instructions="What is the primary narrative marketing purpose of this scene?",
            criteria=PURPOSE_RUBRIC,
        ),
        "emotion": Choice(
            instructions="What is the dominant emotional tone expressed or targeted in this scene?",
            criteria=EMOTION_RUBRIC,
        ),
        "intensity": Score(
            instructions="How intense should the editing pace and visual energy be for this scene?",
            criteria=INTENSITY_LEVELS,
        ),
        "is_hook_or_climax": Noul(
            instructions="Is this scene a critical retention hook (scene 1) or an urgent final CTA climax?",
            criteria={"true": "Hook or climax moment", "false": "Body narrative or explanation"},
        ),
        "editorial_cue": Choice(
            instructions="Which directorial guidance best describes the intended editorial rhythm?",
            criteria=EDITORIAL_CUE_RUBRIC,
        ),
    }
