import cv2
import numpy as np
from PIL import Image, ImageDraw

# 1. Load original boy image as BGR and Alpha separately
img_rgba = Image.open("boy.png").convert("RGBA")
img_np = np.array(img_rgba)
bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
alpha = img_np[:, :, 3]

# Inpaint mouth area on BGR
mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
mask[350:385, 470:550] = 255

inpainted_bgr = cv2.inpaint(bgr, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

# Recombine with alpha
inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
clean_pil = Image.fromarray(np.dstack((inpainted_rgb, alpha)))
clean_pil.save("boy_base_clean.png")
print("Saved boy_base_clean.png successfully!")

# 2. Re-create mouth sprites
MOUTH_W, MOUTH_H = 100, 70
CX = MOUTH_W // 2
CY = MOUTH_H // 2

LINE_COLOR = (45, 25, 18, 255)
MOUTH_INSIDE = (135, 30, 42, 255)
TONGUE_COLOR = (235, 115, 115, 255)
TEETH_COLOR = (255, 255, 255, 255)

def create_sprite():
    return Image.new("RGBA", (MOUTH_W, MOUTH_H), (0, 0, 0, 0))

# X: Natural closed anime smile
def make_X():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.arc([CX - 22, CY - 18, CX + 22, CY + 10], start=25, end=155, fill=LINE_COLOR, width=4)
    im.save("visemes/X.png")

# A: M, B, P (Flat closed line)
def make_A():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.line([CX - 18, CY - 2, CX + 18, CY - 2], fill=LINE_COLOR, width=4)
    im.save("visemes/A.png")

# B: S, T, EE (Slight open + teeth)
def make_B():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.chord([CX - 22, CY - 10, CX + 22, CY + 12], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    d.rectangle([CX - 15, CY - 7, CX + 15, CY - 1], fill=TEETH_COLOR)
    d.chord([CX - 14, CY + 2, CX + 14, CY + 12], start=0, end=180, fill=TONGUE_COLOR)
    im.save("visemes/B.png")

# C: EH, AE (Open mouth)
def make_C():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.chord([CX - 24, CY - 14, CX + 24, CY + 18], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    d.rectangle([CX - 18, CY - 10, CX + 18, CY - 2], fill=TEETH_COLOR)
    d.chord([CX - 16, CY + 4, CX + 16, CY + 18], start=0, end=180, fill=TONGUE_COLOR)
    im.save("visemes/C.png")

# D: AA (Wide open vowel)
def make_D():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.ellipse([CX - 20, CY - 18, CX + 20, CY + 20], fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    d.chord([CX - 15, CY - 16, CX + 15, CY - 4], start=180, end=360, fill=TEETH_COLOR)
    d.chord([CX - 16, CY + 4, CX + 16, CY + 20], start=0, end=180, fill=TONGUE_COLOR)
    im.save("visemes/D.png")

# E: O, ER (Round open)
def make_E():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.ellipse([CX - 16, CY - 14, CX + 16, CY + 16], fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    d.chord([CX - 10, CY + 3, CX + 10, CY + 15], start=0, end=180, fill=TONGUE_COLOR)
    im.save("visemes/E.png")

# F: UW, OO (Small circle)
def make_F():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.ellipse([CX - 10, CY - 8, CX + 10, CY + 8], fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    im.save("visemes/F.png")

# G: F, V
def make_G():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.chord([CX - 18, CY - 8, CX + 18, CY + 10], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    d.rectangle([CX - 14, CY - 5, CX + 14, CY + 3], fill=TEETH_COLOR)
    im.save("visemes/G.png")

# H: L
def make_H():
    im = create_sprite()
    d = ImageDraw.Draw(im)
    d.chord([CX - 22, CY - 12, CX + 22, CY + 16], start=10, end=170, fill=MOUTH_INSIDE, outline=LINE_COLOR, width=4)
    d.chord([CX - 10, CY - 8, CX + 10, CY + 8], start=180, end=360, fill=TONGUE_COLOR)
    im.save("visemes/H.png")

make_X()
make_A()
make_B()
make_C()
make_D()
make_E()
make_F()
make_G()
make_H()
print("Clean visemes generated!")
