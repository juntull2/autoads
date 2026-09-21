"""
caption.py — Caption Engine & Keyword Detector
=================================================
Two responsibilities:
  1. KeywordDetector: Scans Korean subtitle text and tags words with
     semantic categories (number, impact, positive, product, cta).
  2. CaptionEngine: Builds ASS Dialogue line text with appropriate
     animation tags based on scene purpose + keyword categories.

Design goals:
  - Zero external API dependencies (pure rule-based).
  - All animations expressed as ASS \\t() override tags for maximum
    compatibility with libass / FFmpeg subtitles filter.
  - Backward compatible: v9 pre-tagged display strings pass through unchanged.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

from autoads_engine.scene_model import CaptionAnimStyle, ScenePurpose


# ---------------------------------------------------------------------------
# Keyword categories and patterns
# ---------------------------------------------------------------------------

# Number patterns: digits with common Korean quantity suffixes
_RE_NUMBER = re.compile(
    r'\d+(?:[,.]\d+)*(?:%|퍼센트|배|주|일|년|개|회|번|g|mg|ml|달톤|원)?|'
    r'반값|절반|1\+1|무료'
)

# Impact/negative words → SHAKE or strong color
_IMPACT_WORDS = {
    '터지', '뒤집', '파였', '푹', '아예', '심할', '뒤집어', '못', '안',
    '절대', '어려워', '힘든', '없', '안돼', '실패', '싫', '걱정'
}

# Positive/result words → highlight color + PUNCH
_POSITIVE_WORDS = {
    '매끈', '깐달걀', '팽팽', '제로', '차오르', '빨라져', '유지', '됐어',
    '됐', '이식', '완벽', '투명', '맑', '환해', '좋', '최고', '대박',
    '효과', '놀라', '신기', '말려주', '메워주'
}

# Product/brand words → highlight color
_PRODUCT_WORDS = {
    '레티라겐', '레티놀', '콜라겐', '달톤', '스위스', 'GPH', '초저분자',
    '모공', '피지선', '진피', '프락셀', '속피지'
}

# CTA / offer words → PUNCH + strong color
_CTA_WORDS = {
    '링크', '할인', '반값', '특가', '쟁여', '무료', '확인', '비밀',
    '한정', '지금', '빨리', '서두'
}

# Duration / frequency words → number treatment
_DURATION_WORDS = {
    '한 달', '2주', '딱', '하루', '매일', '꾸준히', '30일', '14일'
}


@dataclass
class WordTag:
    """A tagged word or phrase with its semantic category."""
    text: str
    category: str   # 'number' | 'impact' | 'positive' | 'product' | 'cta' | 'normal'
    anim_override: Optional[CaptionAnimStyle] = None


class KeywordDetector:
    """
    Analyzes Korean subtitle text and returns a list of WordTags.
    Operates on raw text (no ASS override tags).
    """

    def analyze(self, text: str) -> List[WordTag]:
        """
        Returns word-level tags. Currently phrase-level matching.
        """
        # Strip existing ASS override tags for analysis
        clean = re.sub(r'\{[^}]+\}', '', text)
        tags: List[WordTag] = []

        # Find numbers
        for m in _RE_NUMBER.finditer(clean):
            tags.append(WordTag(text=m.group(), category='number',
                                anim_override=CaptionAnimStyle.NUMBER_POP))

        # Impact words
        for w in _IMPACT_WORDS:
            if w in clean:
                tags.append(WordTag(text=w, category='impact',
                                    anim_override=CaptionAnimStyle.SHAKE))

        # Positive words
        for w in _POSITIVE_WORDS:
            if w in clean:
                tags.append(WordTag(text=w, category='positive',
                                    anim_override=CaptionAnimStyle.PUNCH))

        # Product words
        for w in _PRODUCT_WORDS:
            if w in clean:
                tags.append(WordTag(text=w, category='product',
                                    anim_override=CaptionAnimStyle.POP))

        # CTA words
        for w in _CTA_WORDS:
            if w in clean:
                tags.append(WordTag(text=w, category='cta',
                                    anim_override=CaptionAnimStyle.PUNCH))

        return tags

    def dominant_anim(self, text: str, fallback: CaptionAnimStyle) -> CaptionAnimStyle:
        """
        Returns the most semantically important animation for a cue,
        based on the highest-priority keyword found.
        Priority: number > cta > impact > positive > product > fallback
        """
        tags = self.analyze(text)
        priority_order = ['number', 'cta', 'impact', 'positive', 'product']
        for cat in priority_order:
            for t in tags:
                if t.category == cat and t.anim_override:
                    return t.anim_override
        return fallback


# ---------------------------------------------------------------------------
# ASS Animation Library
# ---------------------------------------------------------------------------
# Each entry is a function that returns an ASS override tag prefix string.
# Parameters:
#   duration_ms: display duration for timing calculations (rarely needed)
#   intensity:   0.0~1.0 scaling for animation strength

def _anim_pop(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Standard CapCut spring pop: 90 → 110 → 100"""
    s1 = int(90 - 5 * (1 - intensity))    # start scale
    p1 = int(110 + 5 * intensity)         # overshoot
    t1 = int(60 + 20 * (1 - intensity))   # time to peak ms
    t2 = t1 + 70
    return rf"{{\fscx{s1}\fscy{s1}\t(0,{t1},\fscx{p1}\fscy{p1})\t({t1},{t2},\fscx100\fscy100)}}"


def _anim_punch(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Aggressive punch: 75 → 125 → 100 — for emphasis words"""
    s1 = int(75 - 10 * (1 - intensity))
    p1 = int(120 + 10 * intensity)
    t1 = int(45 + 15 * (1 - intensity))
    t2 = t1 + 80
    return rf"{{\fscx{s1}\fscy{s1}\t(0,{t1},\fscx{p1}\fscy{p1})\t({t1},{t2},\fscx100\fscy100)}}"


def _anim_bounce(duration_ms: float = 800, intensity: float = 1.0) -> str:
    """Multi-stage elastic bounce: 90 → 112 → 96 → 104 → 100"""
    p1 = int(112 + 5 * intensity)
    return (
        rf"{{\fscx90\fscy90"
        rf"\t(0,60,\fscx{p1}\fscy{p1})"
        rf"\t(60,120,\fscx96\fscy96)"
        rf"\t(120,180,\fscx104\fscy104)"
        rf"\t(180,240,\fscx100\fscy100)}}"
    )


def _anim_slide_up(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Slide from below + fade in"""
    offset = int(60 + 20 * intensity)
    t1 = int(100 + 40 * (1 - intensity))
    return (
        rf"{{\an2\alpha&HFF&\pos(540,{1540 + offset})"
        rf"\t(0,{t1},\alpha&H00&\pos(540,1540))}}"
    )


def _anim_slide_down(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Slide from above + fade in"""
    offset = int(60 + 20 * intensity)
    t1 = int(100 + 40 * (1 - intensity))
    return (
        rf"{{\an2\alpha&HFF&\pos(540,{1540 - offset})"
        rf"\t(0,{t1},\alpha&H00&\pos(540,1540))}}"
    )


def _anim_shake(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Horizontal shake for agitation/impact — ±5px sinusoidal"""
    a = int(5 + 4 * intensity)
    return (
        rf"{{\pos(540,1540)"
        rf"\t(0,50,\pos({540+a},1540))"
        rf"\t(50,100,\pos({540-a},1540))"
        rf"\t(100,150,\pos({540+a//2},1540))"
        rf"\t(150,200,\pos(540,1540))}}"
    )


def _anim_number_pop(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Large dramatic pop for numbers/stats: 60 → 130 → 100"""
    p1 = int(128 + 10 * intensity)
    t1 = int(50 + 10 * (1 - intensity))
    t2 = t1 + 90
    return rf"{{\fscx60\fscy60\t(0,{t1},\fscx{p1}\fscy{p1})\t({t1},{t2},\fscx100\fscy100)}}"


def _anim_scale_in(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Simple scale from 0 to 100"""
    t1 = int(80 + 40 * (1 - intensity))
    return rf"{{\fscx10\fscy10\t(0,{t1},\fscx100\fscy100)}}"


def _anim_fade_in(duration_ms: float = 700, intensity: float = 1.0) -> str:
    """Alpha fade in"""
    t1 = int(120 + 60 * (1 - intensity))
    return rf"{{\alpha&HFF&\t(0,{t1},\alpha&H00&)}}"


def _anim_none(*args, **kwargs) -> str:
    return ""


_ANIM_FUNCS = {
    CaptionAnimStyle.POP:        _anim_pop,
    CaptionAnimStyle.PUNCH:      _anim_punch,
    CaptionAnimStyle.BOUNCE:     _anim_bounce,
    CaptionAnimStyle.SLIDE_UP:   _anim_slide_up,
    CaptionAnimStyle.SLIDE_DOWN: _anim_slide_down,
    CaptionAnimStyle.SHAKE:      _anim_shake,
    CaptionAnimStyle.NUMBER_POP: _anim_number_pop,
    CaptionAnimStyle.SCALE_IN:   _anim_scale_in,
    CaptionAnimStyle.FADE_IN:    _anim_fade_in,
    CaptionAnimStyle.NONE:       _anim_none,
}


# ---------------------------------------------------------------------------
# ASS Color constants (BGR format as used by libass)
# ---------------------------------------------------------------------------
COLOR_WHITE     = "&H00FFFFFF"
COLOR_YELLOW    = "&H0000E5FF"   # highlight keyword (neon yellow)
COLOR_ORANGE    = "&H000060FF"   # impact/negative
COLOR_MINT      = "&H00AAFFAA"   # number/stat
COLOR_LAVENDER  = "&H00FF80C0"   # CTA/offer


def _keyword_color(category: str) -> str:
    return {
        'positive': COLOR_YELLOW,
        'impact':   COLOR_ORANGE,
        'number':   COLOR_MINT,
        'cta':      COLOR_YELLOW,
        'product':  COLOR_YELLOW,
        'normal':   COLOR_WHITE,
    }.get(category, COLOR_WHITE)


def _word_anim_tags(category: str, intensity: float = 1.0) -> Tuple[str, str]:
    """
    Returns (open_tags, close_tags) for word/phrase-level independent ASS animation.
    open_tags includes font scaling and \\t transition, plus color.
    close_tags resets font scaling and color back to baseline.
    """
    color = _keyword_color(category)
    if category == 'number':
        p1 = int(128 + 10 * intensity)
        open_tag = rf"{{\c{color}&\fscx75\fscy75\t(0,60,\fscx{p1}\fscy{p1})\t(60,140,\fscx100\fscy100)}}"
    elif category == 'impact':
        open_tag = rf"{{\c{color}&\fscx118\fscy118\t(0,40,\fscx92\fscy92)\t(40,90,\fscx108\fscy108)\t(90,140,\fscx100\fscy100)}}"
    elif category == 'positive':
        p1 = int(122 + 8 * intensity)
        open_tag = rf"{{\c{color}&\fscx82\fscy82\t(0,55,\fscx{p1}\fscy{p1})\t(55,120,\fscx100\fscy100)}}"
    elif category == 'cta':
        p1 = int(128 + 10 * intensity)
        open_tag = rf"{{\c{color}&\fscx78\fscy78\t(0,50,\fscx{p1}\fscy{p1})\t(50,115,\fscx100\fscy100)}}"
    elif category == 'product':
        p1 = int(116 + 6 * intensity)
        open_tag = rf"{{\c{color}&\fscx88\fscy88\t(0,60,\fscx{p1}\fscy{p1})\t(60,120,\fscx100\fscy100)}}"
    else:
        open_tag = rf"{{\c{color}&}}"
    close_tag = r"{\fscx100\fscy100\c&H00FFFFFF&}"
    return open_tag, close_tag


# ---------------------------------------------------------------------------
# Caption Engine
# ---------------------------------------------------------------------------

class CaptionEngine:
    """
    Builds ASS Dialogue line text from subtitle cues.

    Main entry points:
        build_anim_prefix()  — returns the opening ASS override tag string
        build_ass_line()     — returns full ASS event line text

    Supports true word/phrase-level independent ASS animation for detected keywords,
    ensuring keywords visually pop beyond simple color tinting.
    """

    def __init__(
        self,
        intensity_scale: float = 1.0,
        detector: Optional[KeywordDetector] = None,
    ):
        self.intensity_scale = intensity_scale
        self.detector = detector or KeywordDetector()

    def build_anim_prefix(
        self,
        anim: CaptionAnimStyle,
        duration_ms: float = 700,
        scene_intensity: float = 1.0,
    ) -> str:
        """
        Returns the ASS override tag prefix for a given animation style.
        Intensity is combined from scene + global scale (capped at 1.5).
        """
        effective = min(1.5, scene_intensity * self.intensity_scale)
        fn = _ANIM_FUNCS.get(anim, _anim_pop)
        return fn(duration_ms=duration_ms, intensity=effective)

    def choose_anim(
        self,
        raw_text: str,
        scene_purpose: ScenePurpose,
        fallback_anim: CaptionAnimStyle,
    ) -> CaptionAnimStyle:
        """
        Choose the best animation for a cue based on keyword analysis.
        If no strong keyword is found, falls back to scene-level default.
        """
        return self.detector.dominant_anim(raw_text, fallback_anim)

    def _enhance_existing_tags(self, display_text: str, scene_intensity: float = 1.0) -> str:
        """
        Enhances existing inline color tags in display_text with word-level animation.
        e.g., '{\\c&H0000E5FF&}제로{\\c&H00FFFFFF&}' -> adds scale overshoot \\t tags.
        """
        effective = min(1.5, scene_intensity * self.intensity_scale)
        pattern = re.compile(r'(\{\\c&H[0-9a-fA-F]+&\})([^{}]+?)(\{\\c&H[0-9a-fA-F]+&\})')

        def repl(m):
            open_part, word, close_part = m.group(1), m.group(2), m.group(3)
            tags = self.detector.analyze(word)
            cat = tags[0].category if tags else 'positive'
            open_anim, close_anim = _word_anim_tags(cat, intensity=effective)
            anim_inside = open_anim.strip('{}')
            return f"{{{anim_inside}}}{word}{{\\fscx100\\fscy100\\c&H00FFFFFF&}}"

        return pattern.sub(repl, display_text)

    def _apply_word_anim(
        self,
        text: str,
        scene_intensity: float = 1.0,
    ) -> str:
        """
        Scans plain text segments for keywords and wraps them with word-level ASS transform animations.
        Preserves existing curly-braced tags untouched.
        """
        effective = min(1.5, scene_intensity * self.intensity_scale)
        tags = self.detector.analyze(text)

        tokens = re.split(r'(\{[^}]+\})', text)
        new_tokens = []
        seen = set()

        for tok in tokens:
            if tok.startswith('{') and tok.endswith('}'):
                new_tokens.append(tok)
            else:
                s = tok
                for tag in sorted(tags, key=lambda t: -len(t.text)):
                    if tag.text in s and tag.text not in seen:
                        seen.add(tag.text)
                        open_tag, close_tag = _word_anim_tags(tag.category, intensity=effective)
                        s = s.replace(tag.text, f"{open_tag}{tag.text}{close_tag}", 1)
                new_tokens.append(s)

        return "".join(new_tokens)

    def build_ass_text(
        self,
        raw_text: str,
        display_text: str,
        anim: CaptionAnimStyle,
        duration_ms: float,
        scene_intensity: float,
        scene_purpose: ScenePurpose,
        auto_keyword_color: bool = True,
    ) -> str:
        """
        Returns the full ASS text field for a Dialogue line.

        If display_text already contains ASS override tags (v9 compat),
        we enhance existing keyword spans with word animations and prepend the anim prefix.
        Otherwise, we generate the text with auto word-level animation and coloring.
        """
        final_anim = self.choose_anim(raw_text, scene_purpose, anim)
        prefix = self.build_anim_prefix(final_anim, duration_ms, scene_intensity)

        has_existing_tags = re.search(r'\{\\[a-zA-Z]', display_text) is not None
        if has_existing_tags:
            if auto_keyword_color:
                display_text = self._enhance_existing_tags(display_text, scene_intensity)
            return prefix + display_text

        # Auto word animation and color in plain text
        if auto_keyword_color:
            tagged = self._apply_word_anim(raw_text, scene_intensity)
        else:
            tagged = raw_text

        return prefix + tagged

    def _auto_color(self, text: str) -> str:
        """Legacy helper maintained for backward compatibility."""
        return self._apply_word_anim(text, 1.0)

    # -----------------------------------------------------------------------
    # ASS file helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def format_time(sec: float) -> str:
        """Format seconds as ASS timestamp H:MM:SS.cc"""
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    @staticmethod
    def ass_header(title: str = "AutoAds v10") -> str:
        return f"""[Script Info]
Title: {title}
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
"""

    def build_dialogue_line(
        self,
        abs_start: float,
        abs_end: float,
        text_field: str,
        layer: int = 0,
        style: str = "PopSub",
    ) -> str:
        """Build a complete ASS Dialogue line."""
        return (
            f"Dialogue: {layer},"
            f"{self.format_time(abs_start)},"
            f"{self.format_time(abs_end)},"
            f"{style},,0,0,0,,{text_field}\n"
        )
