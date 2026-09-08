import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

scene = Image.open("scene_main.jpg").convert("RGBA")
W, H = scene.size

# ----------------------------------------------------
# 1. CREATE SCENE BASE REST (Clean closed mouths for all 3)
# ----------------------------------------------------
base_rest = scene.copy()
draw = ImageDraw.Draw(base_rest)

# SINCHAN REST MOUTH:
# In scene_main.jpg, Sinchan's open mouth is at x: 268 to 290, y: 558 to 582.
# Sample exact surrounding skin colors
sinchan_skin_crop = scene.crop((250, 545, 268, 565))
sinchan_skin_avg = np.array(sinchan_skin_crop).mean(axis=(0,1)).astype(int)
sinchan_skin_tuple = (int(sinchan_skin_avg[0]), int(sinchan_skin_avg[1]), int(sinchan_skin_avg[2]), 255)

# Fill sinchan open mouth with skin
draw.ellipse([265, 555, 292, 584], fill=sinchan_skin_tuple)
# Draw cute Shinchan closed smile line
draw.arc([266, 562, 288, 578], start=20, end=160, fill=(28, 20, 20, 255), width=3)


# GRANDFATHER REST MOUTH:
# In scene_main.jpg, GF's open mouth is at x: 655 to 720, y: 375 to 415.
# Fill open mouth area with elderly skin
gf_skin_crop = scene.crop((640, 360, 655, 380))
gf_skin_avg = np.array(gf_skin_crop).mean(axis=(0,1)).astype(int)
gf_skin_tuple = (int(gf_skin_avg[0]), int(gf_skin_avg[1]), int(gf_skin_avg[2]), 255)

draw.polygon([(652, 382), (722, 382), (715, 412), (660, 412)], fill=gf_skin_tuple)
# Closed gentle wrinkled smile
draw.arc([650, 375, 720, 405], start=15, end=165, fill=(35, 22, 18, 255), width=3)
draw.line([651, 387, 647, 393], fill=(35, 22, 18, 255), width=2)
draw.line([719, 387, 723, 393], fill=(35, 22, 18, 255), width=2)
draw.arc([670, 407, 700, 420], start=20, end=160, fill=(35, 22, 18, 255), width=2) # chin crease


# CAT REST MOUTH:
# In scene_main.jpg, Cat's open mouth is at x: 392 to 430, y: 535 to 572.
cat_fur_crop = scene.crop((390, 520, 410, 535))
cat_fur_avg = np.array(cat_fur_crop).mean(axis=(0,1)).astype(int)
cat_fur_tuple = (int(cat_fur_avg[0]), int(cat_fur_avg[1]), int(cat_fur_avg[2]), 255)

draw.ellipse([390, 536, 432, 574], fill=cat_fur_tuple)
# Draw cute closed cat muzzle line
draw.line([411, 532, 411, 544], fill=(30, 20, 18, 255), width=2)
draw.arc([397, 540, 411, 552], start=0, end=180, fill=(30, 20, 18, 255), width=2)
draw.arc([411, 540, 425, 552], start=0, end=180, fill=(30, 20, 18, 255), width=2)

base_rest.save("scene_base_rest.png")
print("Saved scene_base_rest.png!")
