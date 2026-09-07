import cv2
import numpy as np
from PIL import Image, ImageDraw

# 1. Load boy base clean image
img_rgba = Image.open("boy_base_clean.png").convert("RGBA")
W, H = img_rgba.size
img_np = np.array(img_rgba)

bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
alpha = img_np[:, :, 3]

# 2. Inpaint both eyes to get a clean eyelid skin surface
eye_mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
# Left eye area (x: 380-480, y: 245-345)
eye_mask[245:345, 380:480] = 255
# Right eye area (x: 530-625, y: 250-345)
eye_mask[250:345, 530:625] = 255

inpainted_bgr = cv2.inpaint(bgr, eye_mask, inpaintRadius=8, flags=cv2.INPAINT_TELEA)
inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)

# 3. Create CLOSED EYES Overlay
closed_eyes_pil = Image.fromarray(np.dstack((inpainted_rgb, alpha)))

# Draw crisp anime curved closed eyelashes
draw = ImageDraw.Draw(closed_eyes_pil)
LINE_COLOR = (42, 24, 18, 255)

# Left eye closed smile arc (x: 395 to 475, y: 295)
draw.arc([392, 275, 478, 318], start=20, end=160, fill=LINE_COLOR, width=7)
# Eyelash flick left
draw.line([394, 300, 386, 294], fill=LINE_COLOR, width=5)

# Right eye closed smile arc (x: 535 to 615, y: 298)
draw.arc([535, 280, 618, 320], start=20, end=160, fill=LINE_COLOR, width=7)
# Eyelash flick right
draw.line([616, 302, 624, 296], fill=LINE_COLOR, width=5)

# Mask out everything except the eye regions so it's a lightweight transparent patch
closed_eyes_arr = np.array(closed_eyes_pil)
closed_eyes_alpha = np.zeros((H, W), dtype=np.uint8)
# Only keep the eye regions
closed_eyes_alpha[240:350, 375:485] = 255
closed_eyes_alpha[245:350, 525:630] = 255

# Apply smooth edge feathering
closed_eyes_alpha = cv2.GaussianBlur(closed_eyes_alpha, (15, 15), 0)
closed_eyes_arr[:, :, 3] = closed_eyes_alpha

final_closed = Image.fromarray(closed_eyes_arr)
final_closed.save("blink_closed.png")
print("Saved blink_closed.png with realistic anime closed eyes!")

# 4. Preview test
test_preview = img_rgba.copy()
test_preview.paste(final_closed, (0, 0), final_closed)
test_preview.crop((350, 180, 650, 420)).save("blink_preview_test.png")
print("Saved blink_preview_test.png!")
