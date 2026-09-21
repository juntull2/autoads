"""
Master Rendering Pipeline for Retiragen ad17 Benchmark Video (V5 - Clean, High-Legibility, XHS Radiance):
1. 가독성 극대화 (Clean Canvas):
   - 상단 박스, 날짜 배지, USP 카드, CTA 배너 등 시야를 가리고 가독성을 해치는 난잡한 오버레이 전면 삭제
   - 자막: 단일 Jalnan 2 폰트 통일, 68px, 5.0px 블랙 아웃라인, 2.0px 그림자, MarginV: 340
   - 1큐당 5~12자 단문 분할(1줄 원칙) + CapCut PopSub 스프링 팝 바운스 애니메이션
2. 효과음 절제 (Strictly 1 SFX per scene):
   - 씬당 정확히 1개, 총 7개의 효과음만 적재적소 배치 (스팸 및 중복 차임 금지)
   - BGM -27dB 더킹 유지
3. 샤오홍슈(XHS) 피부 소스 및 광채(Radiance) 이펙트 적극 반영:
   - Cut 4: XHS 리얼 개기름/피지 소스 (17.mp4)
   - Cut 11: Side-by-Side 듀얼 스플릿 (좌: XHS 여드름 비포 18.mp4 vs 우: XHS 도자기 물광 애프터 10.mp4 + 광채 스파클)
   - Cut 13: XHS 피지 컨트롤 B-roll (05.mp4)
   - Cut 14: XHS 깐달걀 도자기 피부 클로즈업 (10.mp4) + 4-Point 다이아몬드/골드 광채 스파클 합성!
   - Cut 18: XHS 탄력 팽팽 볼 클로즈업 (20.mp4) + 4-Point 광채 스파클 합성!
   - Cut 17: 제품 패키지 한글 가독성을 위한 hflip 적용
4. 100% Fish Audio TTS 고음질 윤라영 보이스, 카메라 마이크 음성 100% 차단 (-an), 1.41s 아웃트로 여운
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
BUILD_DIR = os.path.join(WORKDIR, "build_ad17_fish")
CHUNK_DIR = os.path.join(BUILD_DIR, "chunks_clean_v5")
SPLIT_DIR = os.path.join(BUILD_DIR, "split_frames_clean_v5")
SPARKLE_DIR = os.path.join(WORKDIR, "build_temp_v9", "sparkles")

os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(SPLIT_DIR, exist_ok=True)

FONT_JALNAN = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf"

def resolve_asset(path):
    if os.path.exists(path):
        return path
    dirname = os.path.dirname(path)
    base = os.path.basename(path)
    if os.path.exists(dirname):
        for f in os.listdir(dirname):
            if base[:8].lower() in f.lower():
                return os.path.join(dirname, f)
    return path

def render_split_chunk(out_chunk_path, duration=3.350):
    if os.path.exists(out_chunk_path):
        try:
            p_res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', out_chunk_path], capture_output=True, text=True)
            if abs(float(p_res.stdout.strip()) - duration) < 0.05:
                return
        except Exception:
            pass
            
    print(f">> Pre-rendering Side-by-Side Dual Split Screen ({duration:.2f}s)...")
    W, H = 1080, 1920
    FPS = 30
    total_frames = int(round(duration * FPS))
    
    before_vid = resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\18.mp4"))
    after_vid = resolve_asset(os.path.join(XHS_DIR, r"4_ugc_videos\10.mp4"))
    f_tag = ImageFont.truetype(FONT_JALNAN, 36)
    
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:02', '-t', str(duration), '-i', before_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0,fps=30',
        '-an', f'{SPLIT_DIR}/left_%03d.png'
    ], capture_output=True, check=True)
    
    subprocess.run([
        'ffmpeg', '-y', '-ss', '00:00:01', '-t', str(duration), '-i', after_vid,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=540:1920:270:0,fps=30',
        '-an', f'{SPLIT_DIR}/right_%03d.png'
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
        # White center divider line
        d.line([(540, 0), (540, H)], fill=(255, 255, 255, 240), width=4)
        
        # Subtle Before Tag
        d.rounded_rectangle([195, 120, 345, 185], radius=16, fill=(40, 40, 50, 210), outline=(255, 100, 100, 240), width=2)
        d.text((270, 152), '비포', fill=(255, 120, 120), font=f_tag, anchor='mm')
        
        # Subtle After Tag
        d.rounded_rectangle([735, 120, 885, 185], radius=16, fill=(245, 140, 190, 240), outline=(255, 255, 255, 255), width=2)
        d.text((810, 152), '애프터', fill=(255, 255, 255), font=f_tag, anchor='mm')
        
        canvas.convert('RGB').save(f'{SPLIT_DIR}/comp_{f:03d}.png')
        
    cmd = [
        'ffmpeg', '-y', '-r', '30',
        '-i', f'{SPLIT_DIR}/comp_%03d.png',
        '-t', str(duration),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-an',
        out_chunk_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f">> Pre-rendered Split Chunk: {out_chunk_path}")


def render_all_cuts():
    split_chunk = os.path.join(CHUNK_DIR, "c11_split.mp4")
    render_split_chunk(split_chunk, duration=3.350)
    
    # 22 Balanced cuts strictly calibrated to Whisper boundaries (Total: 47.361s)
    # Zero clutter overlays! Clean, cinematic, premium.
    cuts = [
        # Scene 1: Hook (0.00s ~ 1.35s, dur: 1.350)
        {
            "id": 1, "name": "c01_hook_greeting",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 인사하는 장면2 - Trim.mp4")),
            "ss": 0.0, "dur": 1.350, "zoom": True, "hflip": False
        },
        # Scene 2: Laser Agony & Flaking (1.35s ~ 7.95s, dur: 6.600)
        {
            "id": 2, "name": "c02_laser_broll",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "Person_receiving_laser_skin_trea…_202609041413.mp4")),
            "ss": 0.0, "dur": 2.350, "zoom": True, "hflip": False
        },
        {
            "id": 3, "name": "c03_powder_flaking_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "결혼준비_2_메이크업_파우더터치.mp4")),
            "ss": 0.5, "dur": 1.550, "zoom": True, "hflip": False
        },
        {
            "id": 4, "name": "c04_xhs_sebum_shine",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\17.mp4")),
            "ss": 1.0, "dur": 2.700, "zoom": True, "hflip": False
        },
        # Scene 3: Paradigm Shift & Concept (7.95s ~ 16.30s, dur: 8.350)
        {
            "id": 5, "name": "c05_model_confident",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "드루와.mp4")),
            "ss": 0.1, "dur": 1.400, "zoom": True, "hflip": False
        },
        {
            "id": 6, "name": "c06_model_smiling_point",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "따봉.mp4")),
            "ss": 0.5, "dur": 1.450, "zoom": True, "hflip": False
        },
        {
            "id": 7, "name": "c07_model_x_gesture",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "엑스.mp4")),
            "ss": 0.5, "dur": 2.350, "zoom": True, "hflip": False
        },
        {
            "id": 8, "name": "c08_model_worrying",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "답답해 - Trim.mp4")),
            "ss": 0.2, "dur": 1.350, "zoom": True, "hflip": False
        },
        {
            "id": 9, "name": "c09_pouring_pills_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "약 쏟아붓는.mp4")),
            "ss": 0.2, "dur": 1.800, "zoom": True, "hflip": False
        },
        # Scene 4: Shock Reaction (16.30s ~ 18.50s, dur: 2.200)
        {
            "id": 10, "name": "c10_shocked_phone",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "폰 보고 놀라는 장면 - Trim.mp4")),
            "ss": 0.2, "dur": 2.200, "zoom": True, "hflip": False
        },
        # Scene 5: Side-by-Side Before & After + Mechanism (18.50s ~ 29.90s, dur: 11.400)
        {
            "id": 11, "name": "c11_split",
            "asset": split_chunk,
            "ss": 0.0, "dur": 3.350, "zoom": False, "hflip": False, "prebuilt": True
        },
        {
            "id": 12, "name": "c12_collagen_matrix_3d",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "새살 차오르기 2.mp4")),
            "ss": 0.5, "dur": 3.000, "zoom": True, "hflip": False
        },
        {
            "id": 13, "name": "c13_sebum_control_broll",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\05.mp4")),
            "ss": 0.5, "dur": 3.100, "zoom": True, "hflip": False
        },
        # XHS Porcelain Glass Skin + Sparkle Radiance Effect!
        {
            "id": 14, "name": "c14_xhs_glass_skin_radiance",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_ugc_videos\10.mp4")),
            "ss": 2.0, "dur": 1.950, "zoom": True, "hflip": False,
            "radiance": True
        },
        # Scene 6: High-Spec Ingredients & Product (29.90s ~ 40.05s, dur: 10.150)
        {
            "id": 15, "name": "c15_formula_macro_broll",
            "asset": resolve_asset(os.path.join(ROOT_DIR, "약 성분 소개.mp4")),
            "ss": 0.2, "dur": 3.350, "zoom": True, "hflip": False
        },
        {
            "id": 16, "name": "c16_product_closeup_broll",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 확대샷.mp4")),
            "ss": 0.5, "dur": 2.250, "zoom": True, "hflip": False
        },
        {
            "id": 17, "name": "c17_package_hflip",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "제품 얼굴 옆에 들고 찍는 장면(좌우반전됨..) - Trim.mp4")),
            "ss": 0.5, "dur": 2.250, "zoom": True, "hflip": True
        },
        # XHS Bouncy Plump Porcelain Skin + Sparkle Radiance Effect!
        {
            "id": 18, "name": "c18_xhs_bouncy_skin_radiance",
            "asset": resolve_asset(os.path.join(XHS_DIR, r"4_피부_숏폼영상_무자막\20.mp4")),
            "ss": 4.5, "dur": 2.300, "zoom": True, "hflip": False,
            "radiance": True
        },
        # Scene 7: Climax & Ending CTA + Outro Hold (40.05s ~ 47.361s, dur: 7.311)
        {
            "id": 19, "name": "c19_secret_whisper",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "이거 비밀인데.. - Trim.mp4")),
            "ss": 0.5, "dur": 1.450, "zoom": True, "hflip": False
        },
        {
            "id": 20, "name": "c20_model_taking_pill",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "약 복용 장면 - Trim.mp4")),
            "ss": 2.0, "dur": 1.950, "zoom": True, "hflip": False
        },
        {
            "id": 21, "name": "c21_pointing_cta",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "화살표 아래로_CTA (손가락 모양이 좀..) - Trim.mp4")),
            "ss": 0.2, "dur": 2.500, "zoom": True, "hflip": False
        },
        {
            "id": 22, "name": "c22_outro_hold_smile",
            "asset": resolve_asset(os.path.join(MODEL_DIR, "환하게 웃는 장면 - Trim.mp4")),
            "ss": 0.3, "dur": 1.411, "zoom": True, "hflip": False
        }
    ]
    
    rendered_chunks = []
    print(f">> Rendering {len(cuts)} clean cuts (Strictly -an applied to all chunks)...")
    for cut in cuts:
        chunk_out = os.path.join(CHUNK_DIR, f"{cut['name']}.mp4")
        dur = cut["dur"]
        ss = cut["ss"]
        asset = cut["asset"]
        
        if cut.get("prebuilt") and os.path.exists(cut["asset"]):
            rendered_chunks.append(cut["asset"])
            continue
            
        need_render = True
        if os.path.exists(chunk_out):
            try:
                p_res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', chunk_out], capture_output=True, text=True)
                cur_dur = float(p_res.stdout.strip())
                if abs(cur_dur - dur) < 0.05:
                    need_render = False
                    rendered_chunks.append(chunk_out)
            except Exception:
                pass
                
        if need_render:
            vf_filters = []
            vf_filters.append("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
            
            if cut.get("hflip"):
                vf_filters.append("hflip")
                
            if cut.get("zoom"):
                vf_filters.append(f"scale=eval=frame:w='1080*(1+0.12*t/{dur:.3f})':h='1920*(1+0.12*t/{dur:.3f})',crop=1080:1920")
                
            vf_filters.append("fps=30,tpad=stop_mode=clone:stop_duration=5")
            base_vf = ",".join(vf_filters)
            
            if cut.get("radiance"):
                # Composite 4-point sparkle particles over video
                sp_pattern = os.path.join(SPARKLE_DIR, "sp_%03d.png")
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(ss),
                    '-i', asset,
                    '-r', '30',
                    '-i', sp_pattern,
                    '-filter_complex', f"[0:v]{base_vf}[base];[base][1:v]overlay=0:0:format=auto:shortest=1[v]",
                    '-map', '[v]',
                    '-t', str(dur),
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-an',
                    chunk_out
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(ss),
                    '-i', asset,
                    '-vf', base_vf,
                    '-t', str(dur),
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-an',
                    chunk_out
                ]
            subprocess.run(cmd, check=True, capture_output=True)
            rendered_chunks.append(chunk_out)
            print(f"   [{cut['id']:02d}/22] Rendered {cut['name']} (target: {dur:.3f}s, silent video)")
        else:
            print(f"   [{cut['id']:02d}/22] Reusing {cut['name']} (verified: {dur:.3f}s)")
            
    return rendered_chunks

def concat_and_burn():
    chunks = render_all_cuts()
    concat_txt = os.path.join(BUILD_DIR, "concat_list_clean.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in chunks:
            rel_p = os.path.relpath(c, BUILD_DIR).replace('\\', '/')
            f.write(f"file '{rel_p}'\n")
            
    raw_merged = os.path.join(BUILD_DIR, "raw_visual_merged_clean.mp4")
    print(">> Concatenating visual chunks...")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', "concat_list_clean.txt",
        '-c', 'copy', raw_merged
    ], cwd=BUILD_DIR, check=True, capture_output=True)
    
    probe_raw = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', raw_merged], capture_output=True, text=True)
    raw_dur = float(probe_raw.stdout.strip())
    print(f">> Merged Visual Track Duration: {raw_dur:.3f}s")
    
    master_audio = os.path.join(BUILD_DIR, "master_audio_fish.wav")
    ass_subs = os.path.join(BUILD_DIR, "ad17_fish_clean_subs.ass").replace('\\', '/').replace(':', '\\:')
    
    final_output = os.path.join(WORKDIR, "ad17_retiragen_fish_remastered.mp4")
    print(f">> Burning Perfectly Synced Clean Subtitles & Muxing Master Audio into: {final_output}...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', raw_merged,
        '-i', master_audio,
        '-filter_complex', f"[0:v]subtitles='{ass_subs}'[v]",
        '-map', '[v]',
        '-map', '1:a:0',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '256k',
        final_output
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(">> FINAL REMASTERED VIDEO EXPORTED SUCCESSFULLY!")
    
    probe_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', final_output
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    final_dur = float(res.stdout.strip())
    print(f">> Final Video Duration: {final_dur:.3f}s")
    
    # 16-Tile Sheet
    tile_out = os.path.join(WORKDIR, "ad17_tile16_fish.jpg")
    step = final_dur / 17.0
    subprocess.run([
        'ffmpeg', '-y', '-i', final_output,
        '-vf', f"fps=1/{step:.3f},scale=270:480,tile=4x4",
        '-frames:v', '1', tile_out
    ], check=True, capture_output=True)
    print(f">> 16-Tile Sheet: {tile_out}")

if __name__ == "__main__":
    concat_and_burn()
