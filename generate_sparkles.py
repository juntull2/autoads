import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
FPS = 30
DURATION = 3
TOTAL_FRAMES = FPS * DURATION
OUT_DIR = "build_temp_v4/sparkles"
os.makedirs(OUT_DIR, exist_ok=True)

random.seed(333)
# 16 beauty sparkles around cheeks, bridge of nose, forehead, jawline
positions = [
    (340, 700), (720, 680), (540, 560), (400, 850),
    (670, 840), (280, 760), (790, 750), (460, 620),
    (620, 630), (530, 780), (370, 520), (710, 530),
    (480, 920), (600, 910), (300, 620), (770, 620)
]
sparkles = []
for (x, y) in positions:
    max_r = random.uniform(25, 50)
    speed = random.uniform(1.2, 2.6)
    phase = random.uniform(0, math.pi * 2)
    # Luxury cosmetic sparkle colors: champagne gold, diamond pure white, soft sakura pink
    color = random.choice([
        (255, 255, 240), # diamond white
        (255, 245, 180), # champagne gold
        (255, 230, 245), # gentle sakura glow
        (255, 250, 200), # warm radiant
    ])
    sparkles.append((x, y, max_r, speed, phase, color))

def make_sparkle_stamp(r, color, alpha):
    # Pre-render a high quality soft glowing sparkle stamp
    size = int(r * 4.5)
    if size % 2 == 0:
        size += 1
    stamp = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(stamp)
    cx, cy = size // 2, size // 2
    
    # 1. Soft glowing aura with blur
    aura = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d_aura = ImageDraw.Draw(aura)
    ar = r * 1.3
    d_aura.ellipse([cx - ar, cy - ar, cx + ar, cy + ar], fill=color + (int(alpha * 0.5),))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=max(2.0, r * 0.35)))
    stamp.alpha_composite(aura)
    
    # 2. Horizontal and vertical radiant rays
    ray_len = r * 1.9
    ray_w = max(1.5, r * 0.12)
    d.line([(cx - ray_len, cy), (cx + ray_len, cy)], fill=color + (int(alpha * 0.9),), width=int(ray_w * 2))
    d.line([(cx, cy - ray_len), (cx, cy + ray_len)], fill=color + (int(alpha * 0.9),), width=int(ray_w * 2))
    
    # 3. Subtle diagonal rays
    diag = r * 0.75
    d.line([(cx - diag, cy - diag), (cx + diag, cy + diag)], fill=color + (int(alpha * 0.5),), width=max(1, int(ray_w)))
    d.line([(cx - diag, cy + diag), (cx + diag, cy - diag)], fill=color + (int(alpha * 0.5),), width=max(1, int(ray_w)))
    
    # 4. 4-pointed sharp diamond core
    p = [
        (cx, cy - r),
        (cx + r * 0.16, cy - r * 0.16),
        (cx + r, cy),
        (cx + r * 0.16, cy + r * 0.16),
        (cx, cy + r),
        (cx - r * 0.16, cy + r * 0.16),
        (cx - r, cy),
        (cx - r * 0.16, cy - r * 0.16)
    ]
    d.polygon(p, fill=(255, 255, 255, int(alpha)))
    
    # 5. Intense pure white center pin-point
    cr = max(2, r * 0.2)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255, 255))
    return stamp

print("Generating 90 frames of high-end beauty sparkles...")
for f in range(TOTAL_FRAMES):
    t = f / FPS
    frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for (cx, cy, max_r, speed, phase, color) in sparkles:
        val = (math.sin(t * speed * 2 * math.pi + phase) + 1.0) / 2.0
        intensity = math.pow(val, 4.5)
        if intensity > 0.05:
            r = max_r * intensity
            alpha = min(255, int(255 * intensity * 1.2))
            stamp = make_sparkle_stamp(r, color, alpha)
            sw, sh = stamp.size
            frame.alpha_composite(stamp, (int(cx - sw // 2), int(cy - sh // 2)))
    frame.save(os.path.join(OUT_DIR, f"sp_{f:03d}.png"))

print("Sparkle generation complete in build_temp_v4/sparkles!")
