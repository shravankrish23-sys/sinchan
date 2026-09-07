import os
from PIL import Image, ImageDraw

os.makedirs("visemes", exist_ok=True)

# Colors matching the character's anime palette
SKIN_COLOR = (255, 224, 204, 255)
SKIN_SHADOW = (245, 205, 185, 255)
LINE_COLOR = (55, 30, 20, 255)
MOUTH_INSIDE = (140, 35, 45, 255)
TONGUE_COLOR = (230, 110, 110, 255)
TEETH_COLOR = (255, 255, 255, 255)

# Mouth patch dimensions
PATCH_W, PATCH_H = 140, 80
CENTER_X = PATCH_W // 2
CENTER_Y = PATCH_H // 2 + 5

def create_base_patch():
    # Transparent canvas with a smooth skin-toned oval that smoothly covers the old mouth
    img = Image.new("RGBA", (PATCH_W, PATCH_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 15, PATCH_W - 10, PATCH_H - 15], fill=SKIN_COLOR)
    return img, draw

# Viseme X: Neutral (Just the original mouth or smooth slight smile)
def make_viseme_X():
    img, draw = create_base_patch()
    # Gentle closed smile
    draw.arc([CENTER_X - 25, CENTER_Y - 15, CENTER_X + 25, CENTER_Y + 10], start=20, end=160, fill=LINE_COLOR, width=4)
    img.save("visemes/X.png")

# Viseme A: M, B, P (Flat closed pressed lips)
def make_viseme_A():
    img, draw = create_base_patch()
    draw.line([CENTER_X - 22, CENTER_Y - 2, CENTER_X + 22, CENTER_Y - 2], fill=LINE_COLOR, width=4)
    img.save("visemes/A.png")

# Viseme B: S, T, K, EE (Slightly open with upper teeth)
def make_viseme_B():
    img, draw = create_base_patch()
    # Mouth cavity
    draw.chord([CENTER_X - 26, CENTER_Y - 12, CENTER_X + 26, CENTER_Y + 14], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    # Upper teeth
    draw.rectangle([CENTER_X - 18, CENTER_Y - 8, CENTER_X + 18, CENTER_Y - 1], fill=TEETH_COLOR)
    # Tongue bottom
    draw.chord([CENTER_X - 16, CENTER_Y + 2, CENTER_X + 16, CENTER_Y + 14], start=0, end=180, fill=TONGUE_COLOR)
    img.save("visemes/B.png")

# Viseme C: EH, AE (Open mouth)
def make_viseme_C():
    img, draw = create_base_patch()
    draw.chord([CENTER_X - 28, CENTER_Y - 15, CENTER_X + 28, CENTER_Y + 20], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    # Upper teeth
    draw.rectangle([CENTER_X - 20, CENTER_Y - 10, CENTER_X + 20, CENTER_Y - 2], fill=TEETH_COLOR)
    # Tongue
    draw.chord([CENTER_X - 18, CENTER_Y + 5, CENTER_X + 18, CENTER_Y + 20], start=0, end=180, fill=TONGUE_COLOR)
    img.save("visemes/C.png")

# Viseme D: AA (Wide open mouth)
def make_viseme_D():
    img, draw = create_base_patch()
    draw.ellipse([CENTER_X - 26, CENTER_Y - 20, CENTER_X + 26, CENTER_Y + 25], fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    # Upper teeth
    draw.chord([CENTER_X - 18, CENTER_Y - 18, CENTER_X + 18, CENTER_Y - 2], start=180, end=360, fill=TEETH_COLOR)
    # Tongue
    draw.chord([CENTER_X - 20, CENTER_Y + 6, CENTER_X + 20, CENTER_Y + 24], start=0, end=180, fill=TONGUE_COLOR)
    img.save("visemes/D.png")

# Viseme E: O, ER (Round open)
def make_viseme_E():
    img, draw = create_base_patch()
    draw.ellipse([CENTER_X - 18, CENTER_Y - 16, CENTER_X + 18, CENTER_Y + 18], fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    # Tongue
    draw.chord([CENTER_X - 12, CENTER_Y + 4, CENTER_X + 12, CENTER_Y + 17], start=0, end=180, fill=TONGUE_COLOR)
    img.save("visemes/E.png")

# Viseme F: UW, OO (Small circle / pucker)
def make_viseme_F():
    img, draw = create_base_patch()
    draw.ellipse([CENTER_X - 12, CENTER_Y - 10, CENTER_X + 12, CENTER_Y + 10], fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    img.save("visemes/F.png")

# Viseme G: F, V (Upper teeth biting lower lip)
def make_viseme_G():
    img, draw = create_base_patch()
    draw.chord([CENTER_X - 20, CENTER_Y - 10, CENTER_X + 20, CENTER_Y + 10], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    draw.rectangle([CENTER_X - 16, CENTER_Y - 6, CENTER_X + 16, CENTER_Y + 4], fill=TEETH_COLOR)
    img.save("visemes/G.png")

# Viseme H: L (Tongue up)
def make_viseme_H():
    img, draw = create_base_patch()
    draw.chord([CENTER_X - 26, CENTER_Y - 15, CENTER_X + 26, CENTER_Y + 20], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    draw.chord([CENTER_X - 12, CENTER_Y - 10, CENTER_X + 12, CENTER_Y + 10], start=180, end=360, fill=TONGUE_COLOR)
    img.save("visemes/H.png")

make_viseme_X()
make_viseme_A()
make_viseme_B()
make_viseme_C()
make_viseme_D()
make_viseme_E()
make_viseme_F()
make_viseme_G()
make_viseme_H()

print("Created all anime visemes in visemes/ directory!")
