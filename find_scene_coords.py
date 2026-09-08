import cv2
import numpy as np
from PIL import Image, ImageDraw

img = Image.open("scene_main.jpg").convert("RGBA")
W, H = img.size

# Let's draw guide boxes on a debug copy to dial in the exact coordinates
debug = img.copy()
draw = ImageDraw.Draw(debug)

# Estimates:
# Sinchan:
# Head box: (55, 380, 350, 610)
# Left eye: ~ (150, 520)
# In debug_sinchan_face.png (cropped at 50, 380, 350, 620):
# Mouth: roughly around center of cheek/face.
# Let's mark specific coordinate grids to verify.

# Draw 50px grid lines over the character face areas
for x in range(0, 1024, 25):
    draw.line([(x, 0), (x, 1024)], fill=(200, 200, 200, 80), width=1)
for y in range(0, 1024, 25):
    draw.line([(0, y), (1024, y)], fill=(200, 200, 200, 80), width=1)

# Annotate with numbers every 50px
from PIL import ImageFont
try:
    font = ImageFont.load_default()
except:
    font = None

for x in range(0, 1024, 100):
    for y in range(0, 1024, 100):
        draw.text((x+2, y+2), f"{x},{y}", fill=(255, 0, 0, 255), font=font)

debug.save("scene_grid.png")
print("Saved scene_grid.png")
