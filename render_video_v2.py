import os
import math
import json
import numpy as np
from PIL import Image
import imageio_ffmpeg
import subprocess

# 1. Base setup
base_path = "boy_base_clean.png" if os.path.exists("boy_base_clean.png") else "boy.png"
base_img = Image.open(base_path).convert("RGBA")
W, H = base_img.size

# Load Rhubarb JSON
with open("lip_sync.json", "r") as f:
    lip_data = json.load(f)

duration = lip_data["metadata"]["duration"]
cues = lip_data["mouthCues"]

# Load viseme images
visemes = {}
for cue_name in ["A", "B", "C", "D", "E", "F", "G", "H", "X"]:
    path = f"visemes/{cue_name}.png"
    if os.path.exists(path):
        visemes[cue_name] = Image.open(path).convert("RGBA")

# Load blink overlay if available
blink_img = None
if os.path.exists("blink_overlay.png"):
    blink_img = Image.open("blink_overlay.png").convert("RGBA")

# Perfectly centered mouth coordinates
# Center of mouth on face is around x=510, y=365. Mouth sprite size is 100x70
MOUTH_X = 510 - 50
MOUTH_Y = 365 - 35

FPS = 30
total_frames = int(duration * FPS)
print(f"Rendering {total_frames} frames ({duration:.2f}s @ {FPS} FPS)...")

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
temp_raw = "temp_v2.mp4"
final_video = "rhubarb_character_animated_v2.mp4"

writer = imageio_ffmpeg.write_frames(
    temp_raw,
    (W, H),
    fps=FPS,
    codec="libx264",
    pix_fmt_in="rgba",
    pix_fmt_out="yuv420p"
)
writer.send(None)

# Blink intervals (e.g. at 2.2s and 5.4s)
blink_times = [2.0, 4.8]

for frame_idx in range(total_frames):
    current_time = frame_idx / FPS
    
    # Active mouth cue
    active_cue = "X"
    for cue in cues:
        if cue["start"] <= current_time <= cue["end"]:
            active_cue = cue["value"]
            break
            
    viseme_img = visemes.get(active_cue, visemes.get("X"))
    
    # Idle breathing (smooth sinusoidal sway)
    breath_cycle = math.sin(current_time * 2.8)
    sway_y = breath_cycle * 3.5
    
    # Check if blinking (150ms blink duration)
    is_blinking = any(bt <= current_time <= bt + 0.16 for bt in blink_times)
    
    frame = base_img.copy()
    
    # Paste mouth sprite with transparency
    if viseme_img:
        frame.paste(viseme_img, (MOUTH_X, int(MOUTH_Y + sway_y)), viseme_img)
        
    # Paste blink if active
    if is_blinking and blink_img:
        frame.paste(blink_img, (0, int(sway_y)), blink_img)
        
    writer.send(frame.tobytes())

writer.close()

# Mux audio
cmd = [
    ffmpeg_exe,
    "-y",
    "-i", temp_raw,
    "-i", "speech.wav",
    "-c:v", "copy",
    "-c:a", "aac",
    "-shortest",
    final_video
]
subprocess.run(cmd, check=True)

if os.path.exists(temp_raw):
    os.remove(temp_raw)

print(f"SUCCESS! Enhanced video saved to: {os.path.abspath(final_video)}")
