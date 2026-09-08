from PIL import Image, ImageDraw, ImageFont

img = Image.open("scene_main.jpg").convert("RGBA")

# Let's crop Sinchan's features:
# Head roughly: (50, 380) to (360, 620)
# Let's crop sinchan's mouth area:
sinchan_mouth = img.crop((260, 550, 300, 590))
sinchan_mouth.save("debug_sinchan_mouth.png")

# Sinchan's eyes area:
sinchan_eyes = img.crop((170, 480, 310, 560))
sinchan_eyes.save("debug_sinchan_eyes.png")

# Cat's mouth area:
cat_mouth = img.crop((390, 530, 435, 575))
cat_mouth.save("debug_cat_mouth.png")

# Cat's eyes area:
cat_eyes = img.crop((365, 490, 460, 545))
cat_eyes.save("debug_cat_eyes.png")

# Grandfather's mouth area:
gf_mouth = img.crop((650, 370, 725, 420))
gf_mouth.save("debug_gf_mouth.png")

# Grandfather's eyes area:
gf_eyes = img.crop((620, 300, 725, 365))
gf_eyes.save("debug_gf_eyes.png")

print("Saved feature crops!")
