import cv2
import numpy as np
from PIL import Image

scene = Image.open("scene_main.jpg").convert("RGBA")

# Ceiling fan area: approx x: 620 to 930, y: 0 to 110
# Center of fan motor: (774, 52)
fan_crop = scene.crop((630, 0, 930, 110))
fan_crop.save("debug_fan.png")
print("Saved debug_fan.png")
