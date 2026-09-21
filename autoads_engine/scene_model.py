"""
scene_model.py — Scene data structures and purpose-based defaults
=================================================================
Extends the existing v9 scene_defs dict format with semantic metadata:
  purpose, emotion, intensity, camera, transition, sfx events.

Backward compatible: existing dicts without these keys get sensible defaults.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ScenePurpose(str, Enum):
    """Narrative function of a scene in the ad structure."""
    HOOK        = "hook"        # Opening attention grab
    PROBLEM     = "problem"     # Pain point statement
    AGITATION   = "agitation"   # Amplify the problem
    SOLUTION    = "solution"    # Introduce the solution
    PRODUCT     = "product"     # Product reveal
    PROOF       = "proof"       # Before/After, testimonial
    BENEFIT     = "benefit"     # Result, benefit statement
    OFFER       = "offer"       # Price, promotion
    CTA         = "cta"         # Call to action


class SceneEmotion(str, Enum):
    """Emotional tone of the scene."""
    CONFIDENT   = "confident"
    FRUSTRATED  = "frustrated"
    SHOCKED     = "shocked"
    WARM        = "warm"
    URGENT      = "urgent"
    CURIOUS     = "curious"
    HAPPY       = "happy"
    NEUTRAL     = "neutral"


class CameraMotion(str, Enum):
    """Camera movement types. Maps to FFmpeg filter expressions."""
    STATIC          = "static"
    SLOW_ZOOM_IN    = "slow_zoom_in"    # 0.04*t — gentle, subtle
    PUSH_IN         = "push_in"         # 0.08*t — forward momentum
    PULL_OUT        = "pull_out"        # reverse zoom, reveal
    PUNCH_ZOOM      = "punch_zoom"      # fast ramp to 1.25 then ease
    PAN_LEFT        = "pan_left"
    PAN_RIGHT       = "pan_right"
    MICRO_SHAKE     = "micro_shake"     # ±4px sinusoidal shake
    FAST_PUSH       = "fast_push"       # 0.12*t — hook energy


class TransitionType(str, Enum):
    """Cut transition style applied at the start of a cut."""
    HARD_CUT    = "hard_cut"    # No filter — clean edit
    FLASH       = "flash"       # 0.08s white fade-in
    WHITE_FLASH = "white_flash" # 0.15s white fade-in (stronger)
    ZOOM_CUT    = "zoom_cut"    # Push zoom at cut point
    BLUR_IN     = "blur_in"     # Gaussian blur dissolve
    FADE        = "fade"        # Black fade-in 0.25s


class SFXEvent(str, Enum):
    """Named SFX events — mapped to actual SFX file keywords in sfx_engine."""
    SNAP        = "snap"
    POP         = "pop"
    WHOOSH      = "whoosh"
    SWIPE       = "swipe"
    IMPACT      = "impact"
    CLICK       = "click"
    DING        = "ding"
    SUSPENSE    = "suspense"
    RISING      = "rising"


class CaptionAnimStyle(str, Enum):
    """ASS subtitle animation preset names."""
    POP         = "pop"         # Standard CapCut spring pop
    PUNCH       = "punch"       # Bigger overshoot — emphasis words
    BOUNCE      = "bounce"      # Multi-stage elastic bounce
    SLIDE_UP    = "slide_up"    # Slide from below
    SLIDE_DOWN  = "slide_down"  # Slide from above
    SHAKE       = "shake"       # Horizontal shake — agitation
    NUMBER_POP  = "number_pop"  # Large scale pop for numbers/stats
    SCALE_IN    = "scale_in"    # Simple scale 0→1
    FADE_IN     = "fade_in"     # Alpha fade
    NONE        = "none"        # Static, no animation


class VFXCategory(str, Enum):
    """Visual effect overlay category."""
    NONE    = "none"
    BEAUTY  = "beauty"    # Radiance glow, porcelain shine, glimmer stars
    INFO    = "info"      # Measurement crosshair, micro scan lines, clinical markers
    IMPACT  = "impact"    # Chromatic flash pulse, camera micro-shake, shockwave
    PRODUCT = "product"   # Specular light sweep, ring spotlight


# ---------------------------------------------------------------------------
# Purpose → Default mappings (canonical editorial decisions)
# ---------------------------------------------------------------------------

PURPOSE_CAMERA: Dict[ScenePurpose, CameraMotion] = {
    ScenePurpose.HOOK:       CameraMotion.FAST_PUSH,
    ScenePurpose.PROBLEM:    CameraMotion.SLOW_ZOOM_IN,
    ScenePurpose.AGITATION:  CameraMotion.PUNCH_ZOOM,
    ScenePurpose.SOLUTION:   CameraMotion.PUSH_IN,
    ScenePurpose.PRODUCT:    CameraMotion.PUSH_IN,
    ScenePurpose.PROOF:      CameraMotion.SLOW_ZOOM_IN,
    ScenePurpose.BENEFIT:    CameraMotion.PUSH_IN,
    ScenePurpose.OFFER:      CameraMotion.PUSH_IN,
    ScenePurpose.CTA:        CameraMotion.FAST_PUSH,
}

PURPOSE_TRANSITION: Dict[ScenePurpose, TransitionType] = {
    ScenePurpose.HOOK:       TransitionType.FLASH,
    ScenePurpose.PROBLEM:    TransitionType.HARD_CUT,
    ScenePurpose.AGITATION:  TransitionType.FLASH,
    ScenePurpose.SOLUTION:   TransitionType.ZOOM_CUT,
    ScenePurpose.PRODUCT:    TransitionType.WHITE_FLASH,
    ScenePurpose.PROOF:      TransitionType.WHITE_FLASH,
    ScenePurpose.BENEFIT:    TransitionType.FLASH,
    ScenePurpose.OFFER:      TransitionType.FLASH,
    ScenePurpose.CTA:        TransitionType.FLASH,
}

PURPOSE_CAPTION_ANIM: Dict[ScenePurpose, CaptionAnimStyle] = {
    ScenePurpose.HOOK:       CaptionAnimStyle.PUNCH,
    ScenePurpose.PROBLEM:    CaptionAnimStyle.POP,
    ScenePurpose.AGITATION:  CaptionAnimStyle.SHAKE,
    ScenePurpose.SOLUTION:   CaptionAnimStyle.POP,
    ScenePurpose.PRODUCT:    CaptionAnimStyle.PUNCH,
    ScenePurpose.PROOF:      CaptionAnimStyle.BOUNCE,
    ScenePurpose.BENEFIT:    CaptionAnimStyle.POP,
    ScenePurpose.OFFER:      CaptionAnimStyle.NUMBER_POP,
    ScenePurpose.CTA:        CaptionAnimStyle.PUNCH,
}

PURPOSE_SFX: Dict[ScenePurpose, List[SFXEvent]] = {
    ScenePurpose.HOOK:       [SFXEvent.SNAP],
    ScenePurpose.PROBLEM:    [],
    ScenePurpose.AGITATION:  [SFXEvent.SUSPENSE],
    ScenePurpose.SOLUTION:   [SFXEvent.WHOOSH],
    ScenePurpose.PRODUCT:    [SFXEvent.IMPACT],
    ScenePurpose.PROOF:      [SFXEvent.DING],
    ScenePurpose.BENEFIT:    [],
    ScenePurpose.OFFER:      [SFXEvent.POP],
    ScenePurpose.CTA:        [SFXEvent.CLICK],
}

PURPOSE_INTENSITY: Dict[ScenePurpose, float] = {
    ScenePurpose.HOOK:       1.0,
    ScenePurpose.PROBLEM:    0.6,
    ScenePurpose.AGITATION:  0.8,
    ScenePurpose.SOLUTION:   0.8,
    ScenePurpose.PRODUCT:    0.9,
    ScenePurpose.PROOF:      0.7,
    ScenePurpose.BENEFIT:    0.7,
    ScenePurpose.OFFER:      0.9,
    ScenePurpose.CTA:        1.0,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SubCue:
    """A single subtitle cue within a scene."""
    start: float            # seconds relative to scene start
    end: float              # seconds relative to scene start
    text: str               # raw text (no ASS tags)
    display: str = ""       # pre-built ASS inline-tagged text (v9 compat)
    anim: Optional[CaptionAnimStyle] = None   # None = auto inferred from keywords/scene
    keywords: List[str] = field(default_factory=list)  # highlight words

    def __post_init__(self):
        # If display is pre-set (v9 compat), keep it as-is
        if not self.display:
            self.display = self.text

    @property
    def has_anim_override(self) -> bool:
        return self.anim is not None


@dataclass
class CutDef:
    """A single video cut within a scene."""
    name: str
    asset: str = ""                 # path to video/image file
    start: float = 0.0              # seek position in source
    dur: float = 2.0                # duration to use

    # v9 legacy flags (preserved for compatibility)
    zoom: bool = False
    sparkles: bool = False
    flash: bool = False
    hflip: bool = False
    is_split: bool = False          # Side-by-side split chunk
    is_dazzle: bool = False         # Dazzling bloom chunk

    # v10 enhanced fields (applied by engine if set)
    camera: Optional[CameraMotion] = None          # overrides scene default
    camera_intensity: Optional[float] = None       # 0.0~1.0 scale factor
    transition_in: Optional[TransitionType] = None # overrides scene default
    vfx: Optional[VFXCategory] = None              # beauty / info / impact / product
    extra_filters: List[str] = field(default_factory=list)  # raw ffmpeg filters


@dataclass
class SceneDef:
    """
    One scene in the ad. Wraps the v9 dict format.
    Extra fields are applied by the engine; missing fields get defaults
    derived from 'purpose'.
    """
    id: int
    audio: str
    cuts: List[CutDef]
    sub_cues: List[SubCue]

    # Semantic metadata (v10 new)
    purpose: ScenePurpose = ScenePurpose.BENEFIT
    emotion: SceneEmotion = SceneEmotion.NEUTRAL
    intensity: Optional[float] = None   # None → derived from purpose

    # Overrides (None → derived from purpose)
    default_camera: Optional[CameraMotion] = None
    default_transition: Optional[TransitionType] = None
    default_caption_anim: Optional[CaptionAnimStyle] = None
    sfx_events: Optional[List[SFXEvent]] = None

    def effective_intensity(self) -> float:
        if self.intensity is not None:
            return self.intensity
        return PURPOSE_INTENSITY.get(self.purpose, 0.7)

    def effective_camera(self) -> CameraMotion:
        if self.default_camera is not None:
            return self.default_camera
        return PURPOSE_CAMERA.get(self.purpose, CameraMotion.SLOW_ZOOM_IN)

    def effective_transition(self) -> TransitionType:
        if self.default_transition is not None:
            return self.default_transition
        return PURPOSE_TRANSITION.get(self.purpose, TransitionType.HARD_CUT)

    def effective_caption_anim(self) -> CaptionAnimStyle:
        if self.default_caption_anim is not None:
            return self.default_caption_anim
        return PURPOSE_CAPTION_ANIM.get(self.purpose, CaptionAnimStyle.POP)

    def effective_sfx(self) -> List[SFXEvent]:
        if self.sfx_events is not None:
            return self.sfx_events
        return PURPOSE_SFX.get(self.purpose, [])


# ---------------------------------------------------------------------------
# v9 dict → SceneDef converter (backward compat bridge)
# ---------------------------------------------------------------------------

def _cut_from_dict(c: Dict[str, Any]) -> CutDef:
    """Convert a v9 cut dict to CutDef dataclass."""
    vfx_val = None
    if "vfx" in c:
        try:
            vfx_val = VFXCategory(c["vfx"])
        except ValueError:
            vfx_val = None
    elif c.get("sparkles", False):
        vfx_val = VFXCategory.BEAUTY

    return CutDef(
        name=c.get("name", ""),
        asset=c.get("asset", ""),
        start=c.get("start", 0.0),
        dur=c.get("dur", 2.0),
        zoom=c.get("zoom", False),
        sparkles=c.get("sparkles", False),
        flash=c.get("flash", False),
        hflip=c.get("hflip", False),
        is_split=c.get("is_split", False),
        is_dazzle=c.get("is_dazzle", False),
        camera=CameraMotion(c["camera"]) if "camera" in c else None,
        camera_intensity=c.get("camera_intensity"),
        transition_in=TransitionType(c["transition_in"]) if "transition_in" in c else None,
        vfx=vfx_val,
        extra_filters=c.get("extra_filters", []),
    )


def _subcue_from_dict(q: Dict[str, Any]) -> SubCue:
    """Convert a v9 sub_cue dict to SubCue dataclass."""
    anim_style = None
    if "anim" in q:
        try:
            anim_style = CaptionAnimStyle(q["anim"])
        except ValueError:
            anim_style = None

    return SubCue(
        start=q["start"],
        end=q["end"],
        text=q.get("text", ""),
        display=q.get("display", q.get("text", "")),
        anim=anim_style,
        keywords=q.get("keywords", []),
    )


def from_dict(d: Dict[str, Any]) -> SceneDef:
    """
    Convert a v9-style scene dict to SceneDef.
    Any extra fields added in v10 dicts are also picked up.
    """
    cuts = [_cut_from_dict(c) for c in d.get("cuts", [])]
    sub_cues = [_subcue_from_dict(q) for q in d.get("sub_cues", [])]

    return SceneDef(
        id=d["id"],
        audio=d["audio"],
        cuts=cuts,
        sub_cues=sub_cues,
        purpose=ScenePurpose(d["purpose"]) if "purpose" in d else ScenePurpose.BENEFIT,
        emotion=SceneEmotion(d["emotion"]) if "emotion" in d else SceneEmotion.NEUTRAL,
        intensity=d.get("intensity"),
        default_camera=CameraMotion(d["camera"]) if "camera" in d else None,
        default_transition=TransitionType(d["transition"]) if "transition" in d else None,
        default_caption_anim=CaptionAnimStyle(d["caption_anim"]) if "caption_anim" in d else None,
        sfx_events=[SFXEvent(e) for e in d["sfx_events"]] if "sfx_events" in d else None,
    )


def enrich_scene_defs(scene_defs: List[Dict[str, Any]]) -> List[SceneDef]:
    """
    Convert a list of v9-style scene dicts to SceneDef objects.
    Missing 'purpose' fields → inferred from scene position heuristics.
    """
    scenes = []
    n = len(scene_defs)
    for i, d in enumerate(scene_defs):
        sd = from_dict(d)
        # If purpose not set, infer from position
        if "purpose" not in d:
            if i == 0:
                sd.purpose = ScenePurpose.HOOK
            elif i == n - 1:
                sd.purpose = ScenePurpose.CTA
            elif i <= 1:
                sd.purpose = ScenePurpose.PROBLEM
            elif i <= 3:
                sd.purpose = ScenePurpose.SOLUTION
            elif i <= 5:
                sd.purpose = ScenePurpose.PROOF
            elif i <= n - 2:
                sd.purpose = ScenePurpose.BENEFIT
        scenes.append(sd)
    return scenes
