"""
decision.py — Raw Jev Response Parser, Validator & Normalizer
=============================================================
Transforms untrusted, raw TypeSafe SystemOneResponse objects into fully typed,
validated JEVDecision instances.

Validation policy (per spec):
  STRUCTURAL FAILURES → return (None, errors) triggering fallback:
    - Empty / malformed response
    - purpose invalid or missing
    - emotion invalid or missing
    - intensity missing or unparseable
    - required field missing
    - TypeSafe API failure

  SOFT FAILURES → normalize / remove, keep rest of decision:
    - emphasis_words: substring not found in script → drop that word, keep rest
    - emphasis_words: whitespace/form variation → normalize and retry
    - is_hook_or_climax: default to False
    - editorial_cue: default to 'standard_delivery'

TypeSafe SDK v0.7.0 answer attributes:
  ChoiceAnswer: .choice (str), .confidence (float)
  ScoreAnswer:  .score  (float 0..N prob-weighted), .confidence (float)
  NoulAnswer:   .noul   (float 0..1, probability of True)
"""

from __future__ import annotations
import re
import unicodedata
import logging
from typing import Optional, List, Tuple, Dict, Any

from autoads_engine.scene_model import ScenePurpose, SceneEmotion
from autoads_engine.jev.schema import JEVDecision, compute_decision_hash

logger = logging.getLogger("autoads.jev.decision")


def _normalize_text(text: str) -> str:
    """
    Normalize Korean/mixed text for lenient matching:
    - Strip whitespace
    - Unicode NFKC normalization (halfwidth → fullwidth, etc.)
    - Collapse internal spaces
    """
    text = unicodedata.normalize("NFKC", text.strip())
    return re.sub(r"\s+", " ", text)


def _is_word_in_script(word: str, script: str) -> bool:
    """
    Lenient substring check:
    1. Exact normalized match
    2. Normalized word as substring of normalized script
    3. Stripped of all spaces and punctuation for compact comparison
    """
    w_norm = _normalize_text(word)
    s_norm = _normalize_text(script)
    if not w_norm:
        return False
    if w_norm in s_norm:
        return True
    # Compact comparison: remove spaces and common punctuation
    def compact(s: str) -> str:
        return re.sub(r"[\s\u200b\u3000!?,.:;%\-]", "", s)
    if compact(w_norm) and compact(w_norm) in compact(s_norm):
        return True
    return False


def _extract_answer_value(answer: Any, field: str) -> Optional[Any]:
    """
    Extracts a value from a TypeSafe answer object or dict.
    Supports SDK v0.7.0 model objects and plain dicts.
    """
    if answer is None:
        return None
    # SDK typed answer object
    val = getattr(answer, field, None)
    if val is not None:
        return val
    # Plain dict (test mocks)
    if isinstance(answer, dict):
        return answer.get(field)
    return None


def parse_and_validate(
    scene_id: int,
    raw_script: str,
    raw_response: Any,
    script_keywords: Optional[List[str]] = None,
    model_name: str = "jev-latest",
) -> Tuple[Optional[JEVDecision], List[str]]:
    """
    Parses a raw TypeSafe SystemOneResponse (or mock dict) and validates it.

    Returns:
        (JEVDecision, [])          on success
        (None, [error_reasons])    on structural failure (triggers fallback)

    Emphasis words failure is NON-structural: bad words are dropped, rest continues.
    """
    errors: List[str] = []

    # ── Guard: empty response ──────────────────────────────────────────────
    if not raw_response:
        errors.append("Empty raw_response")
        return None, errors

    # ── Extract answers dict ───────────────────────────────────────────────
    answers = getattr(raw_response, "answers", None)
    if answers is None and isinstance(raw_response, dict):
        answers = raw_response.get("answers", raw_response)
    if not isinstance(answers, dict):
        errors.append("Malformed response: 'answers' must be a dict")
        return None, errors

    # ── 1. Purpose  (STRUCTURAL — must be valid) ────────────────────────────
    purpose_ans = answers.get("purpose")
    purpose_raw = _extract_answer_value(purpose_ans, "choice")
    if purpose_raw is None and isinstance(purpose_ans, str):
        purpose_raw = purpose_ans

    purpose: Optional[ScenePurpose] = None
    if purpose_raw:
        try:
            purpose = ScenePurpose(str(purpose_raw).lower().strip())
        except ValueError:
            errors.append(f"Invalid ScenePurpose: '{purpose_raw}'")
    else:
        errors.append("Missing required answer: 'purpose'")

    # ── 2. Emotion  (STRUCTURAL — must be valid) ────────────────────────────
    emotion_ans = answers.get("emotion")
    emotion_raw = _extract_answer_value(emotion_ans, "choice")
    if emotion_raw is None and isinstance(emotion_ans, str):
        emotion_raw = emotion_ans

    emotion: Optional[SceneEmotion] = None
    if emotion_raw:
        try:
            emotion = SceneEmotion(str(emotion_raw).lower().strip())
        except ValueError:
            errors.append(f"Invalid SceneEmotion: '{emotion_raw}'")
    else:
        errors.append("Missing required answer: 'emotion'")

    # ── 3. Intensity  (STRUCTURAL — must be parseable) ──────────────────────
    # SDK v0.7.0 ScoreAnswer.score is a float (0..N, prob-weighted avg over levels)
    # With 4 levels (0..3), normalize to [0.0, 1.0] if > 1.0
    intensity_ans = answers.get("intensity")
    intensity_raw = _extract_answer_value(intensity_ans, "score")
    if intensity_raw is None and isinstance(intensity_ans, (int, float)):
        intensity_raw = intensity_ans

    intensity: float = 0.7  # default if missing
    if intensity_raw is not None:
        try:
            raw_val = float(intensity_raw)
            intensity = raw_val / 3.0 if raw_val > 1.0 else raw_val
            intensity = max(0.0, min(1.0, intensity))
        except (ValueError, TypeError):
            errors.append(f"Unparseable intensity value: '{intensity_raw}'")
    else:
        errors.append("Missing required answer: 'intensity'")

    # Early exit on structural errors
    if errors or purpose is None or emotion is None:
        logger.warning(
            f"JEV structural validation failed for scene {scene_id}: {errors}"
        )
        return None, errors

    # ── 4. is_hook_or_climax  (SOFT — default False) ────────────────────────
    # SDK v0.7.0 NoulAnswer.noul: float 0..1 (probability of True)
    hook_climax_ans = answers.get("is_hook_or_climax")
    hook_climax_raw = _extract_answer_value(hook_climax_ans, "noul")
    if hook_climax_raw is None and isinstance(hook_climax_ans, (int, float, bool)):
        hook_climax_raw = hook_climax_ans

    is_hook_or_climax: bool = False
    if hook_climax_raw is not None:
        try:
            is_hook_or_climax = float(hook_climax_raw) >= 0.5
        except (ValueError, TypeError):
            is_hook_or_climax = False

    # ── 5. Editorial Cue  (SOFT — default 'standard_delivery') ──────────────
    cue_ans = answers.get("editorial_cue")
    cue_raw = _extract_answer_value(cue_ans, "choice")
    if cue_raw is None and isinstance(cue_ans, str):
        cue_raw = cue_ans
    editorial_cue = str(cue_raw or "standard_delivery").strip()

    # ── 6. Confidence  (SOFT — average of available scores) ─────────────────
    conf_scores: List[float] = []
    for ans in (purpose_ans, emotion_ans, intensity_ans):
        c = _extract_answer_value(ans, "confidence")
        if isinstance(c, (int, float)):
            conf_scores.append(float(c))
    avg_conf = (
        max(0.0, min(1.0, sum(conf_scores) / len(conf_scores)))
        if conf_scores
        else 1.0
    )

    # ── 7. Emphasis words  (SOFT — drop unverified, keep rest) ──────────────
    # Accept keywords from both Jev response (if present) and detector candidates.
    # Lenient match: normalized substring check. Bad words dropped silently.
    raw_emphasis_words: List[str] = []

    # Try to get emphasis words from Jev response (if model added them)
    ew_ans = answers.get("emphasis_words")
    if isinstance(ew_ans, list):
        raw_emphasis_words.extend(str(w) for w in ew_ans if w)
    elif isinstance(ew_ans, str) and ew_ans.strip():
        raw_emphasis_words.extend(ew_ans.split(","))

    # Also consider detector-supplied candidates
    if script_keywords:
        for kw in script_keywords:
            if kw.strip() and kw.strip() not in raw_emphasis_words:
                raw_emphasis_words.append(kw.strip())

    emphasis_words: List[str] = []
    dropped: List[str] = []
    for kw in raw_emphasis_words:
        clean = _normalize_text(kw)
        if not clean:
            continue
        if _is_word_in_script(clean, raw_script):
            if clean not in emphasis_words:
                emphasis_words.append(clean)
        else:
            dropped.append(clean)

    if dropped:
        logger.debug(
            f"Scene {scene_id}: {len(dropped)} emphasis word(s) not found in script "
            f"(dropped, not fallback): {dropped}"
        )

    # ── Build final JEVDecision ───────────────────────────────────────────
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

    return JEVDecision(
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
    ), []

