"""
planner.py — SceneDef to Jev Context & Decision Orchestration
============================================================
Converts AutoAds SceneDef structures into clean editorial context, invokes Jev,
and orchestrates validation and fallback.
Strictly excludes all rendering implementation details (FFmpeg filters, ASS tags,
coordinates, asset paths) from Jev inputs.
"""

from __future__ import annotations
import logging
from typing import List, Dict, Optional, Any

from autoads_engine.scene_model import SceneDef
from autoads_engine.caption import KeywordDetector
from autoads_engine.jev.schema import JEVDecision, build_jev_questions
from autoads_engine.jev.client import JevClient
from autoads_engine.jev.decision import parse_and_validate
from autoads_engine.jev.fallback import JevFallback

logger = logging.getLogger("autoads.jev.planner")


class JevPlanner:
    """
    Orchestrates editorial decisions for scenes using TypeSafe Jev or deterministic fallback.
    """

    def __init__(
        self,
        client: Optional[JevClient] = None,
        fallback: Optional[JevFallback] = None,
        detector: Optional[KeywordDetector] = None,
    ):
        self.client = client or JevClient()
        self.detector = detector or KeywordDetector()
        self.fallback = fallback or JevFallback(detector=self.detector)

    def prepare_scene_context(self, scene: SceneDef) -> Dict[str, Any]:
        """
        Extracts editorial context from SceneDef.
        Excludes all FFmpeg/rendering internals.
        """
        full_script = " ".join([q.text for q in scene.sub_cues if q.text]).strip()
        cue_list = [q.text for q in scene.sub_cues if q.text]
        total_dur = sum(c.dur for c in scene.cuts) if scene.cuts else 2.0

        return {
            "scene_id": scene.id,
            "script": full_script,
            "cues": cue_list,
            "estimated_duration_sec": round(total_dur, 2),
            "purpose_hint": scene.purpose.value if scene.purpose else "benefit",
        }

    def plan_scene(
        self,
        scene: SceneDef,
        force_fallback: bool = False,
    ) -> JEVDecision:
        """
        Produces a validated JEVDecision for a single scene.
        """
        raw_script = " ".join([q.text for q in scene.sub_cues if q.text]).strip()

        # Check if fallback is explicitly requested or client is unavailable
        if force_fallback or not self.client.is_available():
            reason = "cli_no_jev" if force_fallback else "client_unavailable"
            return self.fallback.for_scene(scene, reason=reason)

        context = self.prepare_scene_context(scene)
        try:
            questions = build_jev_questions()
            raw_resp = self.client.evaluate(state=context, questions=questions)
        except Exception as e:
            logger.warning(f"Jev API call exception for scene {scene.id}: {e}")
            return self.fallback.for_scene(scene, reason=f"api_exception:{type(e).__name__}")

        if raw_resp is None:
            return self.fallback.for_scene(scene, reason="empty_api_response")

        # Candidate keywords from detector to assist emphasis validation
        detected_tags = self.detector.analyze(raw_script)
        candidates = [t.text for t in detected_tags]

        decision, errors = parse_and_validate(
            scene_id=scene.id,
            raw_script=raw_script,
            raw_response=raw_resp,
            script_keywords=candidates,
            model_name=self.client.model,
        )

        if decision is None:
            logger.warning(f"Jev response validation failed for scene {scene.id} ({errors}); using fallback.")
            return self.fallback.for_scene(scene, reason="validation_failed")

        return decision

    def plan_scenes(
        self,
        scenes: List[SceneDef],
        force_fallback: bool = False,
    ) -> List[JEVDecision]:
        """
        Produces validated JEVDecisions for all scenes in the ad.
        """
        return [self.plan_scene(s, force_fallback=force_fallback) for s in scenes]
