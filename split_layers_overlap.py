import cv2
import numpy as np
from PIL import Image

base_img = Image.open("boy_base_clean.png").convert("RGBA")
W, H = base_img.size
arr = np.array(base_img)

# 1. LEGS LAYER (From Y=790 to bottom)
# Extends high enough under the shirt hem so when torso breathes, no gap appears
legs_arr = arr.copy()
legs_arr[:790, :, 3] = 0
legs_img = Image.fromarray(legs_arr)
legs_img.save("layer_legs.png")

# 2. HEAD LAYER (From top down to Y=490)
# Neck extends under the shirt collar
head_arr = arr.copy()
head_arr[495:, :, 3] = 0
head_img = Image.fromarray(head_arr)
head_img.save("layer_head.png")

# 3. TORSO LAYER (Blue shirt and arms: Y from 445 to 885)
# Cut along the shirt collar and shirt bottom hem
torso_arr = arr.copy()
torso_arr[:445, :, 3] = 0 # above collar
torso_arr[885:, :, 3] = 0 # below shirt hem
torso_img = Image.fromarray(torso_arr)
torso_img.save("layer_torso.png")

# 4. Test Overlapping Recombine
comp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
comp.paste(legs_img, (0, 0), legs_img) # 1. Legs at back
comp.paste(head_img, (0, 0), head_img) # 2. Head behind collar
comp.paste(torso_img, (0, 0), torso_img) # 3. Torso on top

comp.save("layers_overlap_test.png")
print("Saved clean overlapping layers!")
