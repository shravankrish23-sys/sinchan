from PIL import Image

scene = Image.open("scene_main.jpg").convert("RGBA")

# Sinchan coordinates:
# Mouth center: (278, 568) -> paste top-left at (278 - 30, 568 - 30) = (248, 538)
# Eyes top-left: (170, 480)
SINCHAN_MOUTH_POS = (248, 538)
SINCHAN_EYES_POS = (170, 480)

# Cat coordinates:
# Mouth center: (413, 555) -> patch is 55x50 -> top-left at (413 - 27, 555 - 24) = (386, 531)
# Eyes top-left: (365, 490)
CAT_MOUTH_POS = (386, 531)
CAT_EYES_POS = (365, 490)

# Grandfather coordinates:
# Mouth center: (688, 395) -> patch is 80x60 -> top-left at (688 - 40, 395 - 28) = (648, 367)
# Eyes top-left: (620, 300)
GF_MOUTH_POS = (648, 367)
GF_EYES_POS = (620, 300)

# Preview 1: All Neutral Base
prev_neutral = scene.copy()
sinchan_base = Image.open("scene_assets/sinchan/base_patch.png").convert("RGBA")
cat_base = Image.open("scene_assets/cat/base_patch.png").convert("RGBA")
gf_base = Image.open("scene_assets/grandfather/base_patch.png").convert("RGBA")

prev_neutral.paste(sinchan_base, SINCHAN_MOUTH_POS, sinchan_base)
prev_neutral.paste(cat_base, CAT_MOUTH_POS, cat_base)
prev_neutral.paste(gf_base, GF_MOUTH_POS, gf_base)
prev_neutral.save("preview_neutral.png")

# Preview 2: Sinchan Talking ('D' wide) + Cat Irritated + GF Listening
prev_talk1 = scene.copy()
sinchan_d = Image.open("scene_assets/sinchan/viseme_D.png").convert("RGBA")
prev_talk1.paste(sinchan_d, SINCHAN_MOUTH_POS, sinchan_d)
prev_talk1.paste(cat_base, CAT_MOUTH_POS, cat_base)
prev_talk1.paste(gf_base, GF_MOUTH_POS, gf_base)
prev_talk1.save("preview_sinchan_talking.png")

# Preview 3: Grandfather Talking ('D') + Sinchan Listening + Cat Blink
prev_talk2 = scene.copy()
gf_d = Image.open("scene_assets/grandfather/viseme_D.png").convert("RGBA")
cat_blink = Image.open("scene_assets/cat/blink_closed.png").convert("RGBA")
prev_talk2.paste(sinchan_base, SINCHAN_MOUTH_POS, sinchan_base)
prev_talk2.paste(cat_base, CAT_MOUTH_POS, cat_base)
prev_talk2.paste(cat_blink, CAT_EYES_POS, cat_blink)
prev_talk2.paste(gf_d, GF_MOUTH_POS, gf_d)
prev_talk2.save("preview_gf_talking.png")

# Preview 4: Cat Talking ('D' wide) + Sinchan Blink + GF Smile
prev_talk3 = scene.copy()
cat_d = Image.open("scene_assets/cat/viseme_D.png").convert("RGBA")
sinchan_blink = Image.open("scene_assets/sinchan/blink_closed.png").convert("RGBA")
prev_talk3.paste(sinchan_blink, SINCHAN_EYES_POS, sinchan_blink)
prev_talk3.paste(sinchan_base, SINCHAN_MOUTH_POS, sinchan_base)
prev_talk3.paste(cat_d, CAT_MOUTH_POS, cat_d)
prev_talk3.paste(gf_base, GF_MOUTH_POS, gf_base)
prev_talk3.save("preview_cat_talking.png")

print("Saved preview test images!")
