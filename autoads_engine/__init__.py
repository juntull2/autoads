"""
AutoAds Engine — High-quality Meta Reels Ad Editing Engine
==========================================================
Scene-aware automatic editing system that makes contextual decisions
about camera motion, caption animation, transitions, and SFX
based on each scene's purpose, emotion, and intensity.

Usage:
    from autoads_engine import SceneModel, CameraEngine, CaptionEngine
    from autoads_engine import TransitionEngine, SFXEngine, IntensityEngine
    from autoads_engine.presets import get_preset
"""

from autoads_engine.scene_model import (
    ScenePurpose, SceneEmotion, CameraMotion, TransitionType,
    SFXEvent, CaptionAnimStyle, VFXCategory, SceneDef, CutDef, SubCue,
    enrich_scene_defs
)
from autoads_engine.camera import CameraEngine
from autoads_engine.caption import CaptionEngine, KeywordDetector
from autoads_engine.transition import TransitionEngine
from autoads_engine.sfx_engine import SFXEngine
from autoads_engine.intensity import IntensityEngine
from autoads_engine.overlay import GraphicOverlayEngine, OverlayType, OverlaySpec
from autoads_engine.vfx import VFXEngine
from autoads_engine.presets import get_preset, list_presets
from autoads_engine.jev import JEVDecision, JevClient, JevPlanner, JevFallback

__version__ = "1.2.0"
__all__ = [
    "ScenePurpose", "SceneEmotion", "CameraMotion", "TransitionType",
    "SFXEvent", "CaptionAnimStyle", "VFXCategory", "SceneDef", "CutDef", "SubCue",
    "enrich_scene_defs",
    "CameraEngine", "CaptionEngine", "KeywordDetector",
    "TransitionEngine", "SFXEngine", "IntensityEngine",
    "GraphicOverlayEngine", "OverlayType", "OverlaySpec", "VFXEngine",
    "get_preset", "list_presets",
    "JEVDecision", "JevClient", "JevPlanner", "JevFallback",
]
