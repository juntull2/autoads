"""
Retiragen Master Commercial v5:
1. Mandatory Acne Before ➔ After Laser Wipe Transition with glowing cyan/white scanline & sleek glass badges
2. 100% Strict Asset Constraint: Exclusively from 윤라영님모델_소스 and xhs_sources
3. Flawless Voice Narration to the very end (49.58s total timeline with 1.2s outro hold, NO truncation)
4. Clean 1-Line Dynamic Variety Pop Subtitles (Jalnan 2, NO multi-line wrap glitches, neon yellow highlights)
5. Radiant Champagne & Diamond Sparkles on glowing skin
6. 6 Purposeful Sound Effects (Snap, Laser Whoosh, Suspense, Chime, Pop, Click) + Ducked Jazz BGM
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
SFX_DIR = r"C:\Users\5700G\Desktop\효과음"
AUDIO_DIR = r"C:\adforge\temp_audio\retiragen_pore_v2"
BUILD_DIR = os.path.join(WORKDIR, "build_temp_v5")
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

def get_audio_duration(p):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

# Step 1: Ensure Sparkles are generated
def ensure_sparkles():
    old_sparkles = os.path.join(WORKDIR, "build_temp_v4", "sparkles")
    if os.path.exists(old_sparkles) and len(os.listdir(old_sparkles)) >= 90:
        print(">> Copying existing sparkle frames from v4...")
        for f in os.listdir(old_sparkles):
            src = os.path.join(old_sparkles, f)
            dst = os.path.join(SPARKLE_DIR, f)
            if not os.path.exists(dst):
                Image.open(src).save(dst)
        return

    if len(os.listdir(SPARKLE_DIR)) < 90:
        print(">> Generating 90 sparkle frames...")
        subprocess.run(["python", os.path.join(WORKDIR, "generate_sparkles.py")], check=True)

# Step 2: Render Acne Before ➔ After Wipe Chunk
def render_acne_wipe_chunk(out_chunk_path, duration=2.54):
    if os.path.exists(out_chunk_path) and os.path.getsize(out_chunk_path) > 100000:
        print(f">> Acne Before/After chunk already exists: {out_chunk_path}")
        return

    print(f">> Rendering Acne Before ➔ After Wipe Chunk ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))

    before_vid = os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4")
    after_vid = os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4")

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
    wipe_start = int(0.35 * FPS)
    wipe_end = int(1.75 * FPS)
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

        # Sleek Glass Badges (Physically matched to sides)
        # 1. BEFORE badge: Visible on the right side while acne remains
        if prog < 0.92:
            d.rounded_rectangle([W - 270, 160, W - 60, 230], radius=22, fill=(15, 15, 20, 200), outline=(255, 80, 80, 230), width=3)
            d.text((W - 165, 195), "BEFORE", fill=(255, 95, 95), font=f_badge, anchor='mm')

        # 2. AFTER badge: Visible on the left side as clean porcelain skin appears
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
    print(f">> Successfully generated Acne Before/After Wipe: {out_chunk_path}")


def main():
    print("=" * 70)
    print(">> Retiragen Master Commercial v5 (Acne Wipe + Flawless Narration + Clean Subs) Starting...")
    print("=" * 70)

    ensure_sparkles()

    # Define Scenes with Exact Spoken Word Offsets & Strict Asset Boundaries
    # Total Audio Narration Runtime: 48.379s
    # Total Commercial Video Timeline: 49.58s (Includes 1.20s comfortable outro hold)
    scene_defs = [
        # Scene 1 (3.213s): "전 피부과 프락셀 안 받아도 모공 요철 제로예요."
        {
            "id": 1,
            "audio": os.path.join(AUDIO_DIR, "scene_01.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.76, "text": "전 피부과 프락셀 안 받아도"},
                {"start": 1.76, "end": 3.20, "text": "모공 요철 {\\c&H0000E5FF&}제로{\\c&H00FFFFFF&}예요!"}
            ],
            "cuts": [
                {
                    "name": "01_smile",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 0.0, "dur": 3.213,
                    "punch": 1.05, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 2 (4.389s): "유명한 모공 앰플, 레티놀 크림 다 써봐도 개기름 뜨고 화장 밀리고,"
        {
            "id": 2,
            "audio": os.path.join(AUDIO_DIR, "scene_02.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.20, "text": "유명한 모공 앰플,"},
                {"start": 1.20, "end": 2.64, "text": "{\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&} 다 써봐도"},
                {"start": 2.64, "end": 4.389, "text": "개기름 뜨고 화장 밀리고"}
            ],
            "cuts": [
                {
                    "name": "02_mirror_cream",
                    "asset": os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 2.100,
                    "punch": 1.10, "sparkles": False, "flash": True
                },
                {
                    "name": "03_skin_redness",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\14.mp4"),
                    "start": 1.0, "dur": 2.289,
                    "punch": 1.08, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 3 (4.153s): "심할 땐 피부가 아예 뒤집어지더라고요. 결국 나비존 요철만 푹 파였죠"
        {
            "id": 3,
            "audio": os.path.join(AUDIO_DIR, "scene_03.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 0.95, "text": "심할 땐 피부가"},
                {"start": 0.95, "end": 2.05, "text": "아예 {\\c&H0000E5FF&}뒤집어지더라고요{\\c&H00FFFFFF&}"},
                {"start": 2.05, "end": 3.20, "text": "결국 나비존 요철만"},
                {"start": 3.20, "end": 4.153, "text": "{\\c&H0000E5FF&}푹 파였죠{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "04_annoyed",
                    "asset": os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4"),
                    "start": 1.5, "dur": 2.000,
                    "punch": 1.12, "sparkles": False, "flash": True
                },
                {
                    "name": "05_pore_closeup",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\07.mp4"),
                    "start": 2.5, "dur": 2.153,
                    "punch": 1.15, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 4 (4.885s): "근데 귤껍질 같던 볼살 매끈해진 거 보이세요? 전 레티놀 크림을 삼키기 시작했어요."
        {
            "id": 4,
            "audio": os.path.join(AUDIO_DIR, "scene_04.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.45, "text": "귤껍질 같던 볼살"},
                {"start": 1.45, "end": 2.54, "text": "{\\c&H0000E5FF&}매끈해진 거{\\c&H00FFFFFF&} 보이세요?"},
                {"start": 2.54, "end": 3.70, "text": "전 {\\c&H0000E5FF&}레티놀 크림{\\c&H00FFFFFF&}을"},
                {"start": 3.70, "end": 4.885, "text": "{\\c&H0000E5FF&}삼키기 시작했어요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "06_before_after_wipe",
                    "is_wipe": True,
                    "dur": 2.540
                },
                {
                    "name": "07_pill_palm",
                    "asset": os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4"),
                    "start": 0.3, "dur": 2.345,
                    "punch": 1.08, "sparkles": False, "flash": False
                }
            ]
        },
        # Scene 5 (1.881s): "엥? 레티놀 크림을 삼켜요?"
        {
            "id": 5,
            "audio": os.path.join(AUDIO_DIR, "scene_05.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.881, "text": "{\\c&H0000E5FF&}엥?!{\\c&H00FFFFFF&} 레티놀 크림을 삼켜요?!"}
            ],
            "cuts": [
                {
                    "name": "08_shocked_phone",
                    "asset": os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 1.881,
                    "punch": 1.25, "sparkles": False, "flash": True
                }
            ]
        },
        # Scene 6 (7.079s): "저도 처음엔 안 믿었는데, 아니 땡볕 야구장을 다녀와도 피지가 터지기는커녕 요철이 점점 더 팽팽하게 차오르는 거예요!"
        {
            "id": 6,
            "audio": os.path.join(AUDIO_DIR, "scene_06.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.50, "text": "저도 처음엔 안 믿었는데,"},
                {"start": 1.50, "end": 3.00, "text": "땡볕 야구장을 다녀와도"},
                {"start": 3.00, "end": 4.40, "text": "피지가 터지기는커녕"},
                {"start": 4.40, "end": 5.80, "text": "요철이 점점 더"},
                {"start": 5.80, "end": 7.079, "text": "{\\c&H0000E5FF&}팽팽하게 차오르는 거예요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "09_hesitant",
                    "asset": os.path.join(MODEL_DIR, "고민.mp4"),
                    "start": 0.5, "dur": 1.660,
                    "punch": 1.10, "sparkles": False, "flash": True
                },
                {
                    "name": "10_sun_heat",
                    "asset": os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\14.mp4"),
                    "start": 2.0, "dur": 2.760,
                    "punch": 1.15, "sparkles": False, "flash": False
                },
                {
                    "name": "11_skin_glow_porcelain",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"),
                    "start": 1.0, "dur": 2.659,
                    "punch": 1.18, "sparkles": True, "flash": True
                }
            ]
        },
        # Scene 7 (4.859s): "그렇게 한 달 정도 꾸준히 먹어보니, 이젠 프라이머 없이도 매끈한 17호 피부가 됐어요."
        {
            "id": 7,
            "audio": os.path.join(AUDIO_DIR, "scene_07.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.76, "text": "한 달 정도 꾸준히 먹어보니,"},
                {"start": 1.76, "end": 3.10, "text": "이젠 프라이머 없이도"},
                {"start": 3.10, "end": 4.859, "text": "{\\c&H0000E5FF&}매끈한 17호 피부{\\c&H00FFFFFF&}가 됐어요!"}
            ],
            "cuts": [
                {
                    "name": "12_taking_pill",
                    "asset": os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4"),
                    "start": 2.0, "dur": 2.000,
                    "punch": 1.05, "sparkles": False, "flash": True
                },
                {
                    "name": "13_shade17_skin",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"),
                    "start": 2.2, "dur": 2.859,
                    "punch": 1.15, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 8 (8.986s): "알고 보니 속피지선부터 바짝 말려주고 진피 속엔 초저분자 콜라겐을 메워주는 원리라는데, 와, 피부과 프락셀 레이저가 피부 자체에 이식된 느낌?"
        {
            "id": 8,
            "audio": os.path.join(AUDIO_DIR, "scene_08.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.20, "text": "알고 보니 속피지선부터"},
                {"start": 1.20, "end": 2.38, "text": "{\\c&H0000E5FF&}바짝 말려주고!{\\c&H00FFFFFF&}"},
                {"start": 2.38, "end": 3.80, "text": "진피 속엔 초저분자 콜라겐"},
                {"start": 3.80, "end": 5.30, "text": "{\\c&H0000E5FF&}가득 메워주는 원리!{\\c&H00FFFFFF&}"},
                {"start": 5.30, "end": 7.18, "text": "와, 피부과 프락셀 레이저가"},
                {"start": 7.18, "end": 8.986, "text": "{\\c&H0000E5FF&}피부 자체에 이식된 느낌?!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "14_sebum_dry_3d",
                    "asset": os.path.join(MODEL_DIR, "피지,모낭 없애는.mp4"),
                    "start": 0.5, "dur": 2.400,
                    "punch": 1.12, "sparkles": False, "flash": True
                },
                {
                    "name": "15_collagen_mesh_3d",
                    "asset": os.path.join(MODEL_DIR, "Collagen_fibers_repairing_skin_t…_202609041402.mp4"),
                    "start": 0.5, "dur": 2.400,
                    "punch": 1.15, "sparkles": True, "flash": False
                },
                {
                    "name": "16_laser_clinic",
                    "asset": os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4"),
                    "start": 0.5, "dur": 2.000,
                    "punch": 1.10, "sparkles": False, "flash": False
                },
                {
                    "name": "17_cheek_touch",
                    "asset": os.path.join(MODEL_DIR, "환하게 인사하는 장면 - Trim.mp4"),
                    "start": 0.5, "dur": 2.186,
                    "punch": 1.15, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 9 (3.814s): "하루 종일 자연광 맞아도 매끈한 깐달걀 피부 톤이 쭈욱 유지돼요!"
        {
            "id": 9,
            "audio": os.path.join(AUDIO_DIR, "scene_09.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.50, "text": "하루 종일 자연광 맞아도"},
                {"start": 1.50, "end": 2.80, "text": "{\\c&H0000E5FF&}매끈한 깐달걀 피부 톤{\\c&H00FFFFFF&}이"},
                {"start": 2.80, "end": 3.814, "text": "쭈욱 유지돼요!"}
            ],
            "cuts": [
                {
                    "name": "18_daylight_skin",
                    "asset": os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4"),
                    "start": 0.5, "dur": 1.800,
                    "punch": 1.15, "sparkles": True, "flash": True
                },
                {
                    "name": "19_daylight_smile",
                    "asset": os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4"),
                    "start": 1.0, "dur": 2.014,
                    "punch": 1.20, "sparkles": True, "flash": False
                }
            ]
        },
        # Scene 10 (Audio: 5.120s, Video: 6.320s with 1.2s Outro Hold):
        # "30일 기간 한정 반값 할인도 한다는데, 궁금한 분들은 아래 비밀링크 참고해 보세요"
        {
            "id": 10,
            "audio": os.path.join(AUDIO_DIR, "scene_10.wav"),
            "sub_cues": [
                {"start": 0.00, "end": 1.10, "text": "30일 기간 한정"},
                {"start": 1.10, "end": 2.30, "text": "{\\c&H0000E5FF&}반값 할인 중!{\\c&H00FFFFFF&}"},
                {"start": 2.30, "end": 3.40, "text": "궁금한 분들은"},
                {"start": 3.40, "end": 5.120, "text": "{\\c&H0000E5FF&}아래 비밀링크{\\c&H00FFFFFF&} 참고해 보세요~"},
                {"start": 5.120, "end": 6.320, "text": "{\\c&H0000E5FF&}지금 바로 확인하세요!{\\c&H00FFFFFF&}"}
            ],
            "cuts": [
                {
                    "name": "20_product_macro",
                    "asset": os.path.join(MODEL_DIR, "제품 확대샷.mp4"),
                    "start": 1.0, "dur": 2.500,
                    "punch": 1.12, "sparkles": False, "flash": True
                },
                {
                    "name": "21_cta_down_hold",
                    "asset": os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4"),
                    "start": 0.0, "dur": 3.820,
                    "punch": 1.10, "sparkles": False, "flash": False
                }
            ]
        }
    ]

    print(">> Processing 21 Video Chunks...")
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
            punch = c.get("punch", 1.0)
            target_w = int(1080 * punch)
            target_h = int(1920 * punch)
            if target_w % 2 != 0: target_w += 1
            if target_h % 2 != 0: target_h += 1

            filter_chains = []
            filter_chains.append(f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop=1080:1920[scaled]")
            curr_v = "[scaled]"

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
                    "-i", c["asset"]
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

    # Step 3: Build Master Audio (Full Narration + Ducked Jazz BGM + 6 SFX)
    print(">> Mixing Master Audio...")
    master_narr = AudioSegment.empty()
    scene_offsets = []
    curr_offset = 0.0

    for s in scene_defs:
        scene_offsets.append(curr_offset)
        seg = AudioSegment.from_wav(s["audio"])
        master_narr += seg
        curr_offset += len(seg) / 1000.0

    narr_dur_s = len(master_narr) / 1000.0
    print(f"   Spoken Narration Duration: {narr_dur_s:.3f}s")
    total_master_ms = int(round(total_video_dur * 1000.0))

    # BGM setup
    bgm_path = find_sfx("Its Jazz full.wav") or find_sfx("Its Jazz 30 sec.wav")
    if not bgm_path:
        bgm_path = os.path.join(SFX_DIR, r"1_BGM(일상)\Its Jazz 30 sec.wav")
    bgm = AudioSegment.from_wav(bgm_path) - 27 # -27dB ducking
    loop_bgm = AudioSegment.empty()
    while len(loop_bgm) < total_master_ms + 2000:
        loop_bgm += bgm
    loop_bgm = loop_bgm[:total_master_ms].fade_in(400).fade_out(1500)

    # Base mix: overlay narration on BGM
    mix_audio = loop_bgm.overlay(master_narr)

    # 6 Purposeful Sound Effects
    # 1. 0.00s: Opening Snap
    sfx_snap = find_sfx("Finger Snap") or find_sfx("snap")
    if sfx_snap:
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_snap)[:1000] - 8, position=0)

    # 2. Scene 3 + 2.05s: Suspense Riser (나비존 요철 파임)
    sfx_suspense = find_sfx("Suspense 1") or find_sfx("스릴러")
    if sfx_suspense:
        pos_ms = int((scene_offsets[2] + 2.05) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_suspense)[:2000] - 12, position=pos_ms)

    # 3. Scene 4 + 0.35s: Whoosh Laser Scanline Transition (Acne Before -> After Wipe!)
    sfx_whoosh = find_sfx("Whoosh Transition 1") or find_sfx("whoosh")
    if sfx_whoosh:
        pos_ms = int((scene_offsets[3] + 0.35) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_whoosh)[:1500] - 8, position=pos_ms)

    # 4. Scene 4 + 2.54s: Ding Chime (레티놀 삼키기 시작)
    sfx_ding = find_sfx("Ding Chime") or find_sfx("bell")
    if sfx_ding:
        pos_ms = int((scene_offsets[3] + 2.54) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_ding)[:1500] - 8, position=pos_ms)

    # 5. Scene 5 + 0.00s: Pop Reaction Accent (엥?! 삼켜요? 쇼크 리액션)
    sfx_pop = find_sfx("물음표") or find_sfx("pop")
    if sfx_pop:
        pos_ms = int(scene_offsets[4] * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_pop)[:1000] - 6, position=pos_ms)

    # 6. Scene 10 + 2.30s: Subtle Click (비밀링크 안내)
    sfx_click = find_sfx("Mouse Click") or find_sfx("클릭")
    if sfx_click:
        pos_ms = int((scene_offsets[9] + 2.30) * 1000)
        mix_audio = mix_audio.overlay(AudioSegment.from_file(sfx_click)[:800] - 10, position=pos_ms)

    master_audio_path = os.path.join(WORKDIR, "master_audio_v5.wav")
    mix_audio.export(master_audio_path, format="wav")
    print(f">> Master Audio exported to {master_audio_path}")

    # Step 4: Generate Clean Single-Line ASS Subtitles (NO Multi-line Wrap Glitches!)
    print(">> Generating Clean 1-Line Pop-Animated Subtitles (Jalnan 2)...")
    ass_path = os.path.join(WORKDIR, "subtitles_v5.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(f"""[Script Info]
Title: Retiragen Shortform Pop Subtitles v5
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: PopSub,Jalnan 2,66,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.2,2.0,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
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

                # Native ASS Pop Animation: starts at 92%, smoothly bounces to 106% in 100ms, settles to 100% in 180ms
                anim_prefix = "{\\fscx92\\fscy92\\t(0,100,\\fscx106\\fscy106)\\t(100,180,\\fscx100\\fscy100)}"
                f.write(f"Dialogue: 0,{st_str},{et_str},PopSub,,0,0,0,,{anim_prefix}{cue['text']}\n")

    print(f">> Subtitles saved to {ass_path}")

    # Step 5: Final Master Video Assembly (Burning Subtitles & Muxing Audio, NO -shortest!)
    print(">> Assembling Final Master Video (Full Narration + Zero Clipping)...")
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
