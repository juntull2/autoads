"""
sfx_engine.py — Event-based SFX Engine
=========================================
Places SFX on the audio timeline based on scene purpose and intensity.
Replaces the hardcoded absolute-position SFX from v9.

Key rules (from AGENTS.md):
  - SFX over BGM ducked at -27dB
  - Not every cue gets an SFX — only contextually significant moments
  - 6 core SFX categories (snap, suspense, whoosh, ding, pop, click)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import os

from autoads_engine.scene_model import SceneDef, ScenePurpose, SFXEvent


# ---------------------------------------------------------------------------
# SFX keyword search map — matches v9's find_sfx() pattern
# ---------------------------------------------------------------------------
SFX_SEARCH_KEYWORDS: Dict[SFXEvent, List[str]] = {
    SFXEvent.SNAP:      ["Finger Snap", "snap", "스냅"],
    SFXEvent.SUSPENSE:  ["Suspense 1", "스릴러", "suspense", "라이저"],
    SFXEvent.WHOOSH:    ["Whoosh Transition 1", "whoosh", "우쉬"],
    SFXEvent.DING:      ["Ding Chime", "bell", "차임", "ding"],
    SFXEvent.POP:       ["물음표", "pop", "팝"],
    SFXEvent.CLICK:     ["Mouse Click", "클릭", "click"],
    SFXEvent.IMPACT:    ["Impact", "impact", "hit"],
    SFXEvent.RISING:    ["rising", "라이징", "rise"],
    SFXEvent.SWIPE:     ["swipe", "스와이프"],
}

# Volume adjustments per SFX type (dB relative to file level)
SFX_VOLUME: Dict[SFXEvent, int] = {
    SFXEvent.SNAP:     -8,
    SFXEvent.SUSPENSE: -12,
    SFXEvent.WHOOSH:   -8,
    SFXEvent.DING:     -8,
    SFXEvent.POP:      -6,
    SFXEvent.CLICK:    -10,
    SFXEvent.IMPACT:   -9,
    SFXEvent.RISING:   -10,
    SFXEvent.SWIPE:    -9,
}

# Max clip length per SFX (ms) — prevents long tails
SFX_MAX_LEN: Dict[SFXEvent, int] = {
    SFXEvent.SNAP:     1000,
    SFXEvent.SUSPENSE: 1800,
    SFXEvent.WHOOSH:   1500,
    SFXEvent.DING:     1200,
    SFXEvent.POP:      1000,
    SFXEvent.CLICK:    800,
    SFXEvent.IMPACT:   1200,
    SFXEvent.RISING:   2000,
    SFXEvent.SWIPE:    1000,
}


@dataclass
class SFXPlacement:
    """A single SFX to be overlaid at a specific time."""
    event: SFXEvent
    abs_time_s: float   # absolute position in master timeline (seconds)
    volume_db: int      # volume adjustment in dB
    source: str = ""    # origin event description


@dataclass
class SFXTrigger:
    """An event trigger candidate for SFX placement."""
    event: SFXEvent
    abs_time_s: float
    priority: int       # 1 to 10 (higher = takes precedence)
    source: str         # descriptive trigger tag
    volume_offset: int = 0


class SFXEngine:
    """
    Event-based SFX placement engine.
    Connects SFX to:
      1. Cut transitions (FLASH, WHITE_FLASH, ZOOM_CUT) -> WHOOSH / SWIPE
      2. Camera motions (PUNCH_ZOOM, FAST_PUSH) -> IMPACT / WHOOSH
      3. Caption & Keyword events (NUMBER_POP, PUNCH, SHAKE, CTA) -> DING / POP / CLICK / SUSPENSE
      4. Opening hook -> SNAP
    Applies cooldown and priority arbitration to prevent audio clutter.
    """

    def __init__(self, sfx_dir: str, intensity_scale: float = 1.0):
        self.sfx_dir = sfx_dir
        self.intensity_scale = intensity_scale
        self._cache: Dict[str, Optional[str]] = {}

    def find_sfx(self, event: SFXEvent) -> Optional[str]:
        """Find SFX file path for a given event type. Cached."""
        if event in self._cache:
            return self._cache[event]
        keywords = SFX_SEARCH_KEYWORDS.get(event, [])
        for kw in keywords:
            path = self._search(kw)
            if path:
                self._cache[event] = path
                return path
        self._cache[event] = None
        return None

    def _search(self, kw: str) -> Optional[str]:
        if not os.path.isdir(self.sfx_dir):
            return None
        for root, dirs, files in os.walk(self.sfx_dir):
            for f in files:
                if kw.lower() in f.lower():
                    return os.path.join(root, f)
        return None

    def compute_placements(
        self,
        scenes: List[SceneDef],
        scene_offsets: List[float],
        keyword_detector=None,
    ) -> List[SFXPlacement]:
        """
        Compute event-driven SFX placements across the entire ad timeline.

        Integrates:
          - Scene hook openings
          - Transition cut points
          - Camera motion events (punch zoom, fast push)
          - Caption keyword events (numbers, cta, impact words)
        """
        from autoads_engine.scene_model import CameraMotion, TransitionType, CaptionAnimStyle

        detector = keyword_detector
        if detector is None:
            try:
                from autoads_engine.caption import KeywordDetector
                detector = KeywordDetector()
            except Exception:
                detector = None

        raw_triggers: List[SFXTrigger] = []

        for s_idx, (scene, s_offset) in enumerate(zip(scenes, scene_offsets)):
            intensity = scene.effective_intensity() * self.intensity_scale
            if intensity < 0.35:
                continue

            # 1. Opening Hook Snap
            if scene.purpose == ScenePurpose.HOOK:
                raw_triggers.append(SFXTrigger(
                    event=SFXEvent.SNAP,
                    abs_time_s=s_offset + 0.0,
                    priority=10,
                    source="hook:opening_snap"
                ))

            # 2. Transition & Camera events per Cut
            cut_offset = s_offset
            for cut in scene.cuts:
                # Transition trigger
                if cut.transition_in in (TransitionType.FLASH, TransitionType.WHITE_FLASH, TransitionType.ZOOM_CUT):
                    raw_triggers.append(SFXTrigger(
                        event=SFXEvent.WHOOSH,
                        abs_time_s=cut_offset + 0.05,
                        priority=6,
                        source=f"transition:{cut.transition_in.value}"
                    ))

                # Camera motion trigger
                if cut.camera == CameraMotion.PUNCH_ZOOM:
                    raw_triggers.append(SFXTrigger(
                        event=SFXEvent.IMPACT,
                        abs_time_s=cut_offset + 0.05,
                        priority=8,
                        source="camera:punch_zoom"
                    ))
                elif cut.camera == CameraMotion.FAST_PUSH and cut.transition_in not in (TransitionType.FLASH, TransitionType.WHITE_FLASH):
                    raw_triggers.append(SFXTrigger(
                        event=SFXEvent.WHOOSH,
                        abs_time_s=cut_offset + 0.02,
                        priority=5,
                        source="camera:fast_push"
                    ))
                cut_offset += cut.dur

            # 3. Caption & Keyword events per SubCue
            for cue in scene.sub_cues:
                cue_abs = s_offset + cue.start
                tags = detector.analyze(cue.text) if detector else []
                categories = {t.category for t in tags}

                if cue.anim == CaptionAnimStyle.NUMBER_POP or 'number' in categories:
                    raw_triggers.append(SFXTrigger(
                        event=SFXEvent.DING,
                        abs_time_s=cue_abs,
                        priority=7,
                        source="caption:number_pop"
                    ))
                elif cue.anim == CaptionAnimStyle.SHAKE or 'impact' in categories:
                    raw_triggers.append(SFXTrigger(
                        event=SFXEvent.SUSPENSE if scene.purpose in (ScenePurpose.PROBLEM, ScenePurpose.AGITATION) else SFXEvent.IMPACT,
                        abs_time_s=cue_abs,
                        priority=7,
                        source="caption:impact_shake"
                    ))
                elif cue.anim == CaptionAnimStyle.PUNCH and 'cta' in categories:
                    raw_triggers.append(SFXTrigger(
                        event=SFXEvent.CLICK,
                        abs_time_s=cue_abs,
                        priority=9,
                        source="caption:cta_punch"
                    ))
                elif cue.anim == CaptionAnimStyle.BOUNCE or 'positive' in categories:
                    if scene.purpose in (ScenePurpose.PROOF, ScenePurpose.BENEFIT):
                        raw_triggers.append(SFXTrigger(
                            event=SFXEvent.DING,
                            abs_time_s=cue_abs,
                            priority=6,
                            source="caption:positive_bounce"
                        ))

            # 4. Fallback: Purpose-driven scene defaults
            for evt in scene.effective_sfx():
                raw_triggers.append(SFXTrigger(
                    event=evt,
                    abs_time_s=s_offset + self._sfx_offset_within_scene(evt, scene),
                    priority=4,
                    source=f"scene_default:{evt.value}"
                ))

        # Sort triggers by timestamp
        raw_triggers.sort(key=lambda t: t.abs_time_s)

        # Priority arbitration with 0.28s cooldown
        COOLDOWN = 0.28
        resolved: List[SFXTrigger] = []
        for trig in raw_triggers:
            if not resolved:
                resolved.append(trig)
                continue
            last = resolved[-1]
            if (trig.abs_time_s - last.abs_time_s) < COOLDOWN:
                # If the new trigger has strictly higher priority, replace
                if trig.priority > last.priority:
                    resolved[-1] = trig
            else:
                resolved.append(trig)

        # Map to SFXPlacement with volume scaling
        placements: List[SFXPlacement] = []
        for trig in resolved:
            vol = SFX_VOLUME.get(trig.event, -10)
            vol_adj = int(vol + trig.volume_offset)
            placements.append(SFXPlacement(
                event=trig.event,
                abs_time_s=trig.abs_time_s,
                volume_db=vol_adj,
                source=trig.source,
            ))

        return placements

    def _sfx_offset_within_scene(self, event: SFXEvent, scene: SceneDef) -> float:
        """
        Returns seconds offset from scene start to place an SFX.
        Different events should land at contextually appropriate moments.
        """
        if event == SFXEvent.SNAP:
            return 0.0    # opening snap at scene start
        elif event == SFXEvent.SUSPENSE:
            # Place suspense riser partway through problem scenes
            if scene.sub_cues:
                # At the last sub-cue start
                return scene.sub_cues[-1].start
            return 0.5
        elif event in (SFXEvent.WHOOSH, SFXEvent.SWIPE):
            return 0.1    # transition whoosh near start
        elif event == SFXEvent.DING:
            # Proof/solution reveal — place at first cue
            return scene.sub_cues[0].start if scene.sub_cues else 0.0
        elif event == SFXEvent.POP:
            return 0.0    # shock reaction at start
        elif event == SFXEvent.CLICK:
            # CTA — near the offer mention
            if len(scene.sub_cues) >= 2:
                return scene.sub_cues[1].start
            return 1.0
        elif event == SFXEvent.IMPACT:
            return 0.05
        return 0.0

    def apply_to_audio(
        self,
        mix_audio,  # pydub AudioSegment
        placements: List[SFXPlacement],
    ):
        """
        Apply SFX placements to a pydub AudioSegment.
        Returns the modified AudioSegment.
        """
        from pydub import AudioSegment as AS
        for p in placements:
            path = self.find_sfx(p.event)
            if not path or not os.path.exists(path):
                continue
            try:
                max_len = SFX_MAX_LEN.get(p.event, 1500)
                sfx_seg = AS.from_file(path)[:max_len] + p.volume_db
                pos_ms = int(p.abs_time_s * 1000)
                mix_audio = mix_audio.overlay(sfx_seg, position=pos_ms)
            except Exception as e:
                print(f"   [SFX Warning] {p.event.value} at {p.abs_time_s:.2f}s: {e}")
        return mix_audio
