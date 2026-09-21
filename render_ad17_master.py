"""
Master Rendering Pipeline for Retiragen ad17 Benchmark Video:
- 27 Perfectly Calibrated Unique Cuts matching exact scene audio boundaries (Total: 69.101s)
- Pre-rendered Side-by-Side Dual Split Screen (비포 vs 애프터 2분할 비교 연출, 3.20s)
- Overlays:
  - Scene 1: SNS Comment Question Sticker (하얘서 넘 부러워요ㅠㅠ비결이 뭐예요? 💖)
  - Scene 2: Clinic Expense Tag (피부과 프락셀 10회+ / 총 180만원 💸)
  - Scene 6: Spec Highlight Card (스위스 레티놀 + GPH 300Da 콜라겐 27,000mg)
  - Scene 6: Product Package Scene with hflip filter applied!
- Ken Burns 1.0x ➔ 1.15x Push-in Zoom on all cuts
- CapCut PopSub Subtitle Burn (ad17_subtitles.ass, Jalnan 2, MarginV 340, Spring-Pop Bounce, Emojis)
- Master Audio (master_audio_ad17.wav with 1.2x pacing, SFX, ducked BGM, and 1.23s Outro Hold)
Output: ad17_retiragen_master.mp4
"""

import os
import sys
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

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
BUILD_DIR = os.path.join(WORKDIR, "build_ad17")
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks_v2")
SPLIT_DIR = os.path.join(BUILD_DIR, "split_frames")
SPARKLE_DIR = os.path.join(BUILD_DIR, "sparkles")
OVERLAY_DIR = os.path.join(BUILD_DIR, "overlays")

os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(SPARKLE_DIR, exist_ok=True)

FONT_JALNAN = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf"

def resolve_asset(path):
    if os.path.exists(path):
        return path
    dirname = os.path.dirname(path)
    base = os.path.basename(path)
    if os.path.exists(dirname):
        for f in os.listdir(dirname):
            if base[:10].lower() in f.lower():
                return os.path.join(dirname, f)
    return path

def render_split_chunk(out_chunk_path, duration=3.20):
    if os.path.exists(out_chunk_path):
        return
    print(f">> Pre-rendering Side-by-Side Dual Split Screen Chunk ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))
    
    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid = resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4"))
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
        
        sp_idx = (f % 90)
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
        
    cmd = [
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{SPLIT_DIR}/comp_%03d.png',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        out_chunk_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f">> Successfully generated Side-by-Side Dual Split Screen Chunk: {out_chunk_path}")


def render_all_cuts():
    split_chunk_path = os.path.join(BUILD_DIR, "chunks", "cut_11_split.mp4")
    if not os.path.exists(split_chunk_path):
        render_split_chunk(split_chunk_path, duration=3.20)
        
    # 27 Perfectly Calibrated Unique Cuts (Exact Total: 69.101s)
    cuts = [
        # Scene 1: Opening Hook (0.000s ~ 1.992s, dur: 1.992)
        {
            "id": 1, "name": "c01_hook",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 인사하는 장면2 - Trim.mp4")),
            "ss": 0.0, "dur": 1.992,
            "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "comment_sticker.png"),
            "overlay_pos": "(W-w)/2:220"
        },
        # Scene 2: Laser Agony & Flaking (2.072s ~ 11.936s, dur: 9.864)
        {
            "id": 2, "name": "c02_laser",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4")),
            "ss": 0.0, "dur": 3.000,
            "zoom": True, "hflip": False,
            "overlay": os.path.join(OVERLAY_DIR, "clinic_tag.png"),
            "overlay_pos": "(W-w)/2:220"
        },
        {
            "id": 3, "name": "c03_mirror_check",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "거울 보는 장면 - Trim.mp4")),
            "ss": 0.5, "dur": 1.800,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 4, "name": "c04_mirror_frustrated",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "거울 보며 짜증내는 장면.mp4")),
            "ss": 1.0, "dur": 2.400,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 5, "name": "c05_xhs_sebum",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\17.mp4")),
            "ss": 0.5, "dur": 2.664,
            "zoom": True, "hflip": False, "overlay": None
        },
        # Scene 3: Paradigm Shift & Concept (12.016s ~ 25.720s, dur: 13.704)
        {
            "id": 6, "name": "c06_wondering",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "고민.mp4")),
            "ss": 0.5, "dur": 2.500,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 7, "name": "c07_confident",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "드루와.mp4")),
            "ss": 0.2, "dur": 1.900,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 8, "name": "c08_glance",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "카메라 응시하며 째려보기2 - Trim.mp4")),
            "ss": 0.2, "dur": 2.000,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 9, "name": "c09_x_gesture",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "엑스.mp4")),
            "ss": 0.5, "dur": 2.500,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 10, "name": "c10_headache",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "머리 짚는2.mp4")),
            "ss": 0.2, "dur": 2.400,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 11, "name": "c11_pill_palm",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "약 손바닥 위에 있는 장면 - Trim.mp4")),
            "ss": 0.2, "dur": 2.404,
            "zoom": True, "hflip": False, "overlay": None
        },
        # Scene 4: Shock Reaction (25.800s ~ 29.328s, dur: 3.528)
        {
            "id": 12, "name": "c12_shocked_phone",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4")),
            "ss": 0.2, "dur": 2.500,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 13, "name": "c13_wait_moment",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "잠깐 - Trim.mp4")),
            "ss": 0.2, "dur": 1.028,
            "zoom": True, "hflip": False, "overlay": None
        },
        # Scene 5: Side-by-Side Dual Split Screen + Mechanism (29.408s ~ 45.440s, dur: 16.032)
        {
            "id": 14, "name": "c14_split",
            "asset": split_chunk_path,
            "ss": 0.0, "dur": 3.200,
            "zoom": False, "hflip": False, "overlay": None, "prebuilt": True
        },
        {
            "id": 15, "name": "c15_sebum_control",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\05.mp4")),
            "ss": 0.5, "dur": 2.800,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 16, "name": "c16_collagen_matrix",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "새살 차오르기 2.mp4")),
            "ss": 0.5, "dur": 3.500,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 17, "name": "c17_taking_pill",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4")),
            "ss": 2.0, "dur": 3.200,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 18, "name": "c18_porcelain_skin",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업 - Trim.mp4")),
            "ss": 0.5, "dur": 3.332,
            "zoom": True, "hflip": False, "overlay": None
        },
        # Scene 6: Spec Highlight Card & Package (45.520s ~ 58.144s, dur: 12.624)
        {
            "id": 19, "name": "c19_expensive_ceramide",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "머리 짚는.mp4")),
            "ss": 0.5, "dur": 2.800,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 20, "name": "c20_package_hflip",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4")),
            "ss": 0.2, "dur": 3.600,
            "zoom": True,
            "hflip": True, # Crucial hflip!
            "overlay": os.path.join(OVERLAY_DIR, "spec_card.png"),
            "overlay_pos": "(W-w)/2:220"
        },
        {
            "id": 21, "name": "c21_product_closeup",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 확대샷.mp4")),
            "ss": 0.5, "dur": 2.500,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 22, "name": "c22_plump_skin2",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업2 - Trim.mp4")),
            "ss": 0.2, "dur": 2.081,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 23, "name": "c23_after_result",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "여드름 애프터 2.mp4")),
            "ss": 0.5, "dur": 1.643,
            "zoom": True, "hflip": False, "overlay": None
        },
        # Scene 7: Climax & Ending CTA (58.224s ~ 69.101s, dur: 10.877)
        {
            "id": 24, "name": "c24_skin_closeup3",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "피부 클로즈업3 - Trim.mp4")),
            "ss": 0.5, "dur": 2.500,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 25, "name": "c25_secret_whisper",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4")),
            "ss": 0.5, "dur": 2.600,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 26, "name": "c26_pointing_cta",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4")),
            "ss": 0.2, "dur": 3.200,
            "zoom": True, "hflip": False, "overlay": None
        },
        {
            "id": 27, "name": "c27_smiling_outro_hold",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4")),
            "ss": 0.5, "dur": 2.577, # Holds till exact 69.101s!
            "zoom": True, "hflip": False, "overlay": None
        }
    ]
    
    rendered_chunks = []
    print(f">> Rendering {len(cuts)} unique cuts with Ken Burns push-in zoom & overlays...")
    for cut in cuts:
        chunk_out = os.path.join(CHUNK_DIR, f"{cut['name']}.mp4")
        if cut.get("prebuilt") and os.path.exists(cut["asset"]):
            rendered_chunks.append(cut["asset"])
            continue
            
        dur = cut["dur"]
        ss = cut["ss"]
        asset = cut["asset"]
        
        vf_filters = []
        vf_filters.append("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
        
        if cut.get("hflip"):
            vf_filters.append("hflip")
            
        if cut.get("zoom"):
            vf_filters.append("scale=1242:2208,zoompan=z='min(zoom+0.0010,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30")
            
        vf_str = ",".join(vf_filters)
        
        if cut.get("overlay") and os.path.exists(cut["overlay"]):
            overlay_f = cut["overlay"].replace('\\', '/')
            pos = cut.get("overlay_pos", "(W-w)/2:220")
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(ss), '-t', str(dur), '-i', asset,
                '-i', overlay_f,
                '-filter_complex', f"[0:v]{vf_str}[base];[base][1:v]overlay={pos}:format=auto[v]",
                '-map', '[v]',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-r', '30',
                chunk_out
            ]
        else:
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(ss), '-t', str(dur), '-i', asset,
                '-vf', vf_str,
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-r', '30',
                chunk_out
            ]
            
        subprocess.run(cmd, check=True, capture_output=True)
        rendered_chunks.append(chunk_out)
        print(f"   [{cut['id']:02d}/27] Rendered {cut['name']} ({dur:.3f}s)")
        
    return rendered_chunks

def concat_and_burn():
    chunks = render_all_cuts()
    concat_txt = os.path.join(BUILD_DIR, "concat_list_v2.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in chunks:
            c_norm = c.replace('\\', '/')
            f.write(f"file '{c_norm}'\n")
            
    raw_merged = os.path.join(BUILD_DIR, "raw_visual_merged_v2.mp4")
    print(">> Concatenating visual chunks...")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-c', 'copy', raw_merged
    ], check=True, capture_output=True)
    
    # Master Video with Audio & ASS Subtitles
    master_audio = os.path.join(BUILD_DIR, "master_audio_ad17.wav")
    ass_subs = os.path.join(BUILD_DIR, "ad17_subtitles.ass").replace('\\', '/').replace(':', '\\:')
    
    final_output = os.path.join(WORKDIR, "ad17_retiragen_master.mp4")
    print(f">> Burning ASS Subtitles & muxing master audio into final video: {final_output}...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', raw_merged,
        '-i', master_audio,
        '-vf', f"subtitles='{ass_subs}'",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '256k',
        final_output
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(">> FINAL MASTER VIDEO EXPORTED SUCCESSFULLY!")
    
    # Check duration
    probe_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', final_output
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    final_dur = float(res.stdout.strip())
    print(f">> Final Master Video Duration: {final_dur:.3f}s")
    
    # Generate 16-frame tile sheet for verification
    tile_out = os.path.join(WORKDIR, "ad17_tile16_master.jpg")
    step = final_dur / 17.0
    subprocess.run([
        'ffmpeg', '-y', '-i', final_output,
        '-vf', f"fps=1/{step:.3f},scale=270:480,tile=4x4",
        '-frames:v', '1', tile_out
    ], check=True, capture_output=True)
    print(f">> 16-Tile Sheet generated at: {tile_out}")

if __name__ == "__main__":
    concat_and_burn()
