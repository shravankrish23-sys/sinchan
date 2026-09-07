import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ----------------------------------------------------
# IMPROVED CAT ASSETS WITH EXACT MUZZLE BLENDING
# ----------------------------------------------------
CAT_FUR_WHITE = (248, 240, 230, 255)
CAT_LINE = (30, 20, 18, 255)
CAT_MOUTH_BG = (95, 32, 34, 255)
CAT_TONGUE = (235, 110, 120, 255)
CAT_NOSE = (230, 135, 145, 255)
CAT_TEETH = (255, 255, 255, 255)

cat_w, cat_h = 50, 48
cat_viseme_data = {
    "X": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-3], fill=CAT_LINE, width=2),
        d.arc([cx-9, cy-6, cx, cy+4], start=0, end=180, fill=CAT_LINE, width=2),
        d.arc([cx, cy-6, cx+9, cy+4], start=0, end=180, fill=CAT_LINE, width=2)
    ),
    "A": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-3], fill=CAT_LINE, width=2),
        d.line([cx-9, cy-2, cx+9, cy-2], fill=CAT_LINE, width=2)
    ),
    "B": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.polygon([(cx-9, cy-4), (cx+9, cy-4), (cx+7, cy+7), (cx-7, cy+7)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-8, cy-4), (cx-5, cy-4), (cx-7, cy)], fill=CAT_TEETH),
        d.polygon([(cx+5, cy-4), (cx+8, cy-4), (cx+7, cy)], fill=CAT_TEETH),
        d.arc([cx-5, cy+1, cx+5, cy+6], start=0, end=180, fill=CAT_TONGUE)
    ),
    "C": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.polygon([(cx-11, cy-4), (cx+11, cy-4), (cx+9, cy+11), (cx-9, cy+11)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-10, cy-4), (cx-7, cy-4), (cx-9, cy+1)], fill=CAT_TEETH),
        d.polygon([(cx+7, cy-4), (cx+10, cy-4), (cx+9, cy+1)], fill=CAT_TEETH),
        d.ellipse([cx-6, cy+3, cx+6, cy+10], fill=CAT_TONGUE)
    ),
    "D": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.polygon([(cx-13, cy-4), (cx+13, cy-4), (cx+10, cy+15), (cx-10, cy+15)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-11, cy-4), (cx-8, cy-4), (cx-10, cy+2)], fill=CAT_TEETH),
        d.polygon([(cx+8, cy-4), (cx+11, cy-4), (cx+10, cy+2)], fill=CAT_TEETH),
        d.ellipse([cx-8, cy+5, cx+8, cy+15], fill=CAT_TONGUE)
    ),
    "E": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.ellipse([cx-9, cy-4, cx+9, cy+10], fill=CAT_MOUTH_BG, outline=CAT_LINE, width=2),
        d.ellipse([cx-5, cy+3, cx+5, cy+9], fill=CAT_TONGUE)
    ),
    "F": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.ellipse([cx-7, cy-3, cx+7, cy+7], fill=CAT_MOUTH_BG, outline=CAT_LINE, width=2)
    ),
    "G": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.polygon([(cx-10, cy-4), (cx+10, cy-4), (cx+8, cy+6), (cx-8, cy+6)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-9, cy-4), (cx-6, cy-4), (cx-8, cy)], fill=CAT_TEETH),
        d.polygon([(cx+6, cy-4), (cx+9, cy-4), (cx+8, cy)], fill=CAT_TEETH)
    ),
    "H": lambda d, cx, cy: (
        d.line([cx, cy-10, cx, cy-5], fill=CAT_LINE, width=2),
        d.polygon([(cx-14, cy-4), (cx+14, cy-4), (cx+11, cy+17), (cx-11, cy+17)], fill=CAT_MOUTH_BG, outline=CAT_LINE),
        d.polygon([(cx-12, cy-4), (cx-9, cy-4), (cx-11, cy+3)], fill=CAT_TEETH),
        d.polygon([(cx+9, cy-4), (cx+12, cy-4), (cx+11, cy+3)], fill=CAT_TEETH),
        d.ellipse([cx-9, cy+6, cx+9, cy+17], fill=CAT_TONGUE)
    )
}

for cue, draw_fn in cat_viseme_data.items():
    img = Image.new("RGBA", (cat_w, cat_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # White fur oval covering only the muzzle
    d.ellipse([3, 2, cat_w-3, cat_h-2], fill=CAT_FUR_WHITE)
    # Nose
    d.polygon([(cat_w//2-3, 3), (cat_w//2+3, 3), (cat_w//2, 7)], fill=CAT_NOSE, outline=CAT_LINE)
    draw_fn(d, cat_w//2, cat_h//2 + 3)
    img.save(f"scene_assets/cat/viseme_{cue}.png")

print("Updated cat visemes saved!")
