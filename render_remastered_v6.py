"""
Retiragen Master Commercial v6:
1. 1.2x Dynamic TikTok/Reels Pacing (Total timeline ~41.55s, perfectly synced 1:1)
2. Dynamic Ken Burns Zoom-In ("확대 효과" / Zoompan) on key emotional and beauty cuts
3. Acne Before ➔ After Laser Wipe Transition with glowing cyan/white scanline & sleek glass badges
4. Richer Visual Directing:
   - Opening Hook Capsule Sticker: [ ✨ 프락셀 없이 모공 요철 ZERO ✨ ]
   - Sparkling Diamond Stars (샤방샤방) on glowing cheek highlights
   - Makeup sliding cut & Baseball game cut directly matching user's reference video
5. Clean 1-Line Jalnan 2 Pop Subtitles with bright sunny yellow keyword highlights
6. 6 Purposeful Sound Effects (Snap, Laser Whoosh, Suspense Riser, Ding Chime, Pop, Click) + Ducked Jazz BGM
7. Flawless Outro Buffer (1.20s hold on model pointing down) with zero audio truncation
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
MODEL_DIR = r"C:\Users\5700G\Desktop\레티라겐\윤라영님모델_소스"
XHS_DIR = r"C:\Users\5700G\Desktop\레티라겐\xhs_sources"
REF_VID = r"C:\Users\5700G\Desktop\레티라겐\피부 과학의 모든 것_1974644779903348_2026-09-18.mp4"
SFX_DIR = r"C:\Users\5700G\Desktop\효과음"
AUDIO_12X_DIR = r"C:\adforge\temp_audio\retiragen_pore_1.2x"
BUILD_DIR = os.path.join(WORKDIR, "build_temp_v6")
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks")
SPARKLE_DIR = os.path.join(BUILD_DIR, "sparkles")
WIPE_DIR = os.path.join(BUILD_DIR, "wipe_frames")
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(SPARKLE_DIR, exist_ok=True)
os.makedirs(WIPE_DIR, exist_ok=True)

FONT_JALNAN = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf"

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

def get_audio_duration(p):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

# Step 1: Ensure Sparkles are generated
def ensure_sparkles():
    old_sparkles = os.path.join(WORKDIR, "build_temp_v4", "sparkles")
    if os.path.exists(old_sparkles) and len(os.listdir(old_sparkles)) >= 90:
        for f in os.listdir(old_sparkles):
            src = os.path.join(old_sparkles, f)
            dst = os.path.join(SPARKLE_DIR, f)
            if not os.path.exists(dst):
                Image.open(src).save(dst)
        return

    if len(os.listdir(SPARKLE_DIR)) < 90:
        subprocess.run(["python", os.path.join(WORKDIR, "generate_sparkles.py")], check=True)

# Step 2: Render 1.2x Acne Before ➔ After Wipe Chunk (2.15s)
def render_acne_wipe_chunk(out_chunk_path, duration=2.15):
    if os.path.exists(out_chunk_path) and os.path.getsize(out_chunk_path) > 100000:
        print(f">> Acne Before/After chunk already exists: {out_chunk_path}")
        return

    print(f">> Rendering 1.2x Acne Before ➔ After Wipe Chunk ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))

    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid = resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"))

    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:02', '-t', str(duration), '-i', before_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-r', '30', f'{WIPE_DIR}/bf_%03d.png'
    ], capture_output=True, check=True)

    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:00', '-t', str(duration), '-i', after_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-r', '30', f'{WIPE_DIR}/af_%03d.png'
    ], capture_output=True, check=True)

    f_badge = ImageFont.truetype(FONT_JALNAN, 38)
    wipe_start = int(0.25 * FPS) # starts at 0.25s
    wipe_end = int(1.45 * FPS)   # finishes at 1.45s
    wipe_dur = wipe_end - wipe_start

    for f in range(total_frames):
        bf_path = f"{WIPE_DIR}/bf_{f+1:03d}.png"
        af_path = f"{WIPE_DIR}/af_{f+1:03d}.png"
        if not os.path.exists(bf_path) or not os.path.exists(af_path):
            continue
        img_b = Image.open(bf_path).convert('RGBA')
        img_a = Image.open(af_path).convert('RGBA')

        if f < wipe_start:
            prog = 0.0
        elif f > wipe_end:
            prog = 1.0
        else:
            p = (f - wipe_start) / wipe_dur
            prog = 0.5 - 0.5 * math.cos(p * math.pi)

        split_x = int(W * prog)

        # Base canvas is Before (Right side)
        canvas = img_b.copy()
        # Overlay After on Left side
        if split_x > 0:
            crop_a = img_a.crop((0, 0, split_x, H))
            canvas.paste(crop_a, (0, 0))

        d = ImageDraw.Draw(canvas)

        # High-tech glowing cyan laser scanline
        if 0 < split_x < W:
            d.line([(split_x, 0), (split_x, H)], fill=(0, 220, 255, 60), width=36)
            d.line([(split_x, 0), (split_x, H)], fill=(50, 240, 255, 120), width=18)
            d.line([(split_x, 0), (split_x, H)], fill=(180, 255, 255, 200), width=8)
            d.line([(split_x, 0), (split_x, H)], fill=(255, 255, 255, 255), width=3)

        # Sleek Glass Badges
        # 1. BEFORE badge: Visible on the right side while acne remains
        if prog < 0.92:
            d.rounded_rectangle([W - 270, 160, W - 60, 230], radius=22, fill=(15, 15, 20, 200), outline=(255, 80, 80, 230), width=3)
            d.text((W - 165, 195), "BEFORE", fill=(255, 95, 95), font=f_badge, anchor='mm')

        # 2. AFTER badge: Visible on the left side as porcelain skin appears
        if prog > 0.08:
            d.rounded_rectangle([60, 160, 270, 230], radius=22, fill=(15, 15, 20, 200), outline=(0, 230, 255, 230), width=3)
            d.text((165, 195), "AFTER", fill=(0, 235, 255), font=f_badge, anchor='mm')

        canvas.convert('RGB').save(f"{WIPE_DIR}/comp_{f:03d}.png")

    cmd = [
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{WIPE_DIR}/comp_%03d.png',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        out_chunk_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f">> Successfully generated 1.2x Acne Before/After Wipe: {out_chunk_path}")


def main():
    print("=" * 70)
    print(">> Retiragen Master Commercial v6 (1.2x Speed + Dynamic Zoom + Rich Effects) Starting...")
    print("=" * 70)

    ensure_sparkles()

    # Total 1.2x Audio Narration Duration: 40.354s
    # Total Commercial Video Timeline: 41.554s (includes 1.20s comfortable outro hold)
    scene_defs = [
        # Scene 1 (2.677s): "전 피부과 프락셀 안 받아도 모공 요철 제로예요."
        {
            "id": 1,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_01.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.46, "text": "전 피부과 프락셀 안 받아도"},
                {"start": 1.46, "end": 2.677, "text": "모공 요철 {\\c&H0000E5FF&}제로{\\c&H00FFFFFF&}예요!"}
            ],
            "cuts": [
                {
                    "name": "01_smile_hook",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 0.0, "dur": 2.677,
                    "zoom": True, "sparkles": True, "flash": False,
                    "top_badge": "✨ 프락셀 없이 모공 요철 ZERO ✨"
                }
            ]
        },
        # Scene 2 (3.664s): "유명한 모공 앰플, 레티놀 크림 다 써봐도 개기름 뜨고 화장 밀리고,"
        {
            "id": 2,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_02.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.00, "text": "유명한 모공 앰플,"},
                {"start": 1.00, "end": 2.20, "text": "{\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&} 다 써봐도"},
                {"start": 2.20, "end": 3.664, "text": "개기름 뜨고 {\\c&H0000E5FF&}화장 밀리고{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "02_mirror_cream",
                    "asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.800,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "03_makeup_caking",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\09.mp4"),
                    "start": 0.5, "dur": 1.864,
                    "zoom": True, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 3 (3.457s): "심할 땐 피부가 아예 뒤집어지더라고요. 결국 나비존 요철만 푹 파였죠"
        {
            "id": 3,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_03.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 0.75, "text": "심할 땐 피부가"},
                {"start": 0.75, "end": 1.64, "text": "아예 {\\c&H0000E5FF&}뒤집어지더라고요{\\c&H00FFFFFF&}"},
                {"start": 1.64, "end": 2.65, "text": "결국 나비존 요철만"},
                {"start": 2.65, "end": 3.457, "text": "{\\c&H0000E5FF&}푹 파였죠!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "04_annoyed_mirror",
                    "asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"),
                    "start": 1.5, "dur": 1.650,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "05_pore_crater_zoom",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"),
                    "start": 2.0, "dur": 1.807,
                    "zoom": True, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 4 (4.084s): Climax Acne Before ➔ After Laser Wipe & Pill Ingestion!
        # "근데 귤껍질 같던 볼살 매끈해진 거 보이세요? 전 레티놀 크림을 삼키기 시작했어요."
        {
            "id": 4,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_04.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.20, "text": "귤껍질 같던 볼살"},
                {"start": 1.20, "end": 2.15, "text": "{\\c&H0000E5FF&}매끈해진 거{\\c&H00FFFFFF&} 보이세요?"},
                {"start": 2.15, "end": 3.10, "text": "전 {\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&}을"},
                {"start": 3.10, "end": 4.084, "text": "{\\c&H0000E5FF&}삼키기 시작했어요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "06_before_after_laser_wipe",
                    "is_wipe": True,
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
                {"start": 0.00, "end": 1.582, "text": "{\\c&H0000E5FF&}엥?!{\\c&H00FFFFFF&} 레티놀 크림을 삼켜요?!"}
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
        # Scene 6 (5.916s): Outdoor Sunlight / Baseball Stadium & Radiant Skin
        # "저도 처음엔 안 믿었는데, 아니 땡볕 야구장을 다녀와도 피지가 터지기는커녕 요철이 점점 더 팽팽하게 차오르는 거예요!"
        {
            "id": 6,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_06.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.10, "text": "저도 처음엔 안 믿었는데,"},
                {"start": 1.10, "end": 2.40, "text": "{\\c&H0000E5FF&}땡볕 야구장{\\c&H00FFFFFF&}을 다녀와도"},
                {"start": 2.40, "end": 3.50, "text": "피지가 터지기는커녕"},
                {"start": 3.50, "end": 4.60, "text": "요철이 점점 더"},
                {"start": 4.60, "end": 5.916, "text": "{\\c&H0000E5FF&}팽팽하게 차오르는 거예요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "09_hesitant_face",
                    "asset": os.path.join(MODEL_DIR, "고민.mp4"),
                    "start": 0.5, "dur": 1.200,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "10_baseball_stadium",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\12.mp4"),
                    "start": 0.5, "dur": 2.300,
                    "zoom": True, "sparkles": False, "flash": False
                },
                {
                    "name": "11_skin_plumping_glow",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"),
                    "start": 1.0, "dur": 2.416,
                    "zoom": True, "sparkles": True, "flash": True
                }
            ]
        },
        # Scene 7 (4.040s): Routine Pill Intake & 17호 Skin
        # "그렇게 한 달 정도 꾸준히 먹어보니, 이젠 프라이머 없이도 매끈한 17호 피부가 됐어요."
        {
            "id": 7,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_07.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.46, "text": "한 달 정도 꾸준히 먹어보니,"},
                {"start": 1.46, "end": 2.50, "text": "이젠 프라이머 없이도"},
                {"start": 2.50, "end": 4.040, "text": "{\\c&H0000E5FF&}매끈한 17호 피부{\\c&H00FFFFFF&}가 됐어요!"}
            ],
            "cuts": [
                {
                    "name": "12_taking_pill",
                    "asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"),
                    "start": 2.0, "dur": 1.600,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "13_shade17_skin_closeup",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"),
                    "start": 2.2, "dur": 2.440,
                    "zoom": True, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 8 (7.499s): 3D Science Breakdown
        # "알고 보니 속피지선부터 바짝 말려주고 진피 속엔 초저분자 콜라겐을 메워주는 원리라는데, 와, 피부과 프락셀 레이저가 피부 자체에 이식된 느낌?"
        {
            "id": 8,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_08.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.00, "text": "알고 보니 속피지선부터"},
                {"start": 1.00, "end": 2.02, "text": "{\\c&H0000E5FF&}바짝 말려주고!{\\c&H00FFFFFF&}"},
                {"start": 2.02, "end": 3.20, "text": "진피 속엔 초저분자 콜라겐"},
                {"start": 3.20, "end": 4.42, "text": "{\\c&H0000E5FF&}가득 메워주는 원리!{\\c&H00FFFFFF&}"},
                {"start": 4.42, "end": 5.70, "text": "와, 피부과 프락셀 레이저가"},
                {"start": 5.70, "end": 7.499, "text": "{\\c&H0000E5FF&}피부 자체에 이식된 느낌?!{\\c&H00FFFFFF&}"}
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
                    "asset": os.path.join(MODEL_DIR, "Collagen_fibers_repairing_skin_t…_202609041402.mp4"),
                    "start": 0.5, "dur": 2.000,
                    "zoom": True, "sparkles": True, "flash": False
                },
                {
                    "name": "16_laser_clinic",
                    "asset": os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4"),
                    "start": 0.5, "dur": 1.600,
                    "zoom": True, "sparkles": False, "flash": False
                },
                {
                    "name": "17_cheek_touch_radiant",
                    "asset": os.path.join(MODEL_DIR, "환하게 인사하는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.899,
                    "zoom": True, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 9 (3.173s): Natural Daylight Porcelain Glow
        # "하루 종일 자연광 맞아도 매끈한 깐달걀 피부 톤이 쭈욱 유지돼요!"
        {
            "id": 9,
            "audio": os.path.join(AUDIO_12X_DIR, "scene_09.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.15, "text": "하루 종일 자연광 맞아도"},
                {"start": 1.15, "end": 2.35, "text": "{\\c&H0000E5FF&}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&}이"},
                {"start": 2.35, "end": 3.173, "text": "쭈욱 유지돼요!"}
            ],
            "cuts": [
                {
                    "name": "18_daylight_skin_macro",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"),
                    "start": 0.5, "dur": 1.400,
                    "zoom": True, "sparkles": True, "flash": True
                },
                {
                    "name": "19_daylight_smile_bright",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 1.0, "dur": 1.773,
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
                {"start": 0.00, "end": 0.85, "text": "30일 기간 한정"},
                {"start": 0.85, "end": 1.92, "text": "{\\c&H0000E5FF&}반값 할인 중!{\\c&H00FFFFFF&}"},
                {"start": 1.92, "end": 2.80, "text": "궁금한 분들은"},
                {"start": 2.80, "end": 4.263, "text": "{\\c&H0000E5FF&}아래 비밀링크{\\c&H00FFFFFF&} 참고해 보세요~"},
                {"start": 4.263, "end": 5.463, "text": "{\\c&H0000E5FF&}지금 링크에서 확인하세요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "20_product_discount_zoom",
                    "asset": os.path.join(MODEL_DIR, "제품 확대샷.mp4"),
                    "start": 1.0, "dur": 2.000,
                    "zoom": True, "sparkles": False, "flash": True
                },
                {
                    "name": "21_cta_pointing_down",
                    "asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"),
                    "start": 0.0, "dur": 3.463, # Holds on model smiling and pointing down
                    "zoom": False, "sparkles": False, "flash": False
                }
            ]
        }
    ]

    print(">> Processing 21 Video Chunks with Dynamic Ken Burns Zoom & Rich Effects...")
    all_chunks = []
    chunk_idx = 0

    for s_idx, s in enumerate(scene_defs):
        for c_idx, c in enumerate(s["cuts"]):
            chunk_idx += 1
            chunk_file = os.path.join(CHUNK_DIR, f"chunk_{chunk_idx:02d}.mp4")
            all_chunks.append(chunk_file)

            # Special Wipe Chunk
            if c.get("is_wipe", False):
                render_acne_wipe_chunk(chunk_file, duration=c["dur"])
                continue

            # Standard Chunk Rendering
            filter_chains = []
            
            # Base scale + crop to 1080x1920
            filter_chains.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[scaled]")
            curr_v = "[scaled]"

            # Dynamic Ken Burns Zoom-In (확대 효과)
            if c.get("zoom", False):
                # Smooth push-in from 1.0 to 1.15x over duration
                filter_chains.append(f"{curr_v}scale=w='1080*(1+0.07*t)':h='1920*(1+0.07*t)':eval=frame,crop=1080:1920[zoomed]")
                curr_v = "[zoomed]"

            # Sparkles if enabled
            if c.get("sparkles", False):
                filter_chains.append(f"[1:v]fps=30[sp];{curr_v}[sp]overlay=0:0:shortest=1[sparkled]")
                curr_v = "[sparkled]"

            # White flash bloom transition at cut entry
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

    # Concat all chunks
    print(">> Concatenating 21 chunks...")
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

    # Check raw visual duration
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
    bgm = AudioSegment.from_wav(bgm_path) - 27 # -27dB ducking
    loop_bgm = AudioSegment.empty()
    while len(loop_bgm) < total_master_ms + 2000:
        loop_bgm += bgm
    loop_bgm = loop_bgm[:total_master_ms].fade_in(300).fade_out(1200)

    # Base mix: overlay narration on BGM
    mix_audio = loop_bgm.overlay(master_narr)

    # 6 Purposeful Sound Effects (Re-synchronized to 1.2x speed)
    # 1. 0.00s: Opening Snap
    sfx_snap = find_sfx("Finger Snap") or find_sfx("snap")
    if sfx_snap:
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_snap)[:1000] - 8, position=0)

    # 2. Scene 3 + 1.64s: Suspense Riser (나비존 요철 파임)
    sfx_suspense = find_sfx("Suspense 1") or find_sfx("스릴러")
    if sfx_suspense:
        pos_ms = int((scene_offsets[2] + 1.64) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_suspense)[:1800] - 12, position=pos_ms)

    # 3. Scene 4 + 0.25s: Whoosh Laser Scanline Transition (Acne Before -> After Wipe!)
    sfx_whoosh = find_sfx("Whoosh Transition 1") or find_sfx("whoosh")
    if sfx_whoosh:
        pos_ms = int((scene_offsets[3] + 0.25) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_whoosh)[:1500] - 8, position=pos_ms)

    # 4. Scene 4 + 2.15s: Ding Chime (레티놀 삼키기 시작)
    sfx_ding = find_sfx("Ding Chime") or find_sfx("bell")
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

    master_audio_path = os.path.join(WORKDIR, "master_audio_v6.wav")
    mix_audio.export(master_audio_path, format="wav")
    print(f">> Master Audio exported to {master_audio_path}")

    # Step 4: Generate Clean Single-Line ASS Subtitles at 1.2x Speed
    print(">> Generating Clean 1-Line Pop Subtitles at 1.2x Speed (Jalnan 2)...")
    ass_path = os.path.join(WORKDIR, "subtitles_v6.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(f"""[Script Info]
Title: Retiragen Shortform Pop Subtitles v6
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: PopSub,Jalnan 2,66,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.2,2.0,2,60,60,340,1
Style: HookBadge,Jalnan 2,42,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,3.5,1.5,8,40,40,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        # Opening Hook Sticker Badge (0.0s to 2.68s)
        f.write(f"Dialogue: 1,0:00:00.00,0:00:02.68,HookBadge,,0,0,0,,{{\\fscx90\\fscy90\\t(0,120,\\fscx100\\fscy100)}}✨ 프락셀 없이 모공 요철 ZERO ✨\n")

        for s_idx, s in enumerate(scene_defs):
            s_base = scene_offsets[s_idx]
            for cue in s["sub_cues"]:
                st = s_base + cue["start"]
                et = s_base + cue["end"]

                st_h = int(st // 3600)
                st_m = int((st % 3600) // 60)
                st_s = st % 60
                st_str = f"{st_h}:{st_m:02d}:{st_s:05.2f}"

                et_h = int(et // 3600)
                et_m = int((et % 3600) // 60)
                et_s = et % 60
                et_str = f"{et_h}:{et_m:02d}:{et_s:05.2f}"

                # Snappy 1.2x Pop Animation
                anim_prefix = "{\\fscx92\\fscy92\\t(0,80,\\fscx106\\fscy106)\\t(80,150,\\fscx100\\fscy100)}"
                f.write(f"Dialogue: 0,{st_str},{et_str},PopSub,,0,0,0,,{anim_prefix}{cue['text']}\n")

    print(f">> Subtitles saved to {ass_path}")

    # Step 5: Final Master Video Assembly (Burning Subtitles & Muxing Audio)
    print(">> Assembling Final Master Video (1.2x Speed + Full Narration)...")
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
    tile_sheet = os.path.join(WORKDIR, "retiragen_hypit_tile16_final.jpg")
    tile_artifact = r"C:\Users\5700G\.gemini\antigravity-ide\brain\dbf7f899-383b-4576-bd82-ea14ebea7e97\retiragen_hypit_tile16_final.jpg"
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
