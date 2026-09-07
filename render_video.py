import os
import math
import json
import numpy as np
from PIL import Image
import imageio_ffmpeg

# Load assets
base_img = Image.open("boy.png").convert("RGBA")
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

# Target mouth location on boy.png
MOUTH_X = 440
MOUTH_Y = 345

FPS = 30
total_frames = int(duration * FPS)
print(f"Rendering {total_frames} frames ({duration:.2f}s @ {FPS} FPS)...")

# Setup ffmpeg writer
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
temp_raw_video = "temp_video.mp4"
final_video = "rhubarb_character_animated.mp4"

writer = imageio_ffmpeg.write_frames(
    temp_raw_video,
    (W, H),
    fps=FPS,
    codec="libx264",
    pix_fmt_in="rgba",
    pix_fmt_out="yuv420p"
)
writer.send(None) # start generator

for frame_idx in range(total_frames):
    current_time = frame_idx / FPS
    
    # 1. Find active viseme
    active_cue = "X"
    for cue in cues:
        if cue["start"] <= current_time <= cue["end"]:
            active_cue = cue["value"]
            break
            
    viseme_img = visemes.get(active_cue, visemes.get("X"))
    
    # 2. Subtle idle breathing (sine wave float + slight scale)
    breath_cycle = math.sin(current_time * 3.0) # ~2-second breathing cycle
    sway_y = breath_cycle * 4.0 # 4 pixel subtle vertical sway
    
    # Composite frame
    frame = base_img.copy()
    if viseme_img:
        frame.paste(viseme_img, (MOUTH_X, int(MOUTH_Y + sway_y)), viseme_img)
    
    # Convert PIL Image to raw RGBA bytes
    frame_bytes = frame.tobytes()
    writer.send(frame_bytes)

writer.close()
print("Raw video rendered successfully!")

# Now mux audio (speech.wav) with video using ffmpeg
print("Muxing audio with video...")
import subprocess
cmd = [
    ffmpeg_exe,
    "-y",
    "-i", temp_raw_video,
    "-i", "speech.wav",
    "-c:v", "copy",
    "-c:a", "aac",
    "-shortest",
    final_video
]
subprocess.run(cmd, check=True)

if os.path.exists(temp_raw_video):
    os.remove(temp_raw_video)

print(f"SUCCESS! Final animated video created at: {os.path.abspath(final_video)}")
