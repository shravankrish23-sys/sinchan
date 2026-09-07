import cv2
import numpy as np
from PIL import Image

# Load clean base image (without mouth)
base_img = Image.open("boy_base_clean.png").convert("RGBA")
W, H = base_img.size

# Convert to numpy for precise alpha masking
arr = np.array(base_img)

# 1. LEGS LAYER (Waist down: Y from 840 to 1536)
legs_arr = arr.copy()
# Fade out above waist (y: 820 to 860) for smooth blending
for y in range(860):
    if y < 820:
        legs_arr[y, :, 3] = 0
    else:
        alpha_factor = (y - 820) / 40.0
        legs_arr[y, :, 3] = (legs_arr[y, :, 3] * alpha_factor).astype(np.uint8)

legs_img = Image.fromarray(legs_arr)
legs_img.save("layer_legs.png")
print("Saved layer_legs.png (Legs & Feet)")

# 2. TORSO LAYER (Neck down to waist: Y from 430 to 880)
torso_arr = arr.copy()
# Zero out below waist
torso_arr[890:, :, 3] = 0
for y in range(860, 890):
    alpha_factor = (890 - y) / 30.0
    torso_arr[y, :, 3] = (torso_arr[y, :, 3] * alpha_factor).astype(np.uint8)

# Zero out head above neck (y < 430)
torso_arr[:430, :, 3] = 0
for y in range(430, 460):
    alpha_factor = (y - 430) / 30.0
    torso_arr[y, :, 3] = (torso_arr[y, :, 3] * alpha_factor).astype(np.uint8)

torso_img = Image.fromarray(torso_arr)
torso_img.save("layer_torso.png")
print("Saved layer_torso.png (Torso & Shirt)")

# 3. HEAD LAYER (Head & Neck: Y from 0 to 470)
head_arr = arr.copy()
head_arr[470:, :, 3] = 0
for y in range(440, 470):
    alpha_factor = (470 - y) / 30.0
    head_arr[y, :, 3] = (head_arr[y, :, 3] * alpha_factor).astype(np.uint8)

head_img = Image.fromarray(head_arr)
head_img.save("layer_head.png")
print("Saved layer_head.png (Head & Neck)")
