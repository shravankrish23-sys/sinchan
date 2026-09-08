import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("scene_assets/sinchan", exist_ok=True)
os.makedirs("scene_assets/cat", exist_ok=True)
os.makedirs("scene_assets/grandfather", exist_ok=True)

# ----------------------------------------------------
# 1. SINCHAN ASSETS (Shinchan Style)
# ----------------------------------------------------
SINCHAN_SKIN = (248, 179, 148, 255)
SINCHAN_LINE = (28, 20, 20, 255)
SINCHAN_MOUTH_BG = (120, 48, 48, 255)
SINCHAN_TONGUE = (210, 95, 95, 255)
SINCHAN_TEETH = (255, 255, 255, 255)

sinchan_w, sinchan_h = 50, 50
sinchan_viseme_data = {
    "X": lambda d, cx, cy: d.arc([cx-10, cy-6, cx+10, cy+8], start=20, end=160, fill=SINCHAN_LINE, width=3),
    "A": lambda d, cx, cy: d.line([cx-10, cy, cx+10, cy], fill=SINCHAN_LINE, width=3),
    "B": lambda d, cx, cy: (
        d.rounded_rectangle([cx-9, cy-6, cx+9, cy+6], radius=4, fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=2),
        d.rectangle([cx-7, cy-4, cx+7, cy-1], fill=SINCHAN_TEETH),
        d.arc([cx-6, cy, cx+6, cy+4], start=0, end=180, fill=SINCHAN_TONGUE)
    ),
    "C": lambda d, cx, cy: (
        d.ellipse([cx-11, cy-9, cx+11, cy+9], fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=2),
        d.rectangle([cx-8, cy-7, cx+8, cy-3], fill=SINCHAN_TEETH),
        d.ellipse([cx-7, cy+1, cx+7, cy+7], fill=SINCHAN_TONGUE)
    ),
    "D": lambda d, cx, cy: (
        d.ellipse([cx-13, cy-12, cx+13, cy+12], fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=3),
        d.rectangle([cx-9, cy-10, cx+9, cy-5], fill=SINCHAN_TEETH),
        d.ellipse([cx-8, cy, cx+8, cy+10], fill=SINCHAN_TONGUE)
    ),
    "E": lambda d, cx, cy: (
        d.ellipse([cx-10, cy-11, cx+10, cy+11], fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=3),
        d.ellipse([cx-6, cy+2, cx+6, cy+9], fill=SINCHAN_TONGUE)
    ),
    "F": lambda d, cx, cy: (
        d.ellipse([cx-7, cy-7, cx+7, cy+7], fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=2),
        d.ellipse([cx-4, cy, cx+4, cy+5], fill=SINCHAN_TONGUE)
    ),
    "G": lambda d, cx, cy: (
        d.ellipse([cx-10, cy-7, cx+10, cy+7], fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=2),
        d.rectangle([cx-8, cy-5, cx+8, cy], fill=SINCHAN_TEETH)
    ),
    "H": lambda d, cx, cy: (
        d.ellipse([cx-12, cy-14, cx+12, cy+14], fill=SINCHAN_MOUTH_BG, outline=SINCHAN_LINE, width=3),
        d.rectangle([cx-8, cy-12, cx+8, cy-6], fill=SINCHAN_TEETH),
        d.ellipse([cx-7, cy+1, cx+7, cy+12], fill=SINCHAN_TONGUE)
    )
}

for cue, draw_fn in sinchan_viseme_data.items():
    img = Image.new("RGBA", (sinchan_w, sinchan_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Background skin circle with feathered edges
    d.ellipse([4, 4, sinchan_w-4, sinchan_h-4], fill=SINCHAN_SKIN)
    draw_fn(d, sinchan_w//2, sinchan_h//2)
    img.save(f"scene_assets/sinchan/viseme_{cue}.png")

# Sinchan Blinks
sinchan_blink_w, sinchan_blink_h = 130, 70
sinchan_blink_closed = Image.new("RGBA", (sinchan_blink_w, sinchan_blink_h), (0, 0, 0, 0))
bd = ImageDraw.Draw(sinchan_blink_closed)
# Left eye
bd.ellipse([24, 18, 58, 58], fill=SINCHAN_SKIN)
bd.arc([24, 24, 58, 52], start=200, end=340, fill=SINCHAN_LINE, width=4)
# Right eye
bd.ellipse([88, 16, 122, 56], fill=SINCHAN_SKIN)
bd.arc([88, 22, 122, 50], start=200, end=340, fill=SINCHAN_LINE, width=4)
sinchan_blink_closed.save("scene_assets/sinchan/blink_closed.png")

sinchan_blink_half = Image.new("RGBA", (sinchan_blink_w, sinchan_blink_h), (0, 0, 0, 0))
bhd = ImageDraw.Draw(sinchan_blink_half)
bhd.chord([24, 18, 58, 46], start=180, end=360, fill=SINCHAN_SKIN, outline=SINCHAN_LINE, width=3)
bhd.chord([88, 16, 122, 44], start=180, end=360, fill=SINCHAN_SKIN, outline=SINCHAN_LINE, width=3)
sinchan_blink_half.save("scene_assets/sinchan/blink_half.png")


# ----------------------------------------------------
# 2. GRANDFATHER ASSETS
# ----------------------------------------------------
GF_SKIN = (235, 168, 138, 255)
GF_LINE = (35, 22, 18, 255)
GF_MOUTH_BG = (105, 40, 38, 255)
GF_TONGUE = (195, 88, 88, 255)
GF_TEETH = (248, 248, 244, 255)

gf_w, gf_h = 80, 50
gf_viseme_data = {
    "X": lambda d, cx, cy: (
        d.arc([cx-24, cy-10, cx+24, cy+10], start=15, end=165, fill=GF_LINE, width=3),
        d.line([cx-23, cy, cx-26, cy+5], fill=GF_LINE, width=2),
        d.line([cx+23, cy, cx+26, cy+5], fill=GF_LINE, width=2),
        d.arc([cx-12, cy+12, cx+12, cy+22], start=20, end=160, fill=GF_LINE, width=2)
    ),
    "A": lambda d, cx, cy: (
        d.line([cx-22, cy, cx+22, cy], fill=GF_LINE, width=3),
        d.line([cx-22, cy-1, cx-25, cy+4], fill=GF_LINE, width=2),
        d.line([cx+22, cy-1, cx+25, cy+4], fill=GF_LINE, width=2)
    ),
    "B": lambda d, cx, cy: (
        d.chord([cx-20, cy-8, cx+20, cy+10], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=2),
        d.rectangle([cx-16, cy-7, cx+16, cy-3], fill=GF_TEETH),
        d.arc([cx-12, cy+1, cx+12, cy+7], start=0, end=180, fill=GF_TONGUE)
    ),
    "C": lambda d, cx, cy: (
        d.chord([cx-22, cy-10, cx+22, cy+14], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=3),
        d.rectangle([cx-17, cy-9, cx+17, cy-4], fill=GF_TEETH),
        d.ellipse([cx-14, cy+1, cx+14, cy+11], fill=GF_TONGUE)
    ),
    "D": lambda d, cx, cy: (
        d.chord([cx-24, cy-12, cx+24, cy+18], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=3),
        d.rectangle([cx-18, cy-11, cx+18, cy-5], fill=GF_TEETH),
        d.ellipse([cx-15, cy+2, cx+15, cy+15], fill=GF_TONGUE)
    ),
    "E": lambda d, cx, cy: (
        d.ellipse([cx-14, cy-11, cx+14, cy+12], fill=GF_MOUTH_BG, outline=GF_LINE, width=3),
        d.ellipse([cx-10, cy+1, cx+10, cy+9], fill=GF_TONGUE)
    ),
    "F": lambda d, cx, cy: (
        d.ellipse([cx-10, cy-8, cx+10, cy+8], fill=GF_MOUTH_BG, outline=GF_LINE, width=2),
        d.ellipse([cx-6, cy, cx+6, cy+6], fill=GF_TONGUE)
    ),
    "G": lambda d, cx, cy: (
        d.chord([cx-18, cy-8, cx+18, cy+10], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=2),
        d.rectangle([cx-15, cy-7, cx+15, cy-2], fill=GF_TEETH)
    ),
    "H": lambda d, cx, cy: (
        d.chord([cx-22, cy-13, cx+22, cy+20], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=3),
        d.rectangle([cx-17, cy-12, cx+17, cy-6], fill=GF_TEETH),
        d.ellipse([cx-14, cy+2, cx+14, cy+17], fill=GF_TONGUE)
    )
}

for cue, draw_fn in gf_viseme_data.items():
    img = Image.new("RGBA", (gf_w, gf_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, gf_w-4, gf_h-4], fill=GF_SKIN)
    draw_fn(d, gf_w//2, gf_h//2)
    img.save(f"scene_assets/grandfather/viseme_{cue}.png")

# Grandfather Blinks
gf_blink_w, gf_blink_h = 100, 60
gf_blink_closed = Image.new("RGBA", (gf_blink_w, gf_blink_h), (0, 0, 0, 0))
gfd = ImageDraw.Draw(gf_blink_closed)
# Left eye
gfd.ellipse([14, 15, 44, 48], fill=GF_SKIN)
gfd.arc([14, 20, 44, 42], start=200, end=340, fill=GF_LINE, width=3)
gfd.line([16, 40, 24, 44], fill=GF_LINE, width=2)
# Right eye
gfd.ellipse([58, 16, 88, 49], fill=GF_SKIN)
gfd.arc([58, 21, 88, 43], start=200, end=340, fill=GF_LINE, width=3)
gfd.line([78, 44, 86, 40], fill=GF_LINE, width=2)
gf_blink_closed.save("scene_assets/grandfather/blink_closed.png")

gf_blink_half = Image.new("RGBA", (gf_blink_w, gf_blink_h), (0, 0, 0, 0))
gfhd = ImageDraw.Draw(gf_blink_half)
gfhd.chord([14, 15, 44, 38], start=180, end=360, fill=GF_SKIN, outline=GF_LINE, width=2)
gfhd.chord([58, 16, 88, 39], start=180, end=360, fill=GF_SKIN, outline=GF_LINE, width=2)
gf_blink_half.save("scene_assets/grandfather/blink_half.png")


# ----------------------------------------------------
# 3. CAT ASSETS
# ----------------------------------------------------
CAT_FUR_WHITE = (248, 240, 230, 255)
CAT_LINE = (30, 20, 18, 255)
CAT_MOUTH_BG = (95, 32, 34, 255)
CAT_TONGUE = (235, 110, 120, 255)
CAT_NOSE = (230, 135, 145, 255)
CAT_TEETH = (255, 255, 255, 255)

cat_w, cat_h = 46, 44
cat_viseme_data = {
    "X": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-2], fill=CAT_LINE, width=2),
        d.arc([cx-9, cy-4, cx, cy+4], start=0, end=180, fill=CAT_LINE, width=2),
        d.arc([cx, cy-4, cx+9, cy+4], start=0, end=180, fill=CAT_LINE, width=2)
    ),
    "A": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-2], fill=CAT_LINE, width=2),
        d.line([cx-8, cy-1, cx+8, cy-1], fill=CAT_LINE, width=2)
    ),
    "B": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.polygon([(cx-9, cy-3), (cx+9, cy-3), (cx+7, cy+6), (cx-7, cy+6)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-8, cy-3), (cx-5, cy-3), (cx-7, cy)], fill=CAT_TEETH),
        d.polygon([(cx+5, cy-3), (cx+8, cy-3), (cx+7, cy)], fill=CAT_TEETH),
        d.arc([cx-5, cy+1, cx+5, cy+6], start=0, end=180, fill=CAT_TONGUE)
    ),
    "C": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.polygon([(cx-10, cy-3), (cx+10, cy-3), (cx+8, cy+10), (cx-8, cy+10)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-9, cy-3), (cx-6, cy-3), (cx-8, cy+1)], fill=CAT_TEETH),
        d.polygon([(cx+6, cy-3), (cx+9, cy-3), (cx+8, cy+1)], fill=CAT_TEETH),
        d.ellipse([cx-6, cy+3, cx+6, cy+10], fill=CAT_TONGUE)
    ),
    "D": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.polygon([(cx-12, cy-3), (cx+12, cy-3), (cx+9, cy+14), (cx-9, cy+14)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-10, cy-3), (cx-7, cy-3), (cx-9, cy+2)], fill=CAT_TEETH),
        d.polygon([(cx+7, cy-3), (cx+10, cy-3), (cx+9, cy+2)], fill=CAT_TEETH),
        d.ellipse([cx-7, cy+5, cx+7, cy+14], fill=CAT_TONGUE)
    ),
    "E": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.ellipse([cx-8, cy-3, cx+8, cy+10], fill=CAT_MOUTH_BG, outline=CAT_LINE, width=2),
        d.ellipse([cx-5, cy+3, cx+5, cy+9], fill=CAT_TONGUE)
    ),
    "F": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.ellipse([cx-6, cy-2, cx+6, cy+6], fill=CAT_MOUTH_BG, outline=CAT_LINE, width=2)
    ),
    "G": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.polygon([(cx-9, cy-3), (cx+9, cy-3), (cx+7, cy+5), (cx-7, cy+5)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-8, cy-3), (cx-5, cy-3), (cx-7, cy)], fill=CAT_TEETH),
        d.polygon([(cx+5, cy-3), (cx+8, cy-3), (cx+7, cy)], fill=CAT_TEETH)
    ),
    "H": lambda d, cx, cy: (
        d.line([cx, cy-8, cx, cy-4], fill=CAT_LINE, width=2),
        d.polygon([(cx-13, cy-3), (cx+13, cy-3), (cx+10, cy+16), (cx-10, cy+16)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-11, cy-3), (cx-8, cy-3), (cx-10, cy+3)], fill=CAT_TEETH),
        d.polygon([(cx+8, cy-3), (cx+11, cy-3), (cx+10, cy+3)], fill=CAT_TEETH),
        d.ellipse([cx-8, cy+6, cx+8, cy+16], fill=CAT_TONGUE)
    )
}

for cue, draw_fn in cat_viseme_data.items():
    img = Image.new("RGBA", (cat_w, cat_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([3, 3, cat_w-3, cat_h-3], fill=CAT_FUR_WHITE)
    # Nose
    d.polygon([(cat_w//2-3, 4), (cat_w//2+3, 4), (cat_w//2, 8)], fill=CAT_NOSE, outline=CAT_LINE)
    draw_fn(d, cat_w//2, cat_h//2 + 2)
    img.save(f"scene_assets/cat/viseme_{cue}.png")

# Cat Blinks
cat_blink_w, cat_blink_h = 90, 50
cat_blink_closed = Image.new("RGBA", (cat_blink_w, cat_blink_h), (0, 0, 0, 0))
cd = ImageDraw.Draw(cat_blink_closed)
# Left eye
cd.polygon([(10, 16), (38, 22), (34, 36), (12, 30)], fill=(228, 146, 78, 255))
cd.line([(10, 24), (38, 28)], fill=CAT_LINE, width=3)
# Right eye
cd.polygon([(52, 22), (80, 16), (78, 30), (56, 36)], fill=(228, 146, 78, 255))
cd.line([(52, 28), (80, 24)], fill=CAT_LINE, width=3)
cat_blink_closed.save("scene_assets/cat/blink_closed.png")

cat_blink_half = Image.new("RGBA", (cat_blink_w, cat_blink_h), (0, 0, 0, 0))
chd = ImageDraw.Draw(cat_blink_half)
chd.polygon([(10, 16), (38, 22), (36, 28), (12, 24)], fill=(228, 146, 78, 255), outline=CAT_LINE)
chd.polygon([(52, 22), (80, 16), (78, 24), (54, 28)], fill=(228, 146, 78, 255), outline=CAT_LINE)
cat_blink_half.save("scene_assets/cat/blink_half.png")

print("Master visual assets built perfectly!")
