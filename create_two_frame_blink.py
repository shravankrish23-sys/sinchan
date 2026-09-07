from PIL import Image, ImageDraw

W, H = 1024, 1536
LINE_COLOR = (42, 24, 18, 255)
SKIN_COLOR = (253, 181, 136, 255)

# 1. Fully Closed Blink Overlay
blink_closed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d1 = ImageDraw.Draw(blink_closed)

# Left eye fill & lash
d1.ellipse([390, 255, 480, 340], fill=SKIN_COLOR)
d1.arc([388, 272, 482, 322], start=15, end=165, fill=LINE_COLOR, width=7)

# Right eye fill & lash
d1.ellipse([528, 255, 625, 342], fill=SKIN_COLOR)
d1.arc([528, 275, 626, 324], start=15, end=165, fill=LINE_COLOR, width=7)

blink_closed.save("blink_closed_clean.png")

# 2. Half-Closed Blink Overlay (Eyelid halfway down over the iris)
blink_half = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d2 = ImageDraw.Draw(blink_half)

# Left eye top half cover
d2.chord([390, 250, 480, 310], start=180, end=360, fill=SKIN_COLOR)
d2.arc([388, 260, 482, 305], start=15, end=165, fill=LINE_COLOR, width=6)

# Right eye top half cover
d2.chord([528, 252, 625, 312], start=180, end=360, fill=SKIN_COLOR)
d2.arc([528, 262, 626, 307], start=15, end=165, fill=LINE_COLOR, width=6)

blink_half.save("blink_half_clean.png")

print("Created both blink_closed_clean.png and blink_half_clean.png!")
