import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORKDIR = r"C:\Users\5700G\Desktop\레티라겐 레퍼런스"
BUILD_DIR = os.path.join(WORKDIR, "build_ad17")
OVERLAY_DIR = os.path.join(BUILD_DIR, "overlays")
os.makedirs(OVERLAY_DIR, exist_ok=True)

FONT_JALNAN = r"C:\Users\5700G\AppData\Local\Microsoft\Windows\Fonts\Jalnan2.otf"
FONT_SANS_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_SANS = r"C:\Windows\Fonts\malgun.ttf"

def create_comment_sticker():
    W, H = 760, 240
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Drop shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(shadow)
    s_d.rounded_rectangle([14, 16, W - 6, H - 4], radius=24, fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.paste(shadow, (0, 0), shadow)
    
    # Main Card Body
    box = [10, 10, W - 10, H - 10]
    d.rounded_rectangle(box, radius=24, fill=(22, 26, 35, 240), outline=(255, 255, 255, 80), width=2)
    
    # Left Avatar Circle with a stylish profile silhouette or initial
    avatar_box = [35, 35, 115, 115]
    d.ellipse(avatar_box, fill=(255, 140, 180, 255), outline=(255, 255, 255, 220), width=2)
    f_avatar = ImageFont.truetype(FONT_JALNAN, 36)
    d.text((75, 75), "Y", font=f_avatar, fill=(255, 255, 255), anchor="mm")
    
    # User ID & Time
    f_user = ImageFont.truetype(FONT_SANS_BOLD, 26)
    f_time = ImageFont.truetype(FONT_SANS, 22)
    d.text((135, 52), "luv_ely.y", font=f_user, fill=(240, 240, 245, 255))
    d.text((255, 56), "• 1시간 전", font=f_time, fill=(160, 165, 175, 255))
    
    # Comment Text
    f_comment = ImageFont.truetype(FONT_SANS_BOLD, 30)
    d.text((135, 105), "하얘서 넘 부러워요ㅠㅠ비결이 뭐예요?", font=f_comment, fill=(255, 255, 255, 255))
    
    # Heart icon drawn with PIL polygon/arcs for 100% crisp anti-aliased look
    # Draw heart at (145, 165)
    f_heart_cnt = ImageFont.truetype(FONT_SANS_BOLD, 24)
    # Pink mini badge
    d.rounded_rectangle([135, 150, 310, 188], radius=10, fill=(255, 60, 100, 40), outline=(255, 100, 130, 120), width=1)
    d.text((148, 168), "♥ 215명이 공감함", font=f_heart_cnt, fill=(255, 120, 150, 255), anchor="lm")
    
    # "답글 달기" button
    d.text((640, 168), "답글", font=f_heart_cnt, fill=(180, 185, 195, 255), anchor="rm")
    
    out_p = os.path.join(OVERLAY_DIR, "comment_sticker.png")
    img.save(out_p, "PNG")
    print(f">> Fixed Comment Sticker: {out_p}")

def create_clinic_tag():
    W, H = 820, 170
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(shadow)
    s_d.rounded_rectangle([14, 16, W - 6, H - 4], radius=22, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.paste(shadow, (0, 0), shadow)
    
    box = [10, 10, W - 10, H - 10]
    d.rounded_rectangle(box, radius=22, fill=(35, 15, 20, 240), outline=(255, 80, 90, 240), width=3)
    
    f_title = ImageFont.truetype(FONT_JALNAN, 36)
    f_price = ImageFont.truetype(FONT_JALNAN, 44)
    
    d.text((W // 2, 45), "[ 피부과 프락셀 10회 이상 ]", font=f_title, fill=(255, 180, 180), anchor="mm")
    d.text((W // 2, 105), "총 비용 180만원 지출", font=f_price, fill=(255, 240, 90), anchor="mm")
    
    out_p = os.path.join(OVERLAY_DIR, "clinic_tag.png")
    img.save(out_p, "PNG")
    print(f">> Created Clinic Tag: {out_p}")

def create_spec_card():
    W, H = 940, 220
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(shadow)
    s_d.rounded_rectangle([14, 16, W - 6, H - 4], radius=26, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow, (0, 0), shadow)
    
    box = [10, 10, W - 10, H - 10]
    d.rounded_rectangle(box, radius=26, fill=(18, 22, 32, 245), outline=(255, 215, 100, 230), width=3)
    
    f_sub = ImageFont.truetype(FONT_JALNAN, 30)
    f_main = ImageFont.truetype(FONT_JALNAN, 46)
    f_desc = ImageFont.truetype(FONT_SANS_BOLD, 28)
    
    d.text((W // 2, 48), "스위스산 레티놀 + 초저분자 GPH 콜라겐", font=f_sub, fill=(200, 225, 255), anchor="mm")
    d.text((W // 2, 112), "300Da 콜라겐 27,000mg 함유", font=f_main, fill=(255, 230, 80), anchor="mm")
    d.text((W // 2, 168), "속피지선 억제 & 진피 속살 팽팽 복원", font=f_desc, fill=(255, 255, 255), anchor="mm")
    
    out_p = os.path.join(OVERLAY_DIR, "spec_card.png")
    img.save(out_p, "PNG")
    print(f">> Created Spec Card: {out_p}")

create_comment_sticker()
create_clinic_tag()
create_spec_card()
