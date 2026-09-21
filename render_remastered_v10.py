"""
Retiragen Master Commercial v10 — AutoAds Engine Integration
=============================================================
New in v10 vs v9:
  1. Scene Intelligence Layer:
     - Each scene has purpose/emotion/intensity fields.
     - Camera motion selected by purpose (push_in / punch_zoom / slow_zoom / static).
  2. Differentiated Camera Motion:
     - HOOK → fast_push (0.16x)
     - PROBLEM → slow_zoom (0.06x)
     - AGITATION → punch_zoom (fast ramp)
     - SOLUTION/PRODUCT → push_in (0.10x)
     - CTA → fast_push
  3. Caption Keyword Engine:
     - Detects numbers, impact words, positive words, product names, CTA words.
     - Applies different ASS animations: PUNCH vs POP vs SHAKE vs NUMBER_POP.
  4. Event-based SFX:
     - Replaces 6 hardcoded positions with purpose-driven automatic placement.
  5. Editing Intensity Arc:
     - Hook=1.0, Problem=0.6, Agitation=0.8, Solution=0.8, Proof=0.7, CTA=1.0.
  6. Preset System:
     - --preset meta_reels_fast / beauty_ads / ugc / aggressive_sales
  7. Seed support:
     - --seed 42 for deterministic variation in random elements
  8. Full backward compatibility:
     - All v9 chunk cache reuse logic preserved.
     - All v9 asset paths unchanged.

Run:
    python render_remastered_v10.py
    python render_remastered_v10.py --preset beauty_ads
    python render_remastered_v10.py --preset meta_reels_fast --seed 42
"""

import os
import sys
import json
import math
import shutil
import random
import argparse
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── AutoAds Engine imports ─────────────────────────────────────────────────
from autoads_engine.scene_model import (
    ScenePurpose, SceneEmotion, CameraMotion, TransitionType,
    CaptionAnimStyle, VFXCategory, SFXEvent, enrich_scene_defs, SceneDef
)
from autoads_engine.camera import CameraEngine
from autoads_engine.caption import CaptionEngine, KeywordDetector
from autoads_engine.transition import TransitionEngine
from autoads_engine.sfx_engine import SFXEngine
from autoads_engine.intensity import IntensityEngine
from autoads_engine.overlay import GraphicOverlayEngine, OverlayType, OverlaySpec
from autoads_engine.vfx import VFXEngine
from autoads_engine.presets import get_preset

# ── Paths (auto-resolving with v9 compatibility) ───────────────────────────
def _resolve_dir(primary: str, fallbacks: list[str]) -> str:
    try:
        if os.path.exists(primary):
            return primary
    except Exception:
        pass
    for fb in fallbacks:
        try:
            if os.path.exists(fb):
                return fb
        except Exception:
            pass
    for fb in fallbacks:
        try:
            os.makedirs(fb, exist_ok=True)
            return fb
        except Exception:
            pass
    return primary

_curr_dir = os.path.abspath(os.path.dirname(__file__))

WORKDIR = os.environ.get(
    "AUTOADS_WORKDIR",
    _resolve_dir(
        r"C:\Users\5700G\Desktop\레티라겐 레퍼런스",
        [r"C:\Users\임준모\Desktop\레티라겐 레퍼런스", os.path.join(_curr_dir, "build_output")]
    )
)
ROOT_DIR = _resolve_dir(
    r"C:\Users\5700G\Desktop\레티라겐",
    [r"C:\Users\임준모\Desktop\레티라겐", _curr_dir]
)
MODEL_DIR = _resolve_dir(
    r"C:\Users\5700G\Desktop\레티라겐\윤라영님모델_소스",
    [
        r"C:\Users\임준모\Desktop\레티라겐\윤라영님모델_소스",
        r"C:\Users\임준모\OneDrive\윤라영님_소스",
        ROOT_DIR,
    ]
)
XHS_DIR = _resolve_dir(
    r"C:\Users\5700G\Desktop\레티라겐\xhs_sources",
    [
        r"C:\adforge\storage\xhs_sources",
        r"C:\Users\임준모\Downloads\capcut-retiragen-v4\capcut-retiragen-v4\xhs_sources",
        ROOT_DIR,
    ]
)
SFX_DIR = _resolve_dir(
    r"C:\Users\5700G\Desktop\효과음",
    [
        r"C:\adforge\local_assets\sfx",
        r"C:\Users\임준모\Desktop\효과음",
    ]
)
AUDIO_12X_DIR = _resolve_dir(
    r"C:\adforge\temp_audio\retiragen_pore_1.2x",
    [
        r"C:\adforge\temp_audio",
        os.path.join(_curr_dir, "temp_audio"),
    ]
)
BUILD_DIR     = os.path.join(WORKDIR, "build_temp_v10")
CHUNK_DIR     = os.path.join(BUILD_DIR, "chunks")
SPARKLE_DIR   = os.path.join(BUILD_DIR, "sparkles")
SPLIT_DIR     = os.path.join(BUILD_DIR, "split_frames")
OVERLAY_DIR   = os.path.join(BUILD_DIR, "overlays")
try:
    os.makedirs(CHUNK_DIR,   exist_ok=True)
    os.makedirs(SPARKLE_DIR, exist_ok=True)
    os.makedirs(SPLIT_DIR,   exist_ok=True)
    os.makedirs(OVERLAY_DIR, exist_ok=True)
except Exception:
    pass

FONT_JALNAN = _resolve_dir(
    r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf",
    [
        r"C:\Users\임준모\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf",
        r"C:\Windows\Fonts\malgun.ttf",
    ]
)

W, H = 1080, 1920


# ── Utility helpers (reused from v9) ──────────────────────────────────────

def find_sfx(kw):
    for root, dirs, files in os.walk(SFX_DIR):
        for f in files:
            if kw.lower() in f.lower():
                return os.path.join(root, f)
    return None


def resolve_asset(path):
    if os.path.exists(path):
        return path
    dirname = os.path.dirname(path)
    base = os.path.basename(path)
    if os.path.exists(dirname):
        for f in os.listdir(dirname):
            if base[:15].lower() in f.lower():
                return os.path.join(dirname, f)
    return path


def ensure_sparkles():
    """Reuse existing sparkle frames from any previous version."""
    for version in ["v9", "v8", "v7", "v4"]:
        old = os.path.join(WORKDIR, f"build_temp_{version}", "sparkles")
        if os.path.exists(old) and len(os.listdir(old)) >= 90:
            for f in os.listdir(old):
                dst = os.path.join(SPARKLE_DIR, f)
                if not os.path.exists(dst):
                    shutil.copy2(os.path.join(old, f), dst)
            return
    if len(os.listdir(SPARKLE_DIR)) < 90:
        subprocess.run(["python", os.path.join(WORKDIR, "generate_sparkles.py")], check=True)


def render_split_chunk(out_chunk_path, duration=2.15):
    """Side-by-Side Dual Split Screen — reused from v9."""
    print(f">> Rendering Side-by-Side Dual Split Screen ({duration:.2f}s)...")
    FPS = 30
    total_frames = int(round(duration * FPS))
    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid  = resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"))
    f_tag = ImageFont.truetype(FONT_JALNAN, 36)

    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:02', '-t', str(duration), '-i', before_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0',
        '-r', '30', f'{SPLIT_DIR}/left_%03d.png'
    ], capture_output=True, check=True)
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:00', '-t', str(duration), '-i', after_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0',
        '-r', '30', f'{SPLIT_DIR}/right_%03d.png'
    ], capture_output=True, check=True)

    for f in range(total_frames):
        lp = f'{SPLIT_DIR}/left_{f+1:03d}.png'
        rp = f'{SPLIT_DIR}/right_{f+1:03d}.png'
        if not os.path.exists(lp) or not os.path.exists(rp):
            continue
        img_l = Image.open(lp).convert('RGBA')
        img_r = Image.open(rp).convert('RGBA')
        sp_idx = (f % 90) + 1
        sp_file = os.path.join(SPARKLE_DIR, f'sp_{sp_idx:03d}.png')
        if os.path.exists(sp_file):
            sp_img = Image.open(sp_file).convert('RGBA').crop((270, 0, 810, 1920))
            img_r = Image.alpha_composite(img_r, sp_img)
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        canvas.paste(img_l, (0, 0))
        canvas.paste(img_r, (540, 0))
        d = ImageDraw.Draw(canvas)
        d.line([(540, 0), (540, H)], fill=(255, 255, 255, 220), width=4)
        d.rounded_rectangle([195, 120, 345, 185], radius=16, fill=(40, 40, 50, 210), outline=(255, 100, 100, 240), width=2)
        d.text((270, 152), '비포', fill=(255, 120, 120), font=f_tag, anchor='mm')
        d.rounded_rectangle([735, 120, 885, 185], radius=16, fill=(245, 140, 190, 240), outline=(255, 255, 255, 255), width=2)
        d.text((810, 152), '애프터', fill=(255, 255, 255), font=f_tag, anchor='mm')
        canvas.convert('RGB').save(f'{SPLIT_DIR}/comp_{f:03d}.png')

    subprocess.run([
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{SPLIT_DIR}/comp_%03d.png',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        out_chunk_path
    ], check=True, capture_output=True)
    print(f">> Split chunk rendered: {out_chunk_path}")


# ── Scene definitions — v9 dicts + v10 purpose/emotion/intensity fields ───

def build_scene_defs():
    """
    V10 scene definitions: full v9 content + semantic metadata.
    'purpose' drives all engine decisions automatically.
    """
    return [
        # Scene 1 — HOOK: "전 피부과 프락셀 안 받아도 모공 요철 제로예요."
        {
            "id": 1,
            "purpose": "hook",
            "emotion": "confident",
            "intensity": 1.0,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_01.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.46, "text": "전 피부과 프락셀 안 받아도",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H00FFFFFF&}전 피부과 프락셀 안 받아도 {\\fnSegoe UI Emoji\\c&H8080FF&}🌸"},
                {"start": 1.46, "end": 2.677, "text": "모공 요철 제로예요",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H00FFFFFF&}모공 요철 {\\c&H0000E5FF&}제로{\\c&H00FFFFFF&}예요! {\\fnSegoe UI Emoji\\c&H00FFFF&}✨",
                 "anim": "punch"},
            ],
            "cuts": [
                {"name": "01_greeting_smile_hook",
                 "asset": os.path.join(MODEL_DIR, "환하게 인사하는 장면 - Trim.mp4"),
                 "start": 0.0, "dur": 2.677,
                 "zoom": True, "sparkles": True, "flash": False,
                 "camera": "fast_push", "transition_in": "flash",
                 "vfx": "beauty",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.BURST,
                     start_time=0.2, end_time=1.8,
                     position=(880, 360), size=(180, 180),
                     color=(255, 230, 0, 240)
                 )},
            ]
        },
        # Scene 2 — PROBLEM: "유명한 모공 앰플, 레티놀 크림 다 써봐도 개기름 뜨고 화장 밀리고,"
        {
            "id": 2,
            "purpose": "problem",
            "emotion": "frustrated",
            "intensity": 0.65,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_02.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.00, "text": "유명한 모공 앰플,",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}유명한 모공 앰플,"},
                {"start": 1.00, "end": 2.20, "text": "레티놀 크림 다 써봐도",
                 "display": "{\\fnSegoe UI Emoji\\c&H80FFFF&}💧 {\\fnJalnan 2\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&} 다 써봐도"},
                {"start": 2.20, "end": 3.664, "text": "개기름 뜨고 화장 밀리고",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}개기름 뜨고 {\\c&H0000E5FF&}화장 밀리고... {\\fnSegoe UI Emoji\\c&H80FFFF&}💦",
                 "anim": "shake"},
            ],
            "cuts": [
                {"name": "02_mirror_cream",
                 "asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"),
                 "start": 0.5, "dur": 1.800,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "slow_zoom_in", "transition_in": "flash"},
                {"name": "03_xhs_real_sebum_shine",
                 "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\17.mp4"),
                 "start": 1.5, "dur": 1.864,
                 "zoom": True, "sparkles": False, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.X,
                     start_time=0.2, end_time=1.6,
                     position=(820, 520), size=(160, 160),
                     color=(255, 45, 45, 240), line_width=12
                 )},
            ]
        },
        # Scene 3 — AGITATION: "심할 땐 피부가 아예 뒤집어지더라고요. 결국 나비존 요철만 푹 파였죠"
        {
            "id": 3,
            "purpose": "agitation",
            "emotion": "frustrated",
            "intensity": 0.85,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_03.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 0.75, "text": "심할 땐 피부가",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}심할 땐 피부가"},
                {"start": 0.75, "end": 1.64, "text": "아예 뒤집어지더라고요",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}아예 {\\c&H0000E5FF&}뒤집어지더라고요! {\\fnSegoe UI Emoji\\c&H5050FF&}💥",
                 "anim": "shake"},
                {"start": 1.64, "end": 2.65, "text": "결국 나비존 요철만",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}결국 나비존 요철만"},
                {"start": 2.65, "end": 3.457, "text": "푹 파였죠",
                 "display": "{\\fnSegoe UI Emoji\\c&H0050FF&}🚨 {\\fnJalnan 2\\c&H0000E5FF&}푹 파였죠! {\\fnSegoe UI Emoji\\c&H0050FF&}🚨",
                 "anim": "punch"},
            ],
            "cuts": [
                {"name": "04_frustrated_face",
                 "asset": os.path.join(MODEL_DIR, "답답해 - Trim.mp4"),
                 "start": 0.2, "dur": 1.650,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "punch_zoom", "transition_in": "flash"},
                {"name": "05_pore_crater_macro",
                 "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"),
                 "start": 1.0, "dur": 1.807,
                 "zoom": True, "sparkles": False, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut",
                 "vfx": "impact",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.CIRCLE,
                     start_time=0.3, end_time=1.6,
                     position=(540, 920), size=(320, 320),
                     color=(255, 60, 60, 220), line_width=8
                 )},
            ]
        },
        # Scene 4 — PROOF: Split Before/After + "근데 귤껍질 같던 볼살 매끈해진 거 보이세요?"
        {
            "id": 4,
            "purpose": "proof",
            "emotion": "warm",
            "intensity": 0.9,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_04.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.20, "text": "귤껍질 같던 볼살",
                 "display": "{\\fnSegoe UI Emoji\\c&H00A0FF&}🍊 {\\fnJalnan 2\\c&H00FFFFFF&}귤껍질 같던 볼살"},
                {"start": 1.20, "end": 2.15, "text": "매끈해진 거 보이세요",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H0000E5FF&}매끈해진 거{\\c&H00FFFFFF&} 보이세요?",
                 "anim": "bounce"},
                {"start": 2.15, "end": 3.10, "text": "전 레티놀 크림을",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}전 {\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&}을"},
                {"start": 3.10, "end": 4.084, "text": "삼키기 시작했어요",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}💊 {\\fnJalnan 2\\c&H0000E5FF&}삼키기 시작했어요! {\\fnSegoe UI Emoji\\c&H8080FF&}💊",
                 "anim": "punch"},
            ],
            "cuts": [
                {"name": "06_side_by_side_split",
                 "is_split": True,
                 "dur": 2.150},
                {"name": "07_pill_in_palm",
                 "asset": os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4"),
                 "start": 0.3, "dur": 1.934,
                 "zoom": True, "sparkles": False, "flash": False,
                 "camera": "push_in", "transition_in": "zoom_cut"},
            ]
        },
        # Scene 5 — AGITATION: "엥? 레티놀 크림을 삼켜요?"
        {
            "id": 5,
            "purpose": "agitation",
            "emotion": "shocked",
            "intensity": 1.0,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_05.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.582, "text": "엥?! 레티놀 크림을 삼켜요?!",
                 "display": "{\\fnSegoe UI Emoji\\c&H00E5FF&}⚡ {\\fnJalnan 2\\c&H0000E5FF&}엥?!{\\c&H00FFFFFF&} 레티놀 크림을 삼켜요?! {\\fnSegoe UI Emoji\\c&H00E5FF&}⚡",
                 "anim": "punch"},
            ],
            "cuts": [
                {"name": "08_shocked_phone_zoom",
                 "asset": os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4"),
                 "start": 0.5, "dur": 1.582,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "punch_zoom", "transition_in": "flash"},
            ]
        },
        # Scene 6 — SOLUTION: "땡볕 야구장을 다녀와도 피지가 터지기는커녕 요철이 팽팽하게 차오르는 거예요"
        {
            "id": 6,
            "purpose": "solution",
            "emotion": "warm",
            "intensity": 0.8,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_06.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.10, "text": "저도 처음엔 안 믿었는데,",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}저도 처음엔 안 믿었는데,"},
                {"start": 1.10, "end": 2.40, "text": "땡볕 야구장을 다녀와도",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}☀️ {\\fnJalnan 2\\c&H0000E5FF&}땡볕 야구장{\\c&H00FFFFFF&}을 다녀와도"},
                {"start": 2.40, "end": 3.50, "text": "피지가 터지기는커녕",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}피지가 터지기는커녕",
                 "anim": "shake"},
                {"start": 3.50, "end": 4.60, "text": "요철이 점점 더",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}요철이 점점 더"},
                {"start": 4.60, "end": 5.916, "text": "팽팽하게 차오르는 거예요",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}💖 {\\fnJalnan 2\\c&H0000E5FF&}팽팽하게 차오르는 거예요! {\\fnSegoe UI Emoji\\c&H8080FF&}💖",
                 "anim": "bounce"},
            ],
            "cuts": [
                {"name": "09_hesitant_face",
                 "asset": os.path.join(MODEL_DIR, "고민.mp4"),
                 "start": 0.5, "dur": 1.200,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "slow_zoom_in", "transition_in": "flash"},
                {"name": "10_sunny_heat_shielding",
                 "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\12.mp4"),
                 "start": 0.5, "dur": 2.300,
                 "zoom": True, "sparkles": False, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut"},
                {"name": "11_plump_glass_skin_after",
                 "asset": os.path.join(ROOT_DIR, "여드름 애프터 2.mp4"),
                 "start": 0.5, "dur": 2.416,
                 "zoom": True, "sparkles": True, "flash": True,
                 "camera": "push_in", "transition_in": "white_flash",
                 "vfx": "beauty",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.CHECK,
                     start_time=0.2, end_time=2.0,
                     position=(840, 460), size=(150, 150),
                     color=(0, 235, 140, 245), line_width=12
                 )},
            ]
        },
        # Scene 7 — BENEFIT: "한 달 꾸준히 먹어보니 이젠 프라이머 없이도 매끈한 17호 피부"
        {
            "id": 7,
            "purpose": "benefit",
            "emotion": "happy",
            "intensity": 0.75,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_07.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.46, "text": "한 달 정도 꾸준히 먹어보니,",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H00FFFFFF&}한 달 정도 꾸준히 먹어보니,",
                 "anim": "number_pop"},
                {"start": 1.46, "end": 2.50, "text": "이젠 프라이머 없이도",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}이젠 프라이머 없이도"},
                {"start": 2.50, "end": 4.040, "text": "매끈한 17호 피부가 됐어요",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌷 {\\fnJalnan 2\\c&H0000E5FF&}매끈한 17호 피부{\\c&H00FFFFFF&}가 됐어요!",
                 "anim": "bounce"},
            ],
            "cuts": [
                {"name": "12_taking_pill",
                 "asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"),
                 "start": 2.0, "dur": 1.600,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "push_in", "transition_in": "flash"},
                {"name": "13_shade17_skin_closeup2",
                 "asset": os.path.join(MODEL_DIR, "피부 클로즈업2 - Trim.mp4"),
                 "start": 0.0, "dur": 2.440,
                 "zoom": True, "sparkles": True, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut",
                 "vfx": "beauty"},
            ]
        },
        # Scene 8 — PRODUCT: Mechanism explanation + "피부과 프락셀 레이저가 이식된 느낌"
        {
            "id": 8,
            "purpose": "product",
            "emotion": "curious",
            "intensity": 0.8,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_08.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.00, "text": "알고 보니 속피지선부터",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}알고 보니 속피지선부터"},
                {"start": 1.00, "end": 2.02, "text": "바짝 말려주고",
                 "display": "{\\fnSegoe UI Emoji\\c&H00E5FF&}🔬 {\\fnJalnan 2\\c&H0000E5FF&}바짝 말려주고! {\\fnSegoe UI Emoji\\c&H00E5FF&}🔬",
                 "anim": "punch"},
                {"start": 2.02, "end": 3.20, "text": "진피 속엔 초저분자 콜라겐",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}진피 속엔 초저분자 콜라겐"},
                {"start": 3.20, "end": 4.42, "text": "가득 메워주는 원리",
                 "display": "{\\fnSegoe UI Emoji\\c&H80FFFF&}🧬 {\\fnJalnan 2\\c&H0000E5FF&}가득 메워주는 원리! {\\fnSegoe UI Emoji\\c&H80FFFF&}🧬",
                 "anim": "bounce"},
                {"start": 4.42, "end": 5.70, "text": "와, 피부과 프락셀 레이저가",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}와, 피부과 프락셀 레이저가"},
                {"start": 5.70, "end": 7.499, "text": "피부 자체에 이식된 느낌",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}💎 {\\fnJalnan 2\\c&H0000E5FF&}피부 자체에 이식된 느낌?! {\\fnSegoe UI Emoji\\c&H00FFFF&}💎",
                 "anim": "punch"},
            ],
            "cuts": [
                {"name": "14_sebum_dry_3d",
                 "asset": os.path.join(MODEL_DIR, "피지,모낭 없애는.mp4"),
                 "start": 0.5, "dur": 2.000,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "push_in", "transition_in": "flash",
                 "vfx": "info",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.BADGE,
                     start_time=0.2, end_time=1.8,
                     position=(540, 320), size=(380, 68),
                     text="속피지선 집중 케어",
                     color=(25, 30, 45, 230), outline_color=(0, 230, 255, 255)
                 )},
                {"name": "15_collagen_mesh_3d",
                 "asset": os.path.join(ROOT_DIR, "새살 차오르기 2.mp4"),
                 "start": 1.0, "dur": 2.000,
                 "zoom": True, "sparkles": True, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut",
                 "vfx": "beauty"},
                {"name": "16_laser_clinic",
                 "asset": os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4"),
                 "start": 0.5, "dur": 1.600,
                 "zoom": True, "sparkles": False, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut"},
                {"name": "17_cheek_touch_macro",
                 "asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"),
                 "start": 0.5, "dur": 1.899,
                 "zoom": True, "sparkles": True, "flash": False,
                 "camera": "push_in", "transition_in": "hard_cut",
                 "vfx": "beauty"},
            ]
        },
        # Scene 9 — BENEFIT: "하루 종일 자연광 맞아도 매끈한 깐달걀 피부 톤이 쭈욱 유지돼요"
        {
            "id": 9,
            "purpose": "benefit",
            "emotion": "happy",
            "intensity": 0.85,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_09.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.15, "text": "하루 종일 자연광 맞아도",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}☀️ {\\fnJalnan 2\\c&H00FFFFFF&}하루 종일 자연광 맞아도"},
                {"start": 1.15, "end": 2.35, "text": "매끈한 깐달걀 피부 톤이",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H0000E5FF&}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&}이",
                 "anim": "bounce"},
                {"start": 2.35, "end": 3.173, "text": "쭈욱 유지돼요",
                 "display": "{\\fnJalnan 2\\c&H0000E5FF&}쭈욱 유지돼요! {\\fnSegoe UI Emoji\\c&H00FFFF&}✨",
                 "anim": "pop"},
            ],
            "cuts": [
                {"name": "18_daylight_laughter",
                 "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                 "start": 0.5, "dur": 1.400,
                 "zoom": True, "sparkles": True, "flash": True,
                 "camera": "push_in", "transition_in": "flash",
                 "vfx": "beauty"},
                {"name": "19_confident_thumbs_up",
                 "asset": os.path.join(MODEL_DIR, "따봉.mp4"),
                 "start": 0.5, "dur": 1.773,
                 "zoom": True, "sparkles": True, "flash": False,
                 "camera": "push_in", "transition_in": "hard_cut",
                 "vfx": "beauty"},
            ]
        },
        # Scene 10 — OFFER+CTA: "30일 기간 한정 반값 할인 / 아래 비밀링크"
        {
            "id": 10,
            "purpose": "cta",
            "emotion": "urgent",
            "intensity": 1.0,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_10.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 0.85, "text": "30일 기간 한정",
                 "display": "{\\fnJalnan 2\\c&H00FFFFFF&}30일 기간 한정",
                 "anim": "number_pop"},
                {"start": 0.85, "end": 1.92, "text": "반값 할인 중",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🎉 {\\fnJalnan 2\\c&H0000E5FF&}반값 할인 중! {\\fnSegoe UI Emoji\\c&H00FFFF&}🎉",
                 "anim": "punch"},
                {"start": 1.92, "end": 2.80, "text": "궁금한 분들은",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🤫 {\\fnJalnan 2\\c&H00FFFFFF&}궁금한 분들은"},
                {"start": 2.80, "end": 4.263, "text": "아래 비밀링크 참고해 보세요",
                 "display": "{\\fnSegoe UI Emoji\\c&H8080FF&}💖 {\\fnJalnan 2\\c&H0000E5FF&}아래 비밀링크{\\c&H00FFFFFF&} 참고해 보세요~",
                 "anim": "pop"},
                {"start": 4.263, "end": 5.463, "text": "지금 링크에서 확인하세요",
                 "display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}👆 {\\fnJalnan 2\\c&H0000E5FF&}지금 링크에서 확인하세요! {\\fnSegoe UI Emoji\\c&H00FFFF&}👆",
                 "anim": "punch"},
            ],
            "cuts": [
                {"name": "20_product_box_model",
                 "asset": os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4"),
                 "start": 0.5, "dur": 1.800,
                 "hflip": True,
                 "zoom": True, "sparkles": False, "flash": True,
                 "camera": "fast_push", "transition_in": "flash",
                 "vfx": "product",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.BADGE,
                     start_time=0.2, end_time=1.8,
                     position=(540, 320), size=(440, 75),
                     text="30일 기간한정 50% 반값",
                     color=(235, 35, 35, 240), outline_color=(255, 255, 255, 255)
                 )},
                {"name": "21_secret_whisper",
                 "asset": os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4"),
                 "start": 0.5, "dur": 1.800,
                 "zoom": True, "sparkles": False, "flash": False,
                 "camera": "slow_zoom_in", "transition_in": "hard_cut"},
                {"name": "22_cta_pointing_down",
                 "asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"),
                 "start": 0.0, "dur": 1.863,
                 "zoom": False, "sparkles": False, "flash": False,
                 "camera": "static", "transition_in": "hard_cut",
                 "overlay": OverlaySpec(
                     overlay_type=OverlayType.ARROW,
                     start_time=0.2, end_time=1.8,
                     position=(540, 1380), size=(160, 220),
                     color=(255, 220, 0, 255), line_width=10, rotation=180.0
                 )},
            ]
        },
    ]


def build_chunk_filter(
    c: dict,
    scene_purpose: ScenePurpose,
    scene_intensity: float,
    cam_engine: CameraEngine,
    trans_engine: TransitionEngine,
    clip_dur: float,
    vfx_input_idx: Optional[int] = None,
    overlay_input_idx: Optional[int] = None,
    overlay_timing: Optional[Tuple[float, float]] = None,
) -> str:
    """
    Build the complete filter_complex string for a single cut.
    Handles Camera motion, categorized VFX overlay, Graphic overlay, and Transitions.
    """
    filter_chains = []
    curr_in = "0:v"

    # 1. hflip (v9 compat)
    if c.get("hflip", False):
        filter_chains.append(f"[{curr_in}]hflip[flipped]")
        curr_in = "flipped"

    # 2. Base scale + crop
    filter_chains.append(
        f"[{curr_in}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[scaled]"
    )

    # 3. Camera motion (v10 engine or v9 fallback)
    cam_motion_str = c.get("camera", None)
    if cam_motion_str and cam_motion_str != "static":
        try:
            cam_motion = CameraMotion(cam_motion_str)
        except ValueError:
            cam_motion = None
        if cam_motion:
            cam_filter = cam_engine.get_filter(
                cam_motion,
                scene_intensity=scene_intensity,
                clip_duration=clip_dur,
                input_label="scaled",
                output_label="cam_out",
            )
            filter_chains.append(cam_filter)
            curr_v = "[cam_out]"
        else:
            curr_v = "[scaled]"
    elif c.get("zoom", False):
        # v9 legacy fallback
        cam_filter = cam_engine.build_legacy_zoom_filter(
            zoom=True, input_label="scaled", output_label="cam_out", clip_dur=clip_dur
        )
        filter_chains.append(cam_filter)
        curr_v = "[cam_out]"
    else:
        curr_v = "[scaled]"

    # 4. VFX overlay (v10 categorized engine or v9 sparkles fallback)
    if vfx_input_idx is not None:
        filter_chains.append(f"[{vfx_input_idx}:v]fps=30[fx_in];{curr_v}[fx_in]overlay=0:0:shortest=1[vfx_out]")
        curr_v = "[vfx_out]"
    elif c.get("sparkles", False):
        filter_chains.append(f"[1:v]fps=30[sp];{curr_v}[sp]overlay=0:0:shortest=1[sparkled]")
        curr_v = "[sparkled]"

    # 5. Graphic overlay (PIL-rendered overlay asset)
    if overlay_input_idx is not None and overlay_timing is not None:
        st, et = overlay_timing
        filter_chains.append(
            f"[{overlay_input_idx}:v]fps=30[ov_in];"
            f"{curr_v}[ov_in]overlay=0:0:enable='between(t,{st:.3f},{et:.3f})'[ov_out]"
        )
        curr_v = "[ov_out]"

    # 6. Transition (v10 engine or v9 flash fallback)
    trans_str = c.get("transition_in", None)
    if trans_str and trans_str != "hard_cut":
        try:
            trans_type = TransitionType(trans_str)
        except ValueError:
            trans_type = None
        if trans_type:
            trans_filter = trans_engine.get_filter(
                trans_type,
                scene_intensity=scene_intensity,
                input_label=curr_v.strip("[]"),
                output_label="trans_out",
            )
            filter_chains.append(trans_filter)
            curr_v = "[trans_out]"
    elif c.get("flash", False):
        # v9 legacy fallback
        flash_out = curr_v.strip("[]") + "_f"
        filter_chains.append(f"{curr_v}fade=t=in:st=0:d=0.08:color=white[{flash_out}]")
        curr_v = f"[{flash_out}]"

    # 7. Final format
    filter_chains.append(f"{curr_v}fps=30,format=yuv420p[out]")
    return ";".join(filter_chains)


def main():
    parser = argparse.ArgumentParser(description="AutoAds v10 — Meta Reels Commercial Renderer")
    parser.add_argument("--preset", default="meta_reels_fast", help="Editing preset name")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for variation")
    parser.add_argument("--no-cache", action="store_true", help="Force re-render all chunks")
    parser.add_argument("--no-jev", action="store_true", default=True, help="Run baseline AutoAds v10 engine (no Jev API calls)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f">> Seed: {args.seed}")

    cfg = get_preset(args.preset)
    print("=" * 75)
    print(f">> AutoAds v10 — Preset: {args.preset} ({cfg['description']})")
    if args.no_jev:
        print(">> Editorial Engine: AutoAds v10 Baseline (--no-jev)")
    print("=" * 75)

    # Initialize engines
    cam_engine     = CameraEngine(intensity_scale=cfg["camera_intensity_scale"])
    cap_engine     = CaptionEngine(intensity_scale=cfg["caption_intensity_scale"])
    trans_engine   = TransitionEngine(intensity_scale=cfg["transition_intensity_scale"])
    sfx_engine     = SFXEngine(sfx_dir=SFX_DIR, intensity_scale=cfg["sfx_intensity_scale"])
    int_engine     = IntensityEngine(global_scale=cfg["global_intensity_scale"])
    vfx_engine     = VFXEngine(base_dir=BUILD_DIR)
    overlay_engine = GraphicOverlayEngine(font_path=FONT_JALNAN)

    ensure_sparkles()

    # Load and enrich scene definitions
    raw_defs = build_scene_defs()
    scenes: list[SceneDef] = enrich_scene_defs(raw_defs)
    intensity_params = int_engine.per_scene_params(scenes)

    print(f">> Processing {sum(len(s.cuts) for s in scenes)} unique video chunks...")
    all_chunks = []
    chunk_idx = 0

    # Cache from v9 (reuse unchanged chunks)
    v9_chunk_dir = os.path.join(WORKDIR, "build_temp_v9", "chunks")

    for s_idx, (scene, iparams) in enumerate(zip(scenes, intensity_params)):
        scene_intensity = iparams["intensity"]
        scene_purpose   = scene.purpose

        for c_idx, cut in enumerate(scene.cuts):
            chunk_idx += 1
            chunk_file = os.path.join(CHUNK_DIR, f"chunk_{chunk_idx:02d}.mp4")
            all_chunks.append(chunk_file)

            # Special: Side-by-Side Split
            if cut.is_split:
                if not os.path.exists(chunk_file) or os.path.getsize(chunk_file) == 0 or args.no_cache:
                    render_split_chunk(chunk_file, duration=cut.dur)
                else:
                    print(f"   ✓ Chunk {chunk_idx:02d}: {cut.name} (split, cached)")
                continue

            # Determine VFX Category
            cut_vfx: Optional[VFXCategory] = cut.vfx
            if not cut_vfx and cut.sparkles:
                cut_vfx = VFXCategory.BEAUTY

            # Determine Graphic Overlay
            cut_overlay: Optional[OverlaySpec] = cut.overlay

            # Prepare auxiliary inputs & indices
            next_input_idx = 1
            vfx_input_idx = None
            overlay_input_idx = None
            cmd_inputs = [
                "-ss", str(cut.start),
                "-t", str(cut.dur),
                "-i", resolve_asset(cut.asset)
            ]

            # Wire VFX frame sequence
            if cut_vfx and cut_vfx != VFXCategory.NONE:
                vfx_pattern = vfx_engine.get_pattern(cut_vfx)
                if vfx_pattern:
                    cmd_inputs.extend(["-stream_loop", "-1", "-r", "30", "-i", vfx_pattern])
                    vfx_input_idx = next_input_idx
                    next_input_idx += 1

            # Wire Graphic Overlay PNG asset
            overlay_timing = None
            if cut_overlay:
                overlay_img_path = os.path.join(OVERLAY_DIR, f"ov_{chunk_idx:02d}.png")
                ov_img = overlay_engine.render_overlay_image(cut_overlay, canvas_size=(W, H))
                ov_img.save(overlay_img_path)
                cmd_inputs.extend(["-loop", "1", "-t", str(cut.dur), "-i", overlay_img_path])
                overlay_input_idx = next_input_idx
                next_input_idx += 1
                overlay_timing = (cut_overlay.start_time, cut_overlay.end_time)

            # Build filter_complex with explicit input routing
            vf_str = build_chunk_filter(
                c={
                    "hflip": cut.hflip,
                    "zoom": cut.zoom,
                    "sparkles": cut.sparkles and (vfx_input_idx is None), # fallback only if no vfx sequence
                    "flash": cut.flash,
                    "camera": cut.camera.value if cut.camera else None,
                    "transition_in": cut.transition_in.value if cut.transition_in else None,
                },
                scene_purpose=scene_purpose,
                scene_intensity=scene_intensity,
                cam_engine=cam_engine,
                trans_engine=trans_engine,
                clip_dur=cut.dur,
                vfx_input_idx=vfx_input_idx,
                overlay_input_idx=overlay_input_idx,
                overlay_timing=overlay_timing,
            )

            # P0-3: Comprehensive Cache Signature (asset, timing, filter, preset, seed, vfx, overlay)
            cache_meta_file = os.path.join(CHUNK_DIR, f"chunk_{chunk_idx:02d}.meta.json")
            cache_sig = {
                "asset": str(cut.asset),
                "start": cut.start,
                "dur": cut.dur,
                "vf_str": vf_str,
                "preset": args.preset,
                "seed": args.seed,
                "vfx": cut_vfx.value if cut_vfx else None,
                "overlay": {
                    "type": cut_overlay.overlay_type.value,
                    "timing": [round(cut_overlay.start_time, 3), round(cut_overlay.end_time, 3)],
                    "pos": list(cut_overlay.position),
                    "size": list(cut_overlay.size),
                    "text": cut_overlay.text,
                } if cut_overlay else None,
            }
            cache_valid = False
            if (not args.no_cache
                    and os.path.exists(chunk_file)
                    and os.path.getsize(chunk_file) > 50000
                    and os.path.exists(cache_meta_file)):
                try:
                    with open(cache_meta_file, "r", encoding="utf-8") as mf:
                        saved_sig = json.load(mf)
                    if saved_sig == cache_sig:
                        cache_valid = True
                except Exception:
                    cache_valid = False

            if cache_valid:
                vfx_info = f", vfx={cut_vfx.value}" if cut_vfx else ""
                ov_info = f", ov={cut_overlay.overlay_type.value}" if cut_overlay else ""
                print(f"   ✓ Chunk {chunk_idx:02d}: {cut.name} (verified cache{vfx_info}{ov_info})")
                continue

            cmd = ["ffmpeg", "-y"] + cmd_inputs + [
                "-filter_complex", vf_str,
                "-map", "[out]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-an",
                chunk_file
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            try:
                with open(cache_meta_file, "w", encoding="utf-8") as mf:
                    json.dump(cache_sig, mf, ensure_ascii=False, indent=2)
            except Exception:
                pass

            vfx_tag = f" [vfx:{cut_vfx.value}]" if cut_vfx else ""
            ov_tag = f" [ov:{cut_overlay.overlay_type.value}]" if cut_overlay else ""
            print(f"   ✓ Chunk {chunk_idx:02d}: {cut.name} ({cut.dur:.3f}s, {scene_purpose.value}{vfx_tag}{ov_tag})")

    # Concatenate
    print(">> Concatenating chunks...")
    concat_list = os.path.join(BUILD_DIR, "chunks.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write("file '{}'\n".format(ch.replace("\\", "/")))

    raw_visual = os.path.join(BUILD_DIR, "raw_visual.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", raw_visual
    ], check=True, capture_output=True)

    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", raw_visual]
    total_video_dur = float(subprocess.check_output(cmd_dur).decode().strip())
    print(f">> Total Video Duration: {total_video_dur:.3f}s")

    # Build master audio
    print(">> Mixing Master Audio...")
    master_narr = AudioSegment.empty()
    scene_offsets = []
    curr_offset = 0.0

    for scene in scenes:
        scene_offsets.append(curr_offset)
        seg = AudioSegment.from_wav(scene.audio)
        master_narr += seg
        curr_offset += len(seg) / 1000.0

    total_master_ms = int(round(total_video_dur * 1000.0))

    bgm_path = find_sfx("Its Jazz full.wav") or find_sfx("Its Jazz 30 sec.wav")
    if not bgm_path:
        bgm_path = os.path.join(SFX_DIR, r"1_BGM(일상)\Its Jazz 30 sec.wav")
    bgm = AudioSegment.from_wav(bgm_path) + cfg["bgm_volume_db"]
    loop_bgm = AudioSegment.empty()
    while len(loop_bgm) < total_master_ms + 2000:
        loop_bgm += bgm
    loop_bgm = loop_bgm[:total_master_ms].fade_in(300).fade_out(1200)
    mix_audio = loop_bgm.overlay(master_narr)

    # SFX via engine
    if cfg.get("auto_sfx", True):
        placements = sfx_engine.compute_placements(scenes, scene_offsets)
        mix_audio = sfx_engine.apply_to_audio(mix_audio, placements)
        print(f">> Applied {len(placements)} SFX placements automatically.")

    master_audio_path = os.path.join(WORKDIR, "master_audio_v10.wav")
    mix_audio.export(master_audio_path, format="wav")
    print(f">> Master Audio: {master_audio_path}")

    # Generate subtitles with v10 engine
    print(">> Generating Subtitles (v10 Caption Engine)...")
    ass_path = os.path.join(WORKDIR, "subtitles_v10.ass")
    intensity_list = int_engine.compute(scenes)

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(cap_engine.ass_header(f"AutoAds v10 — {args.preset}"))

        for s_idx, (scene, scene_int) in enumerate(zip(scenes, intensity_list)):
            s_base = scene_offsets[s_idx]
            scene_anim = scene.effective_caption_anim()

            for cue in scene.sub_cues:
                abs_start = s_base + cue.start
                abs_end   = s_base + cue.end
                dur_ms    = (cue.end - cue.start) * 1000.0

                # Determine animation: explicit cue override > keyword analysis > scene default
                if cue.has_anim_override:
                    cue_anim = cue.anim
                else:
                    cue_anim = cap_engine.choose_anim(
                        raw_text=cue.text,
                        scene_purpose=scene.purpose,
                        fallback_anim=scene_anim,
                    )

                text_field = cap_engine.build_ass_text(
                    raw_text=cue.text,
                    display_text=cue.display,
                    anim=cue_anim,
                    duration_ms=dur_ms,
                    scene_intensity=scene_int,
                    scene_purpose=scene.purpose,
                    auto_keyword_color=cfg.get("keyword_highlight", True),
                )
                line = cap_engine.build_dialogue_line(abs_start, abs_end, text_field)
                f.write(line)

    print(f">> Subtitles: {ass_path}")

    # Final render
    print(">> Assembling Final Master Video...")
    final_mp4 = os.path.join(WORKDIR, f"retiragen_v10_{args.preset}.mp4")
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", raw_visual,
        "-i", master_audio_path,
        "-vf", f"subtitles='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        final_mp4
    ], check=True)
    print(f">> Final Video: {final_mp4}")

    # Tile sheet verification
    tile_sheet = os.path.join(WORKDIR, f"retiragen_hypit_tile16_v10_{args.preset}.jpg")
    print(">> Generating Verification Tile Sheet...")
    if os.path.exists(tile_sheet):
        os.remove(tile_sheet)
    cmd_tile = f'hypit media tile "{final_mp4}" --frames 16 --columns 4 --to "{tile_sheet}"'
    subprocess.run(cmd_tile, shell=True, check=True)
    print(f">> Tile Sheet: {tile_sheet}")

    # SVML update
    svml_content = (
        f'<composition width="{W}" height="{H}" fps="30" duration="{total_video_dur:.3f}s">\n'
        f'  <video src="{final_mp4.replace(chr(92), "/")}" in="0s" out="{total_video_dur:.3f}s" />\n'
        f'  <audio src="{master_audio_path.replace(chr(92), "/")}" in="0s" out="{total_video_dur:.3f}s" />\n'
        f'</composition>\n'
    )
    with open(os.path.join(WORKDIR, "main.svml"), "w", encoding="utf-8") as f:
        f.write(svml_content)

    print("=" * 75)
    print(f">> AutoAds v10 Complete! Preset: {args.preset}")
    print(f"   Video:  {final_mp4}")
    print(f"   Audio:  {master_audio_path}")
    print(f"   Subs:   {ass_path}")
    print("=" * 75)


if __name__ == "__main__":
    main()
