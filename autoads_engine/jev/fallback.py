"""
fallback.py — Deterministic Fallback Generator for JEVDecision
==============================================================
Generates a guaranteed, safe, and deterministic JEVDecision using existing v10
scene metadata and KeywordDetector rules.
Ensures AutoAds never crashes and continues rendering cleanly when TypeSafe API
is unavailable, offline, misconfigured, or returns invalid schemas.
"""

from __future__ import annotations
import logging
from typing import List, Optional

from autoads_engine.scene_model import SceneDef, ScenePurpose, SceneEmotion
from autoads_engine.caption import KeywordDetector
from autoads_engine.jev.schema import JEVDecision, compute_decision_hash

logger = logging.getLogger("autoads.jev.fallback")


class JevFallback:
    """
    Creates deterministic JEVDecision instances without calling any external LLM/API.
    """

    def __init__(self, detector: Optional[KeywordDetector] = None):
        self.detector = detector or KeywordDetector()

    def for_scene(
        self,
        scene: SceneDef,
        reason: str = "api_unavailable",
    ) -> JEVDecision:
        """
        Derives a deterministic JEVDecision from an existing SceneDef and its subtitle cues.
        """
        raw_script = " ".join([cue.text for cue in scene.sub_cues if cue.text]).strip()

        # 1. Purpose & Emotion from scene definition
        purpose = scene.purpose or ScenePurpose.BENEFIT
        emotion = scene.emotion or SceneEmotion.NEUTRAL

        # 2. Intensity from effective_intensity (clamped 0.0 ~ 1.0)
        intensity = max(0.0, min(1.0, scene.effective_intensity()))

        # 3. Hook or climax
        is_hook_or_climax = purpose in (ScenePurpose.HOOK, ScenePurpose.CTA, ScenePurpose.OFFER)

        # 4. Emphasis words extracted via KeywordDetector
        emphasis_words: List[str] = []
        if raw_script:
            tags = self.detector.analyze(raw_script)
            # Pick highest priority keyword text
            for t in tags[:2]:
                if t.text in raw_script and t.text not in emphasis_words:
                    emphasis_words.append(t.text)

        # 5. Editorial Cue mapping based on purpose
        cue_map = {
            ScenePurpose.HOOK: "hook_attention",
            ScenePurpose.PROBLEM: "empathize_pain",
            ScenePurpose.AGITATION: "amplify_crisis",
            ScenePurpose.SOLUTION: "satisfying_relief",
            ScenePurpose.PRODUCT: "scientific_clarity",
            ScenePurpose.PROOF: "satisfying_relief",
            ScenePurpose.BENEFIT: "satisfying_relief",
            ScenePurpose.OFFER: "urgent_action",
            ScenePurpose.CTA: "urgent_action",
        }
        editorial_cue = cue_map.get(purpose, "standard_delivery")

        d_hash = compute_decision_hash(
            scene_id=scene.id,
            raw_script=raw_script,
            purpose=purpose,
            emotion=emotion,
            intensity=intensity,
            is_hook_or_climax=is_hook_or_climax,
            emphasis_words=emphasis_words,
            editorial_cue=editorial_cue,
            model=f"fallback:{reason}",
        )

        logger.info(f"Fallback JEVDecision generated for scene {scene.id} (reason: {reason})")

        return JEVDecision(
            scene_id=scene.id,
            raw_script=raw_script,
            purpose=purpose,
            emotion=emotion,
            intensity=intensity,
            is_hook_or_climax=is_hook_or_climax,
            emphasis_words=emphasis_words,
            editorial_cue=editorial_cue,
            model=f"fallback:{reason}",
            confidence=1.0,
            decision_hash=d_hash,
        )
