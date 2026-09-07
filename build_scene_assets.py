import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("scene_assets/boy", exist_ok=True)
os.makedirs("scene_assets/cat", exist_ok=True)
os.makedirs("scene_assets/grandfather", exist_ok=True)

scene = Image.open("scene_main.jpg").convert("RGBA")

# ==========================================
# 1. BOY ASSETS GENERATION
# ==========================================
# Boy skin color: #F8B394 -> (248, 179, 148), Line: (28, 20, 18), Mouth inside: (132, 60, 58), Tongue: (200, 95, 95)
BOY_SKIN = (248, 179, 148, 255)
BOY_LINE = (25, 20, 20, 255)
BOY_MOUTH_BG = (120, 48, 48, 255)
BOY_TONGUE = (210, 95, 95, 255)
BOY_TEETH = (255, 255, 255, 255)

# Boy neutral patch to cover open mouth cleanly
boy_patch_w, boy_patch_h = 60, 60
boy_base_patch = Image.new("RGBA", (boy_patch_w, boy_patch_h), (0, 0, 0, 0))
d = ImageDraw.Draw(boy_base_patch)
# Soft circular skin patch
d.ellipse([5, 5, 55, 55], fill=BOY_SKIN)
# Add small neutral smile line
d.arc([18, 20, 42, 38], start=20, end=160, fill=BOY_LINE, width=3)
boy_base_patch.save("scene_assets/boy/base_patch.png")

# Generate Boy Visemes
boy_viseme_defs = {
    "X": ("neutral", 0),
    "A": ("closed_line", 0),
    "B": ("teeth_small", 1),
    "C": ("medium_oval", 2),
    "D": ("wide_open", 3),
    "E": ("round_o", 2),
    "F": ("pucker", 1),
    "G": ("lip_teeth", 1),
    "H": ("tall_open", 3)
}

for cue, (style, scale) in boy_viseme_defs.items():
    v_img = Image.new("RGBA", (boy_patch_w, boy_patch_h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v_img)
    # Fill skin base
    vd.ellipse([5, 5, 55, 55], fill=BOY_SKIN)
    
    cx, cy = 30, 30
    if style == "neutral":
        vd.arc([18, 20, 42, 38], start=20, end=160, fill=BOY_LINE, width=3)
    elif style == "closed_line":
        vd.line([16, cy, 44, cy], fill=BOY_LINE, width=3)
    elif style == "teeth_small":
        vd.rounded_rectangle([18, cy-6, 42, cy+6], radius=4, fill=BOY_MOUTH_BG, outline=BOY_LINE, width=2)
        vd.rectangle([20, cy-4, 40, cy-1], fill=BOY_TEETH)
        vd.arc([22, cy, 38, cy+4], start=0, end=180, fill=BOY_TONGUE)
    elif style == "medium_oval":
        vd.ellipse([16, cy-10, 44, cy+10], fill=BOY_MOUTH_BG, outline=BOY_LINE, width=2)
        vd.rectangle([20, cy-8, 40, cy-4], fill=BOY_TEETH)
        vd.ellipse([22, cy, 38, cy+8], fill=BOY_TONGUE)
    elif style == "wide_open":
        vd.ellipse([14, cy-14, 46, cy+14], fill=BOY_MOUTH_BG, outline=BOY_LINE, width=3)
        vd.rectangle([18, cy-12, 42, cy-6], fill=BOY_TEETH)
        vd.ellipse([20, cy-2, 40, cy+12], fill=BOY_TONGUE)
    elif style == "round_o":
        vd.ellipse([20, cy-11, 40, cy+11], fill=BOY_MOUTH_BG, outline=BOY_LINE, width=3)
        vd.ellipse([24, cy+1, 36, cy+9], fill=BOY_TONGUE)
    elif style == "pucker":
        vd.ellipse([23, cy-7, 37, cy+7], fill=BOY_MOUTH_BG, outline=BOY_LINE, width=2)
    elif style == "lip_teeth":
        vd.ellipse([18, cy-7, 42, cy+7], fill=BOY_MOUTH_BG, outline=BOY_LINE, width=2)
        vd.rectangle([20, cy-5, 40, cy], fill=BOY_TEETH)
    elif style == "tall_open":
        vd.ellipse([16, cy-16, 44, cy+16], fill=BOY_MOUTH_BG, outline=BOY_LINE, width=3)
        vd.rectangle([20, cy-14, 40, cy-7], fill=BOY_TEETH)
        vd.ellipse([22, cy, 38, cy+14], fill=BOY_TONGUE)
    
    # Soft alpha blur on edges for seamless blending
    v_img.save(f"scene_assets/boy/viseme_{cue}.png")

# Boy Blink Overlays
boy_eye_w, boy_eye_h = 140, 80
# Left Eye center relative to patch: (46, 46), Right Eye: (114, 44)
boy_blink_closed = Image.new("RGBA", (boy_eye_w, boy_eye_h), (0, 0, 0, 0))
bd = ImageDraw.Draw(boy_blink_closed)
# Left eye skin + curve
bd.ellipse([28, 25, 64, 65], fill=BOY_SKIN)
bd.arc([28, 30, 64, 58], start=200, end=340, fill=BOY_LINE, width=4)
# Right eye skin + curve
bd.ellipse([96, 23, 132, 63], fill=BOY_SKIN)
bd.arc([96, 28, 132, 56], start=200, end=340, fill=BOY_LINE, width=4)
boy_blink_closed.save("scene_assets/boy/blink_closed.png")

# Half blink
boy_blink_half = Image.new("RGBA", (boy_eye_w, boy_eye_h), (0, 0, 0, 0))
bhd = ImageDraw.Draw(boy_blink_half)
bhd.chord([28, 22, 64, 52], start=180, end=360, fill=BOY_SKIN, outline=BOY_LINE, width=3)
bhd.chord([96, 20, 132, 50], start=180, end=360, fill=BOY_SKIN, outline=BOY_LINE, width=3)
boy_blink_half.save("scene_assets/boy/blink_half.png")


# ==========================================
# 2. GRANDFATHER ASSETS GENERATION
# ==========================================
GF_SKIN = (235, 168, 138, 255)
GF_LINE = (35, 22, 18, 255)
GF_MOUTH_BG = (105, 40, 38, 255)
GF_TONGUE = (195, 88, 88, 255)
GF_TEETH = (245, 245, 240, 255)

gf_patch_w, gf_patch_h = 80, 60
gf_base_patch = Image.new("RGBA", (gf_patch_w, gf_patch_h), (0, 0, 0, 0))
gfd = ImageDraw.Draw(gf_base_patch)
gfd.ellipse([5, 5, 75, 55], fill=GF_SKIN)
# Elderly gentle closed smile line
gfd.arc([15, 15, 65, 38], start=15, end=165, fill=GF_LINE, width=3)
# Smile corner crease
gfd.line([14, 23, 11, 28], fill=GF_LINE, width=2)
gfd.line([66, 23, 69, 28], fill=GF_LINE, width=2)
gf_base_patch.save("scene_assets/grandfather/base_patch.png")

gf_viseme_defs = {
    "X": "neutral",
    "A": "closed_smile",
    "B": "teeth_talk",
    "C": "medium_smile",
    "D": "wide_talk",
    "E": "round_talk",
    "F": "pucker_talk",
    "G": "teeth_lip",
    "H": "open_talk"
}

for cue, style in gf_viseme_defs.items():
    v_img = Image.new("RGBA", (gf_patch_w, gf_patch_h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v_img)
    vd.ellipse([5, 5, 75, 55], fill=GF_SKIN)
    
    cx, cy = 40, 28
    if style == "neutral" or style == "closed_smile":
        vd.arc([16, cy-12, 64, cy+10], start=15, end=165, fill=GF_LINE, width=3)
        vd.line([15, cy-2, 12, cy+3], fill=GF_LINE, width=2)
        vd.line([65, cy-2, 68, cy+3], fill=GF_LINE, width=2)
    elif style == "teeth_talk":
        vd.chord([18, cy-10, 62, cy+12], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=2)
        vd.rectangle([22, cy-9, 58, cy-4], fill=GF_TEETH)
        vd.arc([26, cy, 54, cy+8], start=0, end=180, fill=GF_TONGUE)
    elif style == "medium_smile":
        vd.chord([16, cy-12, 64, cy+15], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=3)
        vd.rectangle([22, cy-11, 58, cy-5], fill=GF_TEETH)
        vd.ellipse([26, cy+1, 54, cy+13], fill=GF_TONGUE)
    elif style == "wide_talk":
        vd.chord([14, cy-14, 66, cy+18], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=3)
        vd.rectangle([20, cy-13, 60, cy-6], fill=GF_TEETH)
        vd.ellipse([24, cy+2, 56, cy+16], fill=GF_TONGUE)
    elif style == "round_talk":
        vd.ellipse([26, cy-12, 54, cy+14], fill=GF_MOUTH_BG, outline=GF_LINE, width=3)
        vd.ellipse([30, cy+2, 50, cy+12], fill=GF_TONGUE)
    elif style == "pucker_talk":
        vd.ellipse([30, cy-8, 50, cy+8], fill=GF_MOUTH_BG, outline=GF_LINE, width=2)
    elif style == "teeth_lip":
        vd.chord([20, cy-8, 60, cy+10], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=2)
        vd.rectangle([24, cy-7, 56, cy-2], fill=GF_TEETH)
    elif style == "open_talk":
        vd.chord([16, cy-15, 64, cy+20], start=0, end=180, fill=GF_MOUTH_BG, outline=GF_LINE, width=3)
        vd.rectangle([22, cy-14, 58, cy-6], fill=GF_TEETH)
        vd.ellipse([26, cy+3, 54, cy+18], fill=GF_TONGUE)
        
    v_img.save(f"scene_assets/grandfather/viseme_{cue}.png")

# Grandfather Blink Overlays
gf_eye_w, gf_eye_h = 110, 70
# Left eye approx (25, 35), Right eye approx (75, 38)
gf_blink_closed = Image.new("RGBA", (gf_eye_w, gf_eye_h), (0, 0, 0, 0))
gfd = ImageDraw.Draw(gf_blink_closed)
gfd.ellipse([10, 15, 45, 55], fill=GF_SKIN)
gfd.arc([10, 22, 45, 48], start=200, end=340, fill=GF_LINE, width=3)
gfd.line([12, 46, 20, 50], fill=GF_LINE, width=2) # wrinkle under eye

gfd.ellipse([60, 18, 95, 58], fill=GF_SKIN)
gfd.arc([60, 25, 95, 51], start=200, end=340, fill=GF_LINE, width=3)
gfd.line([85, 49, 93, 46], fill=GF_LINE, width=2)
gf_blink_closed.save("scene_assets/grandfather/blink_closed.png")

gf_blink_half = Image.new("RGBA", (gf_eye_w, gf_eye_h), (0, 0, 0, 0))
gfhd = ImageDraw.Draw(gf_blink_half)
gfhd.chord([10, 14, 45, 42], start=180, end=360, fill=GF_SKIN, outline=GF_LINE, width=2)
gfhd.chord([60, 17, 95, 45], start=180, end=360, fill=GF_SKIN, outline=GF_LINE, width=2)
gf_blink_half.save("scene_assets/grandfather/blink_half.png")


# ==========================================
# 3. CAT ASSETS GENERATION
# ==========================================
CAT_FUR_WHITE = (248, 240, 230, 255)
CAT_FUR_ORANGE = (228, 146, 78, 255)
CAT_LINE = (30, 20, 18, 255)
CAT_MOUTH_BG = (95, 32, 34, 255)
CAT_TONGUE = (235, 110, 120, 255)
CAT_NOSE = (230, 135, 145, 255)
CAT_TEETH = (255, 255, 255, 255)

cat_patch_w, cat_patch_h = 55, 50
cat_base_patch = Image.new("RGBA", (cat_patch_w, cat_patch_h), (0, 0, 0, 0))
cd = ImageDraw.Draw(cat_base_patch)
cd.ellipse([5, 5, 50, 45], fill=CAT_FUR_WHITE)
# Cat nose
cd.polygon([(24, 12), (30, 12), (27, 16)], fill=CAT_NOSE, outline=CAT_LINE)
# Cute cat closed muzzle line (w shape)
cd.line([27, 16, 27, 21], fill=CAT_LINE, width=2)
cd.arc([17, 18, 27, 28], start=0, end=180, fill=CAT_LINE, width=2)
cd.arc([27, 18, 37, 28], start=0, end=180, fill=CAT_LINE, width=2)
cat_base_patch.save("scene_assets/cat/base_patch.png")

cat_viseme_defs = {
    "X": "neutral",
    "A": "closed_muzzle",
    "B": "teeth_snarl",
    "C": "meow_medium",
    "D": "meow_wide",
    "E": "meow_round",
    "F": "small_o",
    "G": "teeth_lip",
    "H": "yowl_open"
}

for cue, style in cat_viseme_defs.items():
    v_img = Image.new("RGBA", (cat_patch_w, cat_patch_h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v_img)
    vd.ellipse([5, 5, 50, 45], fill=CAT_FUR_WHITE)
    # Nose
    vd.polygon([(24, 12), (30, 12), (27, 16)], fill=CAT_NOSE, outline=CAT_LINE)
    
    cx, cy = 27, 24
    if style == "neutral" or style == "closed_muzzle":
        vd.line([27, 16, 27, 21], fill=CAT_LINE, width=2)
        vd.arc([17, 18, 27, 28], start=0, end=180, fill=CAT_LINE, width=2)
        vd.arc([27, 18, 37, 28], start=0, end=180, fill=CAT_LINE, width=2)
    elif style == "teeth_snarl":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.polygon([(17, 20), (37, 20), (34, 32), (20, 32)], fill=CAT_MOUTH_BG, outline=CAT_LINE)
        # Tiny cat fangs
        vd.polygon([(19, 20), (22, 20), (20, 24)], fill=CAT_TEETH)
        vd.polygon([(32, 20), (35, 20), (34, 24)], fill=CAT_TEETH)
        vd.arc([21, 26, 33, 33], start=0, end=180, fill=CAT_TONGUE)
    elif style == "meow_medium":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.polygon([(16, 20), (38, 20), (35, 36), (19, 36)], fill=CAT_MOUTH_BG, outline=CAT_LINE)
        vd.polygon([(18, 20), (21, 20), (20, 25)], fill=CAT_TEETH)
        vd.polygon([(33, 20), (36, 20), (34, 25)], fill=CAT_TEETH)
        vd.ellipse([20, 28, 34, 37], fill=CAT_TONGUE)
    elif style == "meow_wide":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.polygon([(15, 20), (39, 20), (36, 40), (18, 40)], fill=CAT_MOUTH_BG, outline=CAT_LINE)
        vd.polygon([(17, 20), (21, 20), (19, 26)], fill=CAT_TEETH)
        vd.polygon([(33, 20), (37, 20), (35, 26)], fill=CAT_TEETH)
        vd.ellipse([19, 30, 35, 41], fill=CAT_TONGUE)
    elif style == "meow_round":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.ellipse([19, 20, 35, 36], fill=CAT_MOUTH_BG, outline=CAT_LINE, width=2)
        vd.ellipse([22, 28, 32, 35], fill=CAT_TONGUE)
    elif style == "small_o":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.ellipse([21, 21, 33, 31], fill=CAT_MOUTH_BG, outline=CAT_LINE, width=2)
    elif style == "teeth_lip":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.polygon([(18, 20), (36, 20), (33, 28), (21, 28)], fill=CAT_MOUTH_BG, outline=CAT_LINE)
        vd.polygon([(19, 20), (22, 20), (20, 24)], fill=CAT_TEETH)
        vd.polygon([(32, 20), (35, 20), (34, 24)], fill=CAT_TEETH)
    elif style == "yowl_open":
        vd.line([27, 16, 27, 19], fill=CAT_LINE, width=2)
        vd.polygon([(14, 20), (40, 20), (37, 42), (17, 42)], fill=CAT_MOUTH_BG, outline=CAT_LINE)
        vd.polygon([(16, 20), (20, 20), (18, 27)], fill=CAT_TEETH)
        vd.polygon([(34, 20), (38, 20), (36, 27)], fill=CAT_TEETH)
        vd.ellipse([18, 32, 36, 43], fill=CAT_TONGUE)

    v_img.save(f"scene_assets/cat/viseme_{cue}.png")

# Cat Blink Overlays
cat_eye_w, cat_eye_h = 100, 60
cat_blink_closed = Image.new("RGBA", (cat_eye_w, cat_eye_h), (0, 0, 0, 0))
cd = ImageDraw.Draw(cat_blink_closed)
# Left slanted eye (approx 23, 28)
cd.polygon([(10, 18), (42, 24), (36, 40), (12, 34)], fill=CAT_FUR_ORANGE)
cd.line([(10, 26), (42, 30)], fill=CAT_LINE, width=3)
# Right slanted eye (approx 71, 30)
cd.polygon([(58, 24), (90, 18), (88, 34), (64, 40)], fill=CAT_FUR_ORANGE)
cd.line([(58, 30), (90, 26)], fill=CAT_LINE, width=3)
cat_blink_closed.save("scene_assets/cat/blink_closed.png")

cat_blink_half = Image.new("RGBA", (cat_eye_w, cat_eye_h), (0, 0, 0, 0))
chd = ImageDraw.Draw(cat_blink_half)
chd.polygon([(10, 18), (42, 24), (38, 30), (12, 26)], fill=CAT_FUR_ORANGE, outline=CAT_LINE)
chd.polygon([(58, 24), (90, 18), (88, 26), (62, 30)], fill=CAT_FUR_ORANGE, outline=CAT_LINE)
cat_blink_half.save("scene_assets/cat/blink_half.png")

print("All visual assets created in scene_assets/!")
