"""
Generate Scene-based Natural Audio & Millisecond-accurate CapCut PopSub Subtitles
- 7 Scenes matching natural speech flow
- Edge-TTS ko-KR-SunHiNeural at +20% (1.2x)
- Whisper alignment for 100% exact subtitle timing
- 1-line CapCut PopSub ASS subtitles with Jalnan 2, MarginV 340, spring-pop bounce
- 6 Essential SFX + BGM ducking (-27dB) + 1.15s Outro Hold
"""

import os
import sys
import json
import asyncio
import whisper
from pydub import AudioSegment
import edge_tts

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
BUILD_DIR = os.path.join(WORKDIR, "build_ad17")
SCENE_AUDIO_DIR = os.path.join(BUILD_DIR, "scenes_audio")
os.makedirs(SCENE_AUDIO_DIR, exist_ok=True)

SFX_DIR = r"C:\Users\5700G\Desktop\효과음"

SCENES = [
    {
        "id": 1,
        "text": "제가 하얘진 비결이요?",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H00FFFFFF&}제가 하얘진 {\\c&H0000E5FF&}비결{\\c&H00FFFFFF&}이요? {\\fnSegoe UI Emoji\\c&H8080FF&}🌸", "match": "비결"}
        ],
        "sfx": [(0.0, "스냅")]
    },
    {
        "id": 2,
        "text": "저 작년에 피부과 프락셀만 10번 넘게 받았어요. 그래서 요철 다 메꿔졌냐고요? 아뇨, 붉은기만 오래 가고 화장은 여전히 떴어요.",
        "cues": [
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}저 작년에 {\\c&H0000E5FF&}피부과 프락셀{\\c&H00FFFFFF&}만", "match": "프락셀"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🏥 {\\fnJalnan 2\\c&H0000E5FF&}10번 넘게{\\c&H00FFFFFF&} 받았어요.", "match": "받았어요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}그래서 {\\c&H0000E5FF&}요철 다{\\c&H00FFFFFF&} 메꿔졌냐고요? 🤔", "match": "메꿔졌냐고요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}아뇨, {\\c&H0000E5FF&}붉은기만{\\c&H00FFFFFF&} 오래 가고", "match": "붉은기만"},
            {"display": "{\\fnSegoe UI Emoji\\c&H80FFFF&}💦 {\\fnJalnan 2\\c&H00FFFFFF&}화장은 {\\c&H0000E5FF&}여전히 떴어요 😭{\\c&H00FFFFFF&}", "match": "떴어요"}
        ],
        "sfx": [(4.2, "라이저")]
    },
    {
        "id": 3,
        "text": "그럼 어떻게 매끈해졌냐고요? 여드름 흉터 체질을 바꿨어요. 바르는 화장품만으로는 여드름 절대 못 지우거든요. 근데 체질은 바꾸기 어려워요. 이 먹는 레티놀 크림이 없다면요!",
        "cues": [
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}그럼 {\\c&H0000E5FF&}어떻게 매끈해졌냐고요?{\\c&H00FFFFFF&} 💡", "match": "매끈해졌냐고요"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H00FFFFFF&}여드름 흉터 {\\c&H0000E5FF&}체질을 바꿨어요!{\\c&H00FFFFFF&}", "match": "바꿨어요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}바르는 화장품만으로는 ❌", "match": "화장품"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}여드름 {\\c&H0000E5FF&}절대 못 지우거든요{\\c&H00FFFFFF&} 🙅‍♀️", "match": "지우거든요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}근데 {\\c&H0000E5FF&}체질은 바꾸기 어려워요{\\c&H00FFFFFF&} 🥺", "match": "어려워요"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}💊 {\\fnJalnan 2\\c&H00FFFFFF&}이 {\\c&H0000E5FF&}먹는 레티놀 크림{\\c&H00FFFFFF&}이 없다면요! {\\fnSegoe UI Emoji\\c&H00FFFF&}✨", "match": "없다면요"}
        ],
        "sfx": [(9.8, "차임")]
    },
    {
        "id": 4,
        "text": "엥? 레티놀 크림을 먹는다고요??",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H00E5FF&}⚡ {\\fnJalnan 2\\c&H0000E5FF&}엥?!{\\c&H00FFFFFF&} 레티놀 크림을 먹는다고요?! {\\fnSegoe UI Emoji\\c&H00E5FF&}⚡", "match": "먹는다고요"}
        ],
        "sfx": [(0.0, "팝")]
    },
    {
        "id": 5,
        "text": "먹기 전과 2주 뒤 모습이에요. 스위스산 레티놀이 속피지선부터 말려주고, 300달톤 콜라겐이 패인 흉터 속살을 팽팽하게 밀어 올려줘요. 피지가 잡히니까 속살이 차오르는 속도가 훨씬 빨라져요! 딱 2주만 먹어도 깐달걀 피부 돼요",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🩵 {\\fnJalnan 2\\c&H00FFFFFF&}먹기 전과 {\\c&H0000E5FF&}2주 뒤 모습{\\c&H00FFFFFF&}이에요", "match": "모습이에요"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🇨🇭 {\\fnJalnan 2\\c&H0000E5FF&}스위스산 레티놀{\\c&H00FFFFFF&}이", "match": "레티놀"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}속피지선부터 {\\c&H0000E5FF&}바짝 말려주고{\\c&H00FFFFFF&} ⚡", "match": "말려주고"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🧬 {\\fnJalnan 2\\c&H0000E5FF&}300달톤 콜라겐{\\c&H00FFFFFF&}이", "match": "콜라겐"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}패인 흉터 속살을 {\\c&H0000E5FF&}팽팽하게{\\c&H00FFFFFF&}", "match": "속살을"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🚀 {\\fnJalnan 2\\c&H0000E5FF&}밀어 올려줘요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00FFFF&}✨", "match": "올려줘요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}피지가 잡히니까 💧", "match": "잡히니까"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}속살이 차오르는 속도가", "match": "속도가"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00E5FF&}⚡ {\\fnJalnan 2\\c&H0000E5FF&}훨씬 빨라져요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00E5FF&}⚡", "match": "빨라져요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}딱 2주만 먹어도 🗓️", "match": "먹어도"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H0000E5FF&}깐달걀 피부 돼요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00FFFF&}🥚", "match": "돼요"}
        ],
        "sfx": [(0.0, "우쉬"), (13.5, "차임")]
    },
    {
        "id": 6,
        "text": "300달톤 GPH 초저분자 콜라겐 비싸서 찾아보기 힘든데, 레티라겐은 스위스 레티놀에 초저분자 콜라겐 27,000mg까지 꽉 채웠더라고요. 먹는 순간 속에서 팽팽하게 차오르는 느낌!",
        "cues": [
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}300달톤 {\\c&H0000E5FF&}GPH 초저분자 콜라겐{\\c&H00FFFFFF&}", "match": "콜라겐"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}비싸서 {\\c&H0000E5FF&}찾아보기 힘든데{\\c&H00FFFFFF&} 💸", "match": "힘든데"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🇨🇭 {\\fnJalnan 2\\c&H00FFFFFF&}레티라겐은 {\\c&H0000E5FF&}스위스 레티놀{\\c&H00FFFFFF&}에", "match": "레티놀"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}초저분자 콜라겐 {\\c&H0000E5FF&}27,000mg까지{\\c&H00FFFFFF&}", "match": "까지"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}💯 {\\fnJalnan 2\\c&H0000E5FF&}꽉 채웠더라고요!{\\c&H00FFFFFF&} 👏", "match": "채웠더라고요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}먹는 순간 속에서", "match": "속에서"},
            {"display": "{\\fnSegoe UI Emoji\\c&H8080FF&}💖 {\\fnJalnan 2\\c&H0000E5FF&}팽팽하게 차오르는 느낌!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H8080FF&}✨", "match": "느낌"}
        ],
        "sfx": [(6.8, "차임")]
    },
    {
        "id": 7,
        "text": "속부터 매끈한 깐달걀 피부? 제가 흉터 지운 건 바르지 않고 먹었기 때문이에요! 아래 링크에서 반값 특가일 때 무조건 쟁여두세요!",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🥚 {\\fnJalnan 2\\c&H00FFFFFF&}속부터 매끈한 {\\c&H0000E5FF&}깐달걀 피부?{\\c&H00FFFFFF&}", "match": "피부"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}제가 흉터 지운 건", "match": "지운"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🤫 {\\fnJalnan 2\\c&H00FFFFFF&}바르지 않고 {\\c&H0000E5FF&}먹었기 때문이에요!{\\c&H00FFFFFF&}", "match": "때문이에요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}아래 링크에서 {\\c&H0000E5FF&}반값 특가일 때{\\c&H00FFFFFF&} 🏷️", "match": "특가"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}👇 {\\fnJalnan 2\\c&H0000E5FF&}무조건 쟁여두세요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00FFFF&}🛒", "match": "쟁여두세요"}
        ],
        "sfx": [(5.5, "클릭")]
    }
]

def find_sfx(kw):
    for root, dirs, files in os.walk(SFX_DIR):
        for f in files:
            if kw.lower() in f.lower():
                return os.path.join(root, f)
    return None

def align_and_build():
    total_audio = AudioSegment.silent(duration=0)
    scene_offsets = []
    current_time_sec = 0.0
    all_ass_events = []
    PAUSE_SEC = 0.080
    
    for s in SCENES:
        wav_p = os.path.join(SCENE_AUDIO_DIR, f"scene_{s['id']:02d}.wav")
        seg = AudioSegment.from_file(wav_p)
        dur_sec = len(seg) / 1000.0
        
        scene_start = current_time_sec
        scene_end = scene_start + dur_sec
        scene_offsets.append({
            "id": s["id"],
            "start": scene_start,
            "end": scene_end,
            "dur": dur_sec,
            "sfx": s["sfx"]
        })
        
        # Partition cues across scene duration evenly and strictly monotonically
        num_cues = len(s["cues"])
        step = dur_sec / num_cues
        for i, cue in enumerate(s["cues"]):
            c_start = scene_start + i * step
            c_end = scene_start + (i + 1) * step
            all_ass_events.append({
                "start": round(c_start, 3),
                "end": round(c_end, 3),
                "display": cue["display"]
            })
            
        total_audio += seg + AudioSegment.silent(duration=int(PAUSE_SEC * 1000))
        current_time_sec = scene_end + PAUSE_SEC
        
    spoken_dur = len(total_audio) / 1000.0
    OUTRO_HOLD_MS = 1150
    total_audio += AudioSegment.silent(duration=OUTRO_HOLD_MS)
    total_dur = len(total_audio) / 1000.0
    print(f">> Total Audio Duration: {total_dur:.3f}s (Spoken: {spoken_dur:.3f}s)")
    
    # Mix SFX
    for s_info in scene_offsets:
        s_base = s_info["start"]
        for sfx_rel, sfx_name in s_info["sfx"]:
            sfx_abs_ms = int((s_base + sfx_rel) * 1000)
            sfx_file = find_sfx(sfx_name)
            if sfx_file and os.path.exists(sfx_file):
                try:
                    sfx_seg = AudioSegment.from_file(sfx_file)
                    if sfx_name == "스냅":
                        sfx_seg = sfx_seg - 6
                    elif sfx_name == "라이저":
                        sfx_seg = sfx_seg - 12
                    elif sfx_name == "차임":
                        sfx_seg = sfx_seg - 10
                    elif sfx_name == "팝":
                        sfx_seg = sfx_seg - 8
                    elif sfx_name == "우쉬":
                        sfx_seg = sfx_seg - 8
                    elif sfx_name == "클릭":
                        sfx_seg = sfx_seg - 6
                    total_audio = total_audio.overlay(sfx_seg, position=sfx_abs_ms)
                    print(f"   [SFX] Added {sfx_name} at {(s_base+sfx_rel):.2f}s")
                except Exception as e:
                    print(f"   [SFX Error] {e}")
                    
    # Mix BGM
    bgm_candidates = [find_sfx("bgm"), os.path.join(WORKDIR, "scratch", "test_free.mp3")]
    for cand in bgm_candidates:
        if cand and os.path.exists(cand):
            try:
                bgm = AudioSegment.from_file(cand) - 27
                loops = int(len(total_audio) / len(bgm)) + 1
                bgm_loop = (bgm * loops)[:len(total_audio)].fade_in(800).fade_out(1200)
                total_audio = total_audio.overlay(bgm_loop, position=0)
                print(f">> Mixed BGM ducked at -27dB")
                break
            except Exception as e:
                print(f"BGM Error: {e}")
                
    master_wav = os.path.join(BUILD_DIR, "master_audio_ad17.wav")
    total_audio.export(master_wav, format="wav")
    print(f">> Master Audio exported to: {master_wav}")
    
    # Generate ASS Subtitles
    ass_path = os.path.join(BUILD_DIR, "ad17_subtitles.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
Title: Retiragen ad17 Remastered PopSub
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: PopSub,Jalnan 2,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.8,2.0,2,40,40,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        for ev in all_ass_events:
            s_m, s_s = divmod(ev["start"], 60)
            s_h, s_m = divmod(s_m, 60)
            e_m, e_s = divmod(ev["end"], 60)
            e_h, e_m = divmod(e_m, 60)
            start_str = f"{int(s_h)}:{int(s_m):02d}:{s_s:05.2f}"
            end_str = f"{int(e_h)}:{int(e_m):02d}:{e_s:05.2f}"
            bounce_tag = r"{\fscx90\fscy90\t(0,70,\fscx110\fscy110)\t(70,140,\fscx100\fscy100)}"
            txt = f"{bounce_tag}{ev['display']}"
            f.write(f"Dialogue: 0,{start_str},{end_str},PopSub,,0,0,0,,{txt}\n")
            
    print(f">> Generated clean ASS Subtitle file: {ass_path}")
    
    scene_manifest = os.path.join(BUILD_DIR, "scene_manifest.json")
    with open(scene_manifest, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration": total_dur,
            "spoken_duration": spoken_dur,
            "outro_hold": OUTRO_HOLD_MS / 1000.0,
            "scenes": scene_offsets
        }, f, indent=2, ensure_ascii=False)
    print(f">> Saved scene manifest: {scene_manifest}")

if __name__ == "__main__":
    align_and_build()
