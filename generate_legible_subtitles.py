"""
Generate Maximum-Legibility Subtitles (Jalnan 2 + Clean 5.0px Outline + Spring Pop Bounce)
Synchronized with Fish Audio (47.361s)
"""

import os
import sys
import json

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
BUILD_DIR = os.path.join(WORKDIR, "build_ad17_fish")
SCENE_DIR = os.path.join(BUILD_DIR, "fish_scenes")

SCENES = [
    {
        "id": 1,
        "text": "제가 하얘진 비결이요?",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🌸 {\\fnJalnan 2\\c&H00FFFFFF&}제가 하얘진 {\\c&H0000E5FF&}비결{\\c&H00FFFFFF&}이요? {\\fnSegoe UI Emoji\\c&H8080FF&}🌸"}
        ]
    },
    {
        "id": 2,
        "text": "저 작년에 피부과 프락셀만 10번 넘게 받았어요. 그래서 요철 다 메꿔졌냐고요? 아뇨, 붉은기만 오래 가고 화장은 여전히 떴어요.",
        "cues": [
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}저 작년에 {\\c&H0000E5FF&}피부과 프락셀{\\c&H00FFFFFF&}만"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🏥 {\\fnJalnan 2\\c&H0000E5FF&}10번 넘게{\\c&H00FFFFFF&} 받았어요"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}그래서 {\\c&H0000E5FF&}요철 다{\\c&H00FFFFFF&} 메꿔졌냐고요? 🤔"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}아뇨, {\\c&H0000E5FF&}붉은기만{\\c&H00FFFFFF&} 오래 가고"},
            {"display": "{\\fnSegoe UI Emoji\\c&H80FFFF&}💦 {\\fnJalnan 2\\c&H00FFFFFF&}화장은 {\\c&H0000E5FF&}여전히 떴어요 😭{\\c&H00FFFFFF&}"}
        ]
    },
    {
        "id": 3,
        "text": "그럼 어떻게 매끈해졌냐고요? 여드름 흉터 체질을 바꿨어요. 바르는 화장품만으로는 여드름 절대 못 지우거든요. 근데 체질은 바꾸기 어려워요. 이 먹는 레티놀 크림이 없다면요!",
        "cues": [
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}그럼 {\\c&H0000E5FF&}어떻게 매끈해졌냐고요?{\\c&H00FFFFFF&} 💡"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H00FFFFFF&}여드름 흉터 {\\c&H0000E5FF&}체질을 바꿨어요!{\\c&H00FFFFFF&}"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}바르는 화장품만으로는 ❌"},
            {"display": "{\\fnJalnan 2\\c&H0000E5FF&}여드름 절대 못 지우거든요!{\\c&H00FFFFFF&} 🙅‍♀️"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}근데 {\\c&H0000E5FF&}체질은 바꾸기 어려워요{\\c&H00FFFFFF&} 🥺"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}💊 {\\fnJalnan 2\\c&H00FFFFFF&}이 {\\c&H0000E5FF&}먹는 레티놀 크림{\\c&H00FFFFFF&}이 없다면요! {\\fnSegoe UI Emoji\\c&H00FFFF&}✨"}
        ]
    },
    {
        "id": 4,
        "text": "엥? 레티놀 크림을 먹는다고요??",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H00E5FF&}⚡ {\\fnJalnan 2\\c&H0000E5FF&}엥?!{\\c&H00FFFFFF&} 레티놀 크림을 먹는다고요?! {\\fnSegoe UI Emoji\\c&H00E5FF&}⚡"}
        ]
    },
    {
        "id": 5,
        "text": "먹기 전과 2주 뒤 모습이에요. 스위스산 레티놀이 속피지선부터 말려주고, 300달톤 콜라겐이 패인 흉터 속살을 팽팽하게 밀어 올려줘요. 피지가 잡히니까 속살이 차오르는 속도가 훨씬 빨라져요! 딱 2주만 먹어도 깐달걀 피부 돼요",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H8080FF&}🩵 {\\fnJalnan 2\\c&H00FFFFFF&}먹기 전과 {\\c&H0000E5FF&}2주 뒤 모습{\\c&H00FFFFFF&}이에요"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🇨🇭 {\\fnJalnan 2\\c&H0000E5FF&}스위스산 레티놀{\\c&H00FFFFFF&}이"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}속피지선부터 {\\c&H0000E5FF&}바짝 말려주고{\\c&H00FFFFFF&} ⚡"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🧬 {\\fnJalnan 2\\c&H0000E5FF&}300달톤 콜라겐{\\c&H00FFFFFF&}이"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}패인 흉터 속살을 {\\c&H0000E5FF&}팽팽하게{\\c&H00FFFFFF&}"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🚀 {\\fnJalnan 2\\c&H0000E5FF&}밀어 올려줘요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00FFFF&}✨"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}피지가 잡히니까 💧"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}속살이 차오르는 속도가"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00E5FF&}⚡ {\\fnJalnan 2\\c&H0000E5FF&}훨씬 빨라져요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00E5FF&}⚡"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}딱 2주만 먹어도 🗓️"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}✨ {\\fnJalnan 2\\c&H0000E5FF&}깐달걀 피부 돼요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00FFFF&}🥚"}
        ]
    },
    {
        "id": 6,
        "text": "300달톤 GPH 초저분자 콜라겐 비싸서 찾아보기 힘든데, 레티라겐은 스위스 레티놀에 초저분자 콜라겐 27,000mg까지 꽉 채웠더라고요. 먹는 순간 속에서 팽팽하게 차오르는 느낌!",
        "cues": [
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}300달톤 {\\c&H0000E5FF&}GPH 초저분자 콜라겐{\\c&H00FFFFFF&}"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}비싸서 {\\c&H0000E5FF&}찾아보기 힘든데{\\c&H00FFFFFF&} 💸"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🇨🇭 {\\fnJalnan 2\\c&H00FFFFFF&}레티라겐은 {\\c&H0000E5FF&}스위스 레티놀{\\c&H00FFFFFF&}에"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}초저분자 콜라겐 {\\c&H0000E5FF&}27,000mg까지{\\c&H00FFFFFF&}"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}💯 {\\fnJalnan 2\\c&H0000E5FF&}꽉 채웠더라고요!{\\c&H00FFFFFF&} 👏"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}먹는 순간 속에서"},
            {"display": "{\\fnSegoe UI Emoji\\c&H8080FF&}💖 {\\fnJalnan 2\\c&H0000E5FF&}팽팽하게 차오르는 느낌!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H8080FF&}✨"}
        ]
    },
    {
        "id": 7,
        "text": "속부터 매끈한 깐달걀 피부? 제가 흉터 지운 건 바르지 않고 먹었기 때문이에요! 아래 링크에서 반값 특가일 때 무조건 쟁여두세요!",
        "cues": [
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🥚 {\\fnJalnan 2\\c&H00FFFFFF&}속부터 매끈한 {\\c&H0000E5FF&}깐달걀 피부?{\\c&H00FFFFFF&}"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}제가 흉터 지운 건"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}🤫 {\\fnJalnan 2\\c&H00FFFFFF&}바르지 않고 {\\c&H0000E5FF&}먹었기 때문이에요!{\\c&H00FFFFFF&}"},
            {"display": "{\\fnJalnan 2\\c&H00FFFFFF&}아래 링크에서 {\\c&H0000E5FF&}반값 특가일 때{\\c&H00FFFFFF&} 🏷️"},
            {"display": "{\\fnSegoe UI Emoji\\c&H00FFFF&}👇 {\\fnJalnan 2\\c&H0000E5FF&}무조건 쟁여두세요!{\\c&H00FFFFFF&} {\\fnSegoe UI Emoji\\c&H00FFFF&}🛒"}
        ]
    }
]

manifest_p = os.path.join(BUILD_DIR, "fish_scene_manifest.json")
with open(manifest_p, "r", encoding="utf-8") as f:
    manifest = json.load(f)

scenes_info = manifest["scenes"]

all_ass_events = []
for s_idx, s in enumerate(SCENES):
    s_info = scenes_info[s_idx]
    s_start = s_info["start"]
    s_dur = s_info["dur"]
    num_cues = len(s["cues"])
    step = s_dur / num_cues
    
    for i, cue in enumerate(s["cues"]):
        c_start = s_start + i * step
        c_end = s_start + (i + 1) * step
        all_ass_events.append({
            "start": round(c_start, 3),
            "end": round(c_end, 3),
            "display": cue["display"]
        })

ass_path = os.path.join(BUILD_DIR, "ad17_fish_subtitles.ass")
with open(ass_path, "w", encoding="utf-8") as f:
    f.write("""[Script Info]
Title: Retiragen ad17 Fish Legible PopSub
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: PopSub,Jalnan 2,68,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5.0,2.0,2,40,40,340,1

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

print(f">> High Legibility Jalnan 2 Subtitles Generated: {ass_path}")
