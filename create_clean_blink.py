import numpy as np
from PIL import Image, ImageDraw

base_img = Image.open("boy_base_clean.png").convert("RGBA")
W, H = base_img.size

blink_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(blink_img)

LINE_COLOR = (42, 24, 18, 255)
SKIN_COLOR = (253, 181, 136, 255) # Peach skin tone

# 1. Left Eye: Fill white sclera / iris area (x: 395 to 475, y: 260 to 335)
draw.ellipse([395, 260, 475, 335], fill=SKIN_COLOR)
# Closed lash curve
draw.arc([392, 275, 478, 320], start=20, end=160, fill=LINE_COLOR, width=7)

# 2. Right Eye: Fill white sclera / iris (x: 535 to 615, y: 262 to 338)
draw.ellipse([538, 262, 618, 338], fill=SKIN_COLOR)
# Closed lash curve
draw.arc([535, 278, 620, 322], start=20, end=160, fill=LINE_COLOR, width=7)

blink_img.save("blink_closed_clean.png")

# Test on face
test_comp = base_img.copy()
test_comp.paste(blink_img, (0, 0), blink_img)
test_comp.crop((350, 180, 650, 420)).save("blink_test_clean.png")
print("Saved clean blink_test_clean.png!")
