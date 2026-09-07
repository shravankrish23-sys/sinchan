import os
import math
import json
import numpy as np
from PIL import Image
import imageio_ffmpeg
import subprocess

# 1. Load body layers
legs_img = Image.open("layer_legs.png").convert("RGBA")
torso_img = Image.open("layer_torso.png").convert("RGBA")
head_img = Image.open("layer_head.png").convert("RGBA")
W, H = legs_img.size

# 2. Load Rhubarb Lip Sync Data
with open("lip_sync.json", "r") as f:
    lip_data = json.load(f)

duration = lip_data["metadata"]["duration"]
cues = lip_data["mouthCues"]

# 3. Load Visemes
visemes = {}
for cue_name in ["A", "B", "C", "D", "E", "F", "G", "H", "X"]:
    path = f"visemes/{cue_name}.png"
    if os.path.exists(path):
        visemes[cue_name] = Image.open(path).convert("RGBA")

# 4. Load Blink Overlays (Half & Full Closed)
blink_closed = Image.open("blink_closed_clean.png").convert("RGBA")
blink_half = Image.open("blink_half_clean.png").convert("RGBA")

MOUTH_CENTER_X = 495
MOUTH_CENTER_Y = 360
NECK_PIVOT_X = 512
NECK_PIVOT_Y = 460

FPS = 30
total_frames = int(duration * FPS)
print(f"Rendering {total_frames} frames ({duration:.2f}s @ {FPS} FPS) with animated 3-phase eye blinks & smooth rigging...")

# Natural blink timestamps throughout the 7.6s clip
blink_timestamps = [1.2, 3.8, 6.2]

def rotate_layer_around_pivot(image, angle_deg, pivot):
    if abs(angle_deg) < 0.01:
        return image
    return image.rotate(angle_deg, resample=Image.Resampling.BICUBIC, center=pivot)

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
temp_raw = "temp_smooth_blink.mp4"
final_video = "rhubarb_character_rigged_final.mp4"

writer = imageio_ffmpeg.write_frames(
    temp_raw,
    (W, H),
    fps=FPS,
    codec="libx264",
    pix_fmt_in="rgba",
    pix_fmt_out="yuv420p"
)
writer.send(None)

smoothed_head_angle = 0.0
smoothed_torso_dy = 0.0

for frame_idx in range(total_frames):
    current_time = frame_idx / FPS
    
    # 1. Active mouth viseme
    active_cue = "X"
    for cue in cues:
        if cue["start"] <= current_time <= cue["end"]:
            active_cue = cue["value"]
            break
    mouth_sprite = visemes.get(active_cue, visemes.get("X"))
    
    # 2. Gentle Torso Breathing (Max 1.8px)
    target_torso_dy = -math.sin(current_time * 2.2) * 1.8
    smoothed_torso_dy = smoothed_torso_dy * 0.85 + target_torso_dy * 0.15
    head_dy = smoothed_torso_dy * 1.1
    
    # 3. Soft head tilt (Max 0.35° continuous micro-sway)
    target_head_angle = math.sin(current_time * 1.2) * 0.35 + math.sin(current_time * 0.6) * 0.12
    smoothed_head_angle = smoothed_head_angle * 0.85 + target_head_angle * 0.15
    
    # 4. Animated 3-Phase Eye Blink (Open -> Half -> Closed -> Half -> Open)
    current_blink_overlay = None
    for bt in blink_timestamps:
        dt = current_time - bt
        if 0.00 <= dt < 0.04:
            current_blink_overlay = blink_half
            break
        elif 0.04 <= dt < 0.12:
            current_blink_overlay = blink_closed
            break
        elif 0.12 <= dt < 0.16:
            current_blink_overlay = blink_half
            break
    
    # 5. Composite Head Layer (Head + Mouth + Animated Blink)
    head_comp = head_img.copy()
    
    # Paste Mouth Viseme
    if mouth_sprite:
        mw, mh = mouth_sprite.size
        head_comp.paste(mouth_sprite, (int(MOUTH_CENTER_X - mw/2), int(MOUTH_CENTER_Y - mh/2)), mouth_sprite)
        
    # Paste Eye Blink
    if current_blink_overlay:
        head_comp.paste(current_blink_overlay, (0, 0), current_blink_overlay)
        
    # Apply soft head rotation around neck
    head_transformed = rotate_layer_around_pivot(head_comp, smoothed_head_angle, (NECK_PIVOT_X, NECK_PIVOT_Y))
    
    # 6. Assemble Canvas
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # Layer 1: Legs & Feet (Ground locked)
    frame.paste(legs_img, (0, 0), legs_img)
    
    # Layer 2: Head & Neck (Moves with breathing + tilt, tucked behind shirt collar)
    frame.paste(head_transformed, (0, int(head_dy)), head_transformed)
    
    # Layer 3: Torso & Arms (Breathes upward, covers seams)
    frame.paste(torso_img, (0, int(smoothed_torso_dy)), torso_img)
    
    writer.send(frame.tobytes())

writer.close()

# 7. Mux Audio with Video
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

print(f"SUCCESS! Final animated video with eye blinks created at: {os.path.abspath(final_video)}")
