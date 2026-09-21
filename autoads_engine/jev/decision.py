"""
decision.py — Raw Jev Response Parser, Validator & Normalizer
=============================================================
Transforms untrusted, raw TypeSafe SystemOneResponse objects into fully typed,
validated JEVDecision instances.
Guarantees that no invalid enum, out-of-bounds intensity, or malformed data
ever enters the AutoAds rendering engines.
"""

from __future__ import annotations
import logging
from typing import Optional, List, Tuple, Dict, Any

from autoads_engine.scene_model import ScenePurpose, SceneEmotion
from autoads_engine.jev.schema import JEVDecision, compute_decision_hash

logger = logging.getLogger("autoads.jev.decision")


def parse_and_validate(
    scene_id: int,
    raw_script: str,
    raw_response: Any,
    script_keywords: Optional[List[str]] = None,
    model_name: str = "jev-latest",
) -> Tuple[Optional[JEVDecision], List[str]]:
    """
    Parses a raw TypeSafe SystemOneResponse (or mock dict) and validates it against
    AutoAds constraints.

    Returns:
        (JEVDecision, []) on success
        (None, [error_reasons]) on failure (triggering fallback)
    """
    errors: List[str] = []

    if scene_id < 0:
        errors.append(f"Invalid scene_id: {scene_id} (must be >= 0)")

    if not raw_response:
        errors.append("Empty raw_response")
        return None, errors

    # Extract answers dictionary
    answers = getattr(raw_response, "answers", None)
    if answers is None and isinstance(raw_response, dict):
        answers = raw_response.get("answers", raw_response)

    if not isinstance(answers, dict):
        errors.append("Malformed response: 'answers' must be a dictionary")
        return None, errors

    # 1. Purpose validation
    purpose_ans = answers.get("purpose")
    purpose_raw = getattr(purpose_ans, "choice", None) if purpose_ans else None
    if purpose_raw is None and isinstance(purpose_ans, dict):
        purpose_raw = purpose_ans.get("choice")
    elif isinstance(purpose_ans, str):
        purpose_raw = purpose_ans

    purpose: Optional[ScenePurpose] = None
    if purpose_raw:
        try:
            purpose = ScenePurpose(str(purpose_raw).lower().strip())
        except ValueError:
            errors.append(f"Invalid ScenePurpose enum value: '{purpose_raw}'")
    else:
        errors.append("Missing required question answer: 'purpose'")

    # 2. Emotion validation
    emotion_ans = answers.get("emotion")
    emotion_raw = getattr(emotion_ans, "choice", None) if emotion_ans else None
    if emotion_raw is None and isinstance(emotion_ans, dict):
        emotion_raw = emotion_ans.get("choice")
    elif isinstance(emotion_ans, str):
        emotion_raw = emotion_ans

    emotion: Optional[SceneEmotion] = None
    if emotion_raw:
        try:
            emotion = SceneEmotion(str(emotion_raw).lower().strip())
        except ValueError:
            errors.append(f"Invalid SceneEmotion enum value: '{emotion_raw}'")
    else:
        errors.append("Missing required question answer: 'emotion'")

    # 3. Intensity validation & normalization
    intensity_ans = answers.get("intensity")
    intensity_raw = getattr(intensity_ans, "score", None) if intensity_ans else None
    if intensity_raw is None and isinstance(intensity_ans, dict):
        intensity_raw = intensity_ans.get("score")
    elif isinstance(intensity_ans, (int, float)):
        intensity_raw = intensity_ans

    intensity: float = 0.7
    if intensity_raw is not None:
        try:
            raw_val = float(intensity_raw)
            # TypeSafe Score with 4 levels (0..3): normalize to 0.0..1.0 if > 1.0
            if raw_val > 1.0:
                normalized = raw_val / 3.0
            else:
                normalized = raw_val
            # Safety clamp: must be strictly in [0.0, 1.0]
            intensity = max(0.0, min(1.0, normalized))
        except (ValueError, TypeError):
            errors.append(f"Invalid intensity value: '{intensity_raw}'")
    else:
        errors.append("Missing required question answer: 'intensity'")

    # 4. is_hook_or_climax (Noul)
    hook_climax_ans = answers.get("is_hook_or_climax")
    hook_climax_raw = getattr(hook_climax_ans, "noul", None) if hook_climax_ans else None
    if hook_climax_raw is None and isinstance(hook_climax_ans, dict):
        hook_climax_raw = hook_climax_ans.get("noul")
    elif isinstance(hook_climax_ans, (int, float, bool)):
        hook_climax_raw = hook_climax_ans

    is_hook_or_climax: bool = False
    if hook_climax_raw is not None:
        try:
            val = float(hook_climax_raw)
            is_hook_or_climax = val >= 0.5
        except (ValueError, TypeError):
            is_hook_or_climax = False

    # 5. Editorial Cue
    cue_ans = answers.get("editorial_cue")
    cue_raw = getattr(cue_ans, "choice", None) if cue_ans else None
    if cue_raw is None and isinstance(cue_ans, dict):
        cue_raw = cue_ans.get("choice")
    elif isinstance(cue_ans, str):
        cue_raw = cue_ans

    editorial_cue: str = str(cue_raw or "standard_delivery").strip()

    # 6. Confidence calculation
    conf_scores: List[float] = []
    for ans in [purpose_ans, emotion_ans, intensity_ans]:
        c = getattr(ans, "confidence", None) if ans else None
        if c is None and isinstance(ans, dict):
            c = ans.get("confidence")
        if isinstance(c, (int, float)):
            conf_scores.append(float(c))

    avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 1.0
    avg_conf = max(0.0, min(1.0, avg_conf))

    # 7. Emphasis words (validated against raw_script)
    emphasis_words: List[str] = []
    # If script_keywords supplied (from KeywordDetector or Jev extraction), verify they are in script
    for kw in (script_keywords or []):
        clean_kw = kw.strip()
        if clean_kw and clean_kw in raw_script and clean_kw not in emphasis_words:
            emphasis_words.append(clean_kw)

    # Return validated decision or failure
    if errors or purpose is None or emotion is None:
        logger.warning(f"JEV decision validation failed for scene {scene_id}: {errors}")
        return None, errors

    d_hash = compute_decision_hash(
        scene_id=scene_id,
        raw_script=raw_script,
        purpose=purpose,
        emotion=emotion,
        intensity=intensity,
        is_hook_or_climax=is_hook_or_climax,
        emphasis_words=emphasis_words,
        editorial_cue=editorial_cue,
        model=model_name,
    )

    decision = JEVDecision(
        scene_id=scene_id,
        raw_script=raw_script,
        purpose=purpose,
        emotion=emotion,
        intensity=intensity,
        is_hook_or_climax=is_hook_or_climax,
        emphasis_words=emphasis_words,
        editorial_cue=editorial_cue,
        model=model_name,
        confidence=avg_conf,
        decision_hash=d_hash,
    )
    return decision, []
