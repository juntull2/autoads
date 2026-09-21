"""
Retiragen Master Commercial v8:
1. Top theme capsule badges DELETED completely per user request ("상단 테마 캡슐 배지 삭제해").
   - Keeps only clean, floral & emoji-embellished animated dialogue subtitles at bottom (Jalnan 2 + Segoe UI Emoji).
2. Dazzling Blinding Light Transition ("눈부신 효과로 장면 전환") instead of Before/After text boxes:
   - Severe acne skin ➔ exponential radiant bloom flare ramp ➔ pure blinding white brilliance peak ➔ soft unveil to porcelain smooth skin with shimmering stars.
   - Zero "BEFORE" or "AFTER" text clutter!
3. 3D Repeated Scenes Completely Eliminated ("3d 부분에 똑같은 장면 반복 수정"):
   - Scene 6 Cut 11: 3D cellular skin plumping (새살 차오르기.mp4)
   - Scene 8 Cut 14: 3D sebum drying cross-section (피지,모낭 없애는.mp4)
   - Scene 8 Cut 15: 3D glowing white collagen matrix fibers weaving (새살 차오르기 2.mp4) - REPLACED duplicate!
   - Scene 8 Cut 16: Dermatology clinic green laser procedure
4. 1.2x Speech Speed with 1:1 Millisecond Sync & 1.05s Outro Hold (Zero Truncation).
"""

import os
import sys
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageEnhance
from pydub import AudioSegment

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
ROOT_DIR = r"C:\Users\5700G\Desktop\레티라겐"
MODEL_DIR = r"C:\Users\5700G\Desktop\레티라겐\윤라영님모델_소스"
XHS_DIR = r"C:\Users\5700G\Desktop\레티라겐\xhs_sources"
SFX_DIR = r"C:\Users\5700G\Desktop\효과음"
AUDIO_12X_DIR = r"C:\adforge\temp_audio\retiragen_pore_1.2x"
BUILD_DIR = os.path.join(WORKDIR, "build_temp_v8")
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks")
SPARKLE_DIR = os.path.join(BUILD_DIR, "sparkles")
DAZZLE_DIR = os.path.join(BUILD_DIR, "dazzle_frames")
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(SPARKLE_DIR, exist_ok=True)
os.makedirs(DAZZLE_DIR, exist_ok=True)

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

# Step 1: Ensure Sparkles are generated
def ensure_sparkles():
    old_sparkles = os.path.join(WORKDIR, "build_temp_v4", "sparkles")
    if os.path.exists(old_sparkles) and len(os.listdir(old_sparkles)) >= 90:
        for f in os.listdir(old_sparkles):
            src = os.path.join(old_sparkles, f)
            dst = os.path.join(SPARKLE_DIR, f)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
        return

    if len(os.listdir(SPARKLE_DIR)) < 90:
        subprocess.run(["python", os.path.join(WORKDIR, "generate_sparkles.py")], check=True)

# Step 2: Render Dazzling Blinding Bloom Transition Chunk (2.15s)
def render_dazzling_bloom_chunk(out_chunk_path, duration=2.15):
    print(f">> Rendering Dazzling Blinding Light Transition Chunk ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))

    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid = resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"))

    # Extract Before Frames
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:02', '-t', str(duration), '-i', before_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-r', '30', f'{DAZZLE_DIR}/bf_%03d.png'
    ], capture_output=True, check=True)

    # Extract After Frames
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:00', '-t', str(duration), '-i', after_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-r', '30', f'{DAZZLE_DIR}/af_%03d.png'
    ], capture_output=True, check=True)

    # Composite with Blinding Bloom Transition
    # Peak at frame 31 (around 1.03s)
    # Ramp up: frame 21 to 31 (0.70s to 1.03s)
    # Ramp down: frame 31 to 42 (1.03s to 1.40s)
    # After frame 33: Sparkles appear on after porcelain skin!
    for f in range(total_frames):
        bf_path = f'{DAZZLE_DIR}/bf_{f+1:03d}.png'
        af_path = f'{DAZZLE_DIR}/af_{f+1:03d}.png'
        if not os.path.exists(bf_path) or not os.path.exists(af_path):
            continue
        img_b = Image.open(bf_path).convert('RGB')
        img_a = Image.open(af_path).convert('RGB')

        # Add Shimmering Sparkles on After Skin
        sp_idx = (f % 90) + 1
        sp_file = os.path.join(SPARKLE_DIR, f'sp_{sp_idx:03d}.png')
        if os.path.exists(sp_file):
            sp_img = Image.open(sp_file).convert('RGBA')
            img_a_rgba = img_a.convert('RGBA')
            img_a = Image.alpha_composite(img_a_rgba, sp_img).convert('RGB')

        if f < 21:
            out_img = img_b
        elif f < 31:
            # Exponential Ramp up to Blinding Bloom
            p = (f - 21) / 10.0
            flash = (math.sin(p * math.pi / 2)) ** 1.3
            enh = ImageEnhance.Brightness(img_b)
            bright_b = enh.enhance(1.0 + flash * 3.5)
            white_ov = Image.new('RGB', (W, H), (255, 255, 255))
            out_img = Image.blend(bright_b, white_ov, min(1.0, flash * 0.96))
        elif f < 42:
            # Smooth Ramp down from Blinding Bloom to Porcelain Skin
            p = (f - 31) / 11.0
            flash = (math.cos(p * math.pi / 2)) ** 1.3
            enh = ImageEnhance.Brightness(img_a)
            bright_a = enh.enhance(1.0 + flash * 3.5)
            white_ov = Image.new('RGB', (W, H), (255, 255, 255))
            out_img = Image.blend(bright_a, white_ov, min(1.0, flash * 0.96))
        else:
            out_img = img_a

        out_img.save(f'{DAZZLE_DIR}/comp_{f:03d}.png')

    cmd = [
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{DAZZLE_DIR}/comp_%03d.png',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        out_chunk_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f">> Successfully generated Dazzling Light Transition: {out_chunk_path}")


def main():
    print("=" * 75)
    print(">> Retiragen Master Commercial v8 (No Badges + Dazzling Transition + Unique 3D) Starting...")
    print("=" * 75)

    ensure_sparkles()

    scene_defs = [
        # Scene 1 (2.677s): Opening Hook
        # "전 피부과 프락셀 안 받아도 모공 요철 제로예요."
        {
            "id": 1,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_01.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.46, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H00FFFFFF&}전 피부과 프락셀 안 받아도 {\\fnSegoe UI Emoji\\c&H8080FF&}🌸"},
                {"start": 1.46, "end": 2.677, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H00FFFFFF&}모공 요철 {\\c&H0000E5FF&}제로{\\c&H00FFFFFF&}예요! {\\fnSegoe UI Emoji\\c&H00FFFF&}✨"}
            ],
            "cuts": [
                {
                    "name": "01_greeting_smile_hook",
                    "asset": os.path.join(MODEL_DIR, "환하게 인사하는 장면 - Trim.mp4"),
                    "start": 0.0, "dur": 2.677,
                    "zoom": True, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 2 (3.664s): Mirror Check & Severe Face Oil Blotting Paper
        # "유명한 모공 앰플, 레티놀 크림 다 써봐도 개기름 뜨고 화장 밀리고,"
        {
            "id": 2,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_02.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.00, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}유명한 모공 앰플,"},
                {"start": 1.00, "end": 2.20, "text": "{\\fnSegoe UI Emoji\\c&H80FFFF&}💧 {\\fnJalnan 2\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&} 다 써봐도"},
                {"start": 2.20, "end": 3.664, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}개기름 뜨고 {\\c&H0000E5FF&}화장 밀리고... {\\fnSegoe UI Emoji\\c&H80FFFF&}💦"}
            ],
            "cuts": [
                {
                    "name": "02_mirror_cream",
                    "asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.800,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "03_oil_blotting_paper",
                    "asset": os.path.join(ROOT_DIR, "기름종이.mp4"),
                    "start": 3.5, "dur": 1.864,
                    "zoom": True, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 3 (3.457s): Frustrated Face & Butterfly Zone Pore Crater Macro
        # "심할 땐 피부가 아예 뒤집어지더라고요. 결국 나비존 요철만 푹 파였죠"
        {
            "id": 3,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_03.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 0.75, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}심할 땐 피부가"},
                {"start": 0.75, "end": 1.64, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}아예 {\\c&H0000E5FF&}뒤집어지더라고요! {\\fnSegoe UI Emoji\\c&H5050FF&}💥"},
                {"start": 1.64, "end": 2.65, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}결국 나비존 요철만"},
                {"start": 2.65, "end": 3.457, "text": "{\\fnSegoe UI Emoji\\c&H0050FF&}🚨 {\\fnJalnan 2\\c&H0000E5FF&}푹 파였죠! {\\fnSegoe UI Emoji\\c&H0050FF&}🚨"}
            ],
            "cuts": [
                {
                    "name": "04_frustrated_face",
                    "asset": os.path.join(MODEL_DIR, "답답해 - Trim.mp4"),
                    "start": 0.2, "dur": 1.650,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "05_pore_crater_macro",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"),
                    "start": 1.0, "dur": 1.807,
                    "zoom": True, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 4 (4.084s): Dazzling Blinding Light Transition & Pill in Palm
        # "근데 귤껍질 같던 볼살 매끈해진 거 보이세요? 전 레티놀 크림을 삼키기 시작했어요."
        {
            "id": 4,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_04.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.20, "text": "{\\fnSegoe UI Emoji\\c&H00A0FF&}🍊 {\\fnJalnan 2\\c&H00FFFFFF&}귤껍질 같던 볼살"},
                {"start": 1.20, "end": 2.15, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H0000E5FF&}매끈해진 거{\\c&H00FFFFFF&} 보이세요?"},
                {"start": 2.15, "end": 3.10, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}전 {\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&}을"},
                {"start": 3.10, "end": 4.084, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}💊 {\\fnJalnan 2\\c&H0000E5FF&}삼키기 시작했어요! {\\fnSegoe UI Emoji\\c&H8080FF&}💊"}
            ],
            "cuts": [
                {
                    "name": "06_dazzling_bloom_transition",
                    "is_dazzle": True,
                    "dur": 2.150
                },
                {
                    "name": "07_pill_in_palm",
                    "asset": os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4"),
                    "start": 0.3, "dur": 1.934,
                    "zoom": True, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 5 (1.582s): Shock Reaction
        # "엥? 레티놀 크림을 삼켜요?"
        {
            "id": 5,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_05.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.582, "text": "{\\fnSegoe UI Emoji\\c&H00E5FF&}⚡ {\\fnJalnan 2\\c&H0000E5FF&}엥?!{\\c&H00FFFFFF&} 레티놀 크림을 삼켜요?! {\\fnSegoe UI Emoji\\c&H00E5FF&}⚡"}
            ],
            "cuts": [
                {
                    "name": "08_shocked_phone_zoom",
                    "asset": os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.582,
                    "zoom": True, "sparkles": False, "flash": True
                }
            ]
        },
        # Scene 6 (5.916s): Hesitation + Sunny Heat + 3D Skin Cellular Plumping
        # "저도 처음엔 안 믿었는데, 아니 땡볕 야구장을 다녀와도 피지가 터지기는커녕 요철이 점점 더 팽팽하게 차오르는 거예요!"
        {
            "id": 6,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_06.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.10, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}저도 처음엔 안 믿었는데,"},
                {"start": 1.10, "end": 2.40, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}☀️ {\\fnJalnan 2\\c&H0000E5FF&}땡볕 야구장{\\c&H00FFFFFF&}을 다녀와도"},
                {"start": 2.40, "end": 3.50, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}피지가 터지기는커녕"},
                {"start": 3.50, "end": 4.60, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}요철이 점점 더"},
                {"start": 4.60, "end": 5.916, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}💖 {\\fnJalnan 2\\c&H0000E5FF&}팽팽하게 차오르는 거예요! {\\fnSegoe UI Emoji\\c&H8080FF&}💖"}
            ],
            "cuts": [
                {
                    "name": "09_hesitant_face",
                    "asset": os.path.join(MODEL_DIR, "고민.mp4"),
                    "start": 0.5, "dur": 1.200,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "10_sunny_heat_shielding",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\12.mp4"),
                    "start": 0.5, "dur": 2.300,
                    "zoom": True, "sparkles": False, "flash": False
                },
                {
                    "name": "11_3d_skin_cellular_plumping",
                    "asset": os.path.join(ROOT_DIR, "새살 차오르기.mp4"),
                    "start": 1.0, "dur": 2.416,
                    "zoom": True, "sparkles": True, "flash": True
                }
            ]
        },
        # Scene 7 (4.040s): Supplement Intake + 17호 Skin Closeup Angle 2
        # "그렇게 한 달 정도 꾸준히 먹어보니, 이젠 프라이머 없이도 매끈한 17호 피부가 됐어요."
        {
            "id": 7,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_07.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.46, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H00FFFFFF&}한 달 정도 꾸준히 먹어보니,"},
                {"start": 1.46, "end": 2.50, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}이젠 프라이머 없이도"},
                {"start": 2.50, "end": 4.040, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌷 {\\fnJalnan 2\\c&H0000E5FF&}매끈한 17호 피부{\\c&H00FFFFFF&}가 됐어요!"}
            ],
            "cuts": [
                {
                    "name": "12_taking_pill",
                    "asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"),
                    "start": 2.0, "dur": 1.600,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "13_shade17_skin_closeup2",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업2 - Trim.mp4"),
                    "start": 0.0, "dur": 2.440,
                    "zoom": True, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 8 (7.499s): 3D Sebum Dry + 3D Collagen Matrix + Clinic Laser + Admiring Cheek Touch
        # "알고 보니 속피지선부터 바짝 말려주고 진피 속엔 초저분자 콜라겐을 메워주는 원리라는데, 와, 피부과 프락셀 레이저가 피부 자체에 이식된 느낌?"
        {
            "id": 8,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_08.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.00, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}알고 보니 속피지선부터"},
                {"start": 1.00, "end": 2.02, "text": "{\\fnSegoe UI Emoji\\c&H00E5FF&}🔬 {\\fnJalnan 2\\c&H0000E5FF&}바짝 말려주고! {\\fnSegoe UI Emoji\\c&H00E5FF&}🔬"},
                {"start": 2.02, "end": 3.20, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}진피 속엔 초저분자 콜라겐"},
                {"start": 3.20, "end": 4.42, "text": "{\\fnSegoe UI Emoji\\c&H80FFFF&}🧬 {\\fnJalnan 2\\c&H0000E5FF&}가득 메워주는 원리! {\\fnSegoe UI Emoji\\c&H80FFFF&}🧬"},
                {"start": 4.42, "end": 5.70, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}와, 피부과 프락셀 레이저가"},
                {"start": 5.70, "end": 7.499, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}💎 {\\fnJalnan 2\\c&H0000E5FF&}피부 자체에 이식된 느낌?! {\\fnSegoe UI Emoji\\c&H00FFFF&}💎"}
            ],
            "cuts": [
                {
                    "name": "14_sebum_dry_3d",
                    "asset": os.path.join(MODEL_DIR, "피지,모낭 없애는.mp4"),
                    "start": 0.5, "dur": 2.000,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "15_collagen_mesh_3d",
                    "asset": os.path.join(ROOT_DIR, "새살 차오르기 2.mp4"), # 3D Collagen fibers weaving! Completely unique!
                    "start": 1.0, "dur": 2.000,
                    "zoom": True, "sparkles": True, "flash": False
                },
                {
                    "name": "16_laser_clinic",
                    "asset": os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4"),
                    "start": 0.5, "dur": 1.600,
                    "zoom": True, "sparkles": False, "flash": False
                },
                {
                    "name": "17_cheek_touch_macro",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"),
                    "start": 0.5, "dur": 1.899,
                    "zoom": True, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 9 (3.173s): Radiant Laughter + Double Thumbs Up
        # "하루 종일 자연광 맞아도 매끈한 깐달걀 피부 톤이 쭈욱 유지돼요!"
        {
            "id": 9,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_09.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.15, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}☀️ {\\fnJalnan 2\\c&H00FFFFFF&}하루 종일 자연광 맞아도"},
                {"start": 1.15, "end": 2.35, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H0000E5FF&}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&}이"},
                {"start": 2.35, "end": 3.173, "text": "{\\fnJalnan 2\\c&H0000E5FF&}쭈욱 유지돼요! {\\fnSegoe UI Emoji\\c&H00FFFF&}✨"}
            ],
            "cuts": [
                {
                    "name": "18_daylight_laughter",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.400,
                    "zoom": True, "sparkles": True, "flash": True
                },
                {
                    "name": "19_confident_thumbs_up",
                    "asset": os.path.join(MODEL_DIR, "따봉.mp4"),
                    "start": 0.5, "dur": 1.773,
                    "zoom": True, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 10 (Audio: 4.263s, Video: 5.463s with 1.20s Outro Hold):
        # "30일 기간 한정 반값 할인도 한다는데, 궁금한 분들은 아래 비밀링크 참고해 보세요"
        {
            "id": 10,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_10.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 0.85, "text": "{\\fnJalnan 2\\c&H00FFFFFF&}30일 기간 한정"},
                {"start": 0.85, "end": 1.92, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🎉 {\\fnJalnan 2\\c&H0000E5FF&}반값 할인 중! {\\fnSegoe UI Emoji\\c&H00FFFF&}🎉"},
                {"start": 1.92, "end": 2.80, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🤫 {\\fnJalnan 2\\c&H00FFFFFF&}궁금한 분들은"},
                {"start": 2.80, "end": 4.263, "text": "{\\fnSegoe UI Emoji\\c&H8080FF&}💖 {\\fnJalnan 2\\c&H0000E5FF&}아래 비밀링크{\\c&H00FFFFFF&} 참고해 보세요~"},
                {"start": 4.263, "end": 5.463, "text": "{\\fnSegoe UI Emoji\\c&H00FFFF&}👆 {\\fnJalnan 2\\c&H0000E5FF&}지금 링크에서 확인하세요! {\\fnSegoe UI Emoji\\c&H00FFFF&}👆"}
            ],
            "cuts": [
                {
                    "name": "20_product_box_model",
                    "asset": os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4"),
                    "start": 0.5, "dur": 1.800,
                    "hflip": True,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "21_secret_whisper",
                    "asset": os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4"),
                    "start": 0.5, "dur": 1.800,
                    "zoom": True, "sparkles": False, "flash": False
                },
                {
                    "name": "22_cta_pointing_down",
                    "asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"),
                    "start": 0.0, "dur": 1.863,
                    "zoom": False, "sparkles": False, "flash": False
                }
            ]
        }
    ]

    print(">> Processing 22 Unique Video Chunks...")
    all_chunks = []
    chunk_idx = 0

    v7_chunk_dir = os.path.join(WORKDIR, "build_temp_v7", "chunks")

    for s_idx, s in enumerate(scene_defs):
        for c_idx, c in enumerate(s["cuts"]):
            chunk_idx += 1
            chunk_file = os.path.join(CHUNK_DIR, f"chunk_{chunk_idx:02d}.mp4")
            all_chunks.append(chunk_file)

            # Special Dazzling Light Transition Chunk (Chunk 06)
            if c.get("is_dazzle", False):
                render_dazzling_bloom_chunk(chunk_file, duration=c["dur"])
                continue

            # Check if this chunk is unchanged from v7 and can be reused
            # Only Chunk 06 (dazzle) and Chunk 15 (new collagen 3D) are changed!
            v7_candidate = os.path.join(v7_chunk_dir, f"chunk_{chunk_idx:02d}.mp4")
            if chunk_idx != 6 and chunk_idx != 15 and os.path.exists(v7_candidate) and os.path.getsize(v7_candidate) > 50000:
                if not os.path.exists(chunk_file) or os.path.getsize(chunk_file) == 0:
                    shutil.copy2(v7_candidate, chunk_file)
                print(f"   ✓ Chunk {chunk_idx:02d}: {c['name']} reused from v7 cache.")
                continue

            # Standard Chunk Rendering
            filter_chains = []
            curr_in = "0:v"

            if c.get("hflip", False):
                filter_chains.append(f"[{curr_in}]hflip[flipped]")
                curr_in = "flipped"

            filter_chains.append(f"[{curr_in}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[scaled]")
            curr_v = "[scaled]"

            if c.get("zoom", False):
                filter_chains.append(f"{curr_v}scale=w='1080*(1+0.07*t)':h='1920*(1+0.07*t)':eval=frame,crop=1080:1920[zoomed]")
                curr_v = "[zoomed]"

            if c.get("sparkles", False):
                filter_chains.append(f"[1:v]fps=30[sp];{curr_v}[sp]overlay=0:0:shortest=1[sparkled]")
                curr_v = "[sparkled]"

            if c.get("flash", False):
                filter_chains.append(f"{curr_v}fade=t=in:st=0:d=0.08:color=white[flashed]")
                curr_v = "[flashed]"

            filter_chains.append(f"{curr_v}fps=30,format=yuv420p[out]")
            vf_str = ";".join(filter_chains)

            if not os.path.exists(chunk_file) or os.path.getsize(chunk_file) == 0:
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(c["start"]),
                    "-t", str(c["dur"]),
                    "-i", resolve_asset(c["asset"])
                ]
                if c.get("sparkles", False):
                    sp_pattern = os.path.join(SPARKLE_DIR, "sp_%03d.png")
                    cmd.extend(["-stream_loop", "-1", "-r", "30", "-i", sp_pattern])

                cmd.extend([
                    "-filter_complex", vf_str,
                    "-map", "[out]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-an",
                    chunk_file
                ])
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"   ✓ Chunk {chunk_idx:02d}: {c['name']} ({c['dur']:.3f}s) rendered.")
            else:
                print(f"   ✓ Chunk {chunk_idx:02d}: {c['name']} exists.")

    # Concat all 22 chunks
    print(">> Concatenating 22 unique chunks...")
    concat_list = os.path.join(BUILD_DIR, "chunks.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(f"file '{ch.replace('\\\\', '/')}'\n")

    raw_visual = os.path.join(BUILD_DIR, "raw_visual.mp4")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        raw_visual
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)
    print(">> Raw visual concatenated successfully.")

    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", raw_visual]
    total_video_dur = float(subprocess.check_output(cmd_dur).decode().strip())
    print(f">> Total Video Duration: {total_video_dur:.3f}s")

    # Step 3: Build 1.2x Master Audio
    print(">> Mixing 1.2x Master Audio...")
    master_narr = AudioSegment.empty()
    scene_offsets = []
    curr_offset = 0.0

    for s in scene_defs:
        scene_offsets.append(curr_offset)
        seg = AudioSegment.from_wav(s["audio"])
        master_narr += seg
        curr_offset += len(seg) / 1000.0

    narr_dur_s = len(master_narr) / 1000.0
    print(f"   Spoken 1.2x Narration Duration: {narr_dur_s:.3f}s")
    total_master_ms = int(round(total_video_dur * 1000.0))

    # BGM setup
    bgm_path = find_sfx("Its Jazz full.wav") or find_sfx("Its Jazz 30 sec.wav")
    if not bgm_path:
        bgm_path = os.path.join(SFX_DIR, r"1_BGM(일상)\Its Jazz 30 sec.wav")
    bgm = AudioSegment.from_wav(bgm_path) - 27
    loop_bgm = AudioSegment.empty()
    while len(loop_bgm) < total_master_ms + 2000:
        loop_bgm += bgm
    loop_bgm = loop_bgm[:total_master_ms].fade_in(300).fade_out(1200)

    mix_audio = loop_bgm.overlay(master_narr)

    # SFX Synchronization
    # 1. 0.00s: Opening Snap
    sfx_snap = find_sfx("Finger Snap") or find_sfx("snap")
    if sfx_snap:
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_snap)[:1000] - 8, position=0)

    # 2. Scene 3 + 1.64s: Suspense Riser (나비존 요철 파임)
    sfx_suspense = find_sfx("Suspense 1") or find_sfx("스릴러")
    if sfx_suspense:
        pos_ms = int((scene_offsets[2] + 1.64) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_suspense)[:1800] - 12, position=pos_ms)

    # 3. Scene 4 + 1.03s: Dazzling Transition Whoosh & Magical Shine (Blinding light reveal!)
    sfx_whoosh = find_sfx("Whoosh Transition 1") or find_sfx("whoosh")
    if sfx_whoosh:
        pos_ms = int((scene_offsets[3] + 0.85) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_whoosh)[:1500] - 8, position=pos_ms)
    sfx_ding = find_sfx("Ding Chime") or find_sfx("bell")
    if sfx_ding:
        pos_ms = int((scene_offsets[3] + 1.10) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_ding)[:1200] - 8, position=pos_ms)

    # 4. Scene 4 + 2.15s: Ding Chime (레티놀 삼키기 시작)
    if sfx_ding:
        pos_ms = int((scene_offsets[3] + 2.15) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_ding)[:1200] - 8, position=pos_ms)

    # 5. Scene 5 + 0.00s: Pop Reaction Accent (엥?! 삼켜요? 쇼크 리액션)
    sfx_pop = find_sfx("물음표") or find_sfx("pop")
    if sfx_pop:
        pos_ms = int(scene_offsets[4] * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_pop)[:1000] - 6, position=pos_ms)

    # 6. Scene 10 + 1.92s: Subtle Click (비밀링크 안내)
    sfx_click = find_sfx("Mouse Click") or find_sfx("클릭")
    if sfx_click:
        pos_ms = int((scene_offsets[9] + 1.92) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_click)[:800] - 10, position=pos_ms)

    master_audio_path = os.path.join(WORKDIR, "master_audio_v8.wav")
    mix_audio.export(master_audio_path, format="wav")
    print(f">> Master Audio exported to {master_audio_path}")

    # Step 4: Generate Clean Subtitles (No Top Badges! Only Floral & Emoji Dialogue)
    print(">> Generating Subtitles (No Top Badges, Only Floral/Emoji Animated PopSub)...")
    ass_path = os.path.join(WORKDIR, "subtitles_v8.ass")

    def format_time(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(f"""[Script Info]
Title: Retiragen Shortform CapCut Floral Subtitles v8
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: PopSub,Jalnan 2,68,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5.0,2.5,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        # NO TOP BADGES! Only Dialogue Subtitles
        for s_idx, s in enumerate(scene_defs):
            s_base = scene_offsets[s_idx]

            for cue in s["sub_cues"]:
                st = s_base + cue["start"]
                et = s_base + cue["end"]
                st_str = format_time(st)
                et_str = format_time(et)

                anim_prefix = "{\\fscx90\\fscy90\\t(0,70,\\fscx110\\fscy110)\\t(70,140,\\fscx100\\fscy100)}"
                f.write(f"Dialogue: 0,{st_str},{et_str},PopSub,,0,0,0,,{anim_prefix}{cue['text']}\n")

    print(f">> Subtitles saved to {ass_path}")

    # Step 5: Final Master Video Assembly
    print(">> Assembling Final Master Video...")
    final_mp4 = os.path.join(WORKDIR, "retiragen_shortform_hypit.mp4")
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

    cmd_final = [
        "ffmpeg", "-y",
        "-i", raw_visual,
        "-i", master_audio_path,
        "-vf", f"subtitles='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        final_mp4
    ]
    subprocess.run(cmd_final, check=True)
    print(f"Final Commercial Video Successfully Created at: {final_mp4}")

    # Step 6: Generate 16-Frame Tile Sheet for Visual Inspection
    tile_sheet = os.path.join(WORKDIR, "retiragen_hypit_tile16_v8.jpg")
    tile_artifact = r"C:\Users\5700G\.gemini\antigravity-ide\brain\dbf7f899-383b-4576-bd82-ea14ebea7e97\retiragen_hypit_tile16_v8.jpg"
    print(">> Generating 16-Frame Verification Tile Sheet with Hypit...")
    if os.path.exists(tile_sheet):
        os.remove(tile_sheet)
    if os.path.exists(tile_artifact):
        os.remove(tile_artifact)

    cmd_tile = f'hypit media tile "{final_mp4}" --frames 16 --columns 4 --to "{tile_sheet}"'
    subprocess.run(cmd_tile, shell=True, check=True)

    Image.open(tile_sheet).save(tile_artifact)
    print(f"Verification Tile Sheet ready at: {tile_artifact}")

    # Step 7: Update Hypit SVML
    svml_content = f"""<composition width="1080" height="1920" fps="30" duration="{total_video_dur:.3f}s">
  <video src="{final_mp4.replace('\\', '/')}" in="0s" out="{total_video_dur:.3f}s" />
  <audio src="{master_audio_path.replace('\\', '/')}" in="0s" out="{total_video_dur:.3f}s" />
</composition>
"""
    with open(os.path.join(WORKDIR, "main.svml"), "w", encoding="utf-8") as f:
        f.write(svml_content)
    print(">> Updated main.svml successfully!")

if __name__ == "__main__":
    main()
