import os
import math
import json
import numpy as np
from PIL import Image
import imageio_ffmpeg
import subprocess

# 1. Load Scene Base (Clean rest states)
base_img = Image.open("scene_base_rest.png").convert("RGBA")
W, H = base_img.size

# 2. Load Timeline & Rhubarb Cues
with open("scene_timeline.json", "r") as f:
    timeline = json.load(f)

total_duration = timeline["total_duration"]

with open("lip_sync_sinchan.json", "r") as f:
    sinchan_cues = json.load(f)["mouthCues"]

with open("lip_sync_grandfather.json", "r") as f:
    gf_cues = json.load(f)["mouthCues"]

with open("lip_sync_cat.json", "r") as f:
    cat_cues = json.load(f)["mouthCues"]

# 3. Load Character Visemes
def load_visemes(char_folder):
    vis = {}
    for cue in ["A", "B", "C", "D", "E", "F", "G", "H", "X"]:
        p = f"scene_assets/{char_folder}/viseme_{cue}.png"
        if os.path.exists(p):
            vis[cue] = Image.open(p).convert("RGBA")
    return vis

sinchan_visemes = load_visemes("sinchan")
gf_visemes = load_visemes("grandfather")
cat_visemes = load_visemes("cat")

# 4. Load Blink Overlays
sinchan_blink_closed = Image.open("scene_assets/sinchan/blink_closed.png").convert("RGBA")
sinchan_blink_half = Image.open("scene_assets/sinchan/blink_half.png").convert("RGBA")

gf_blink_closed = Image.open("scene_assets/grandfather/blink_closed.png").convert("RGBA")
gf_blink_half = Image.open("scene_assets/grandfather/blink_half.png").convert("RGBA")

cat_blink_closed = Image.open("scene_assets/cat/blink_closed.png").convert("RGBA")
cat_blink_half = Image.open("scene_assets/cat/blink_half.png").convert("RGBA")

# 5. Exact Anchor Positions
SINCHAN_MOUTH_POS = (254, 544)
SINCHAN_EYES_POS = (176, 492)

GF_MOUTH_POS = (648, 372)
GF_EYES_POS = (628, 312)

CAT_MOUTH_POS = (386, 530)
CAT_EYES_POS = (376, 500)

# Natural independent blink timestamps
sinchan_blinks = [0.9, 3.2, 5.5, 7.7]
gf_blinks = [0.7, 2.6, 4.8, 6.9]
cat_blinks = [1.6, 3.8, 5.9, 8.0]

def get_blink_overlay(current_time, blink_list, half_img, closed_img):
    for bt in blink_list:
        dt = current_time - bt
        if 0.00 <= dt < 0.04:
            return half_img
        elif 0.04 <= dt < 0.12:
            return closed_img
        elif 0.12 <= dt < 0.16:
            return half_img
    return None

def get_active_cue(current_time, start_t, end_t, cues):
    if not (start_t <= current_time <= end_t):
        return "X"
    rel_t = current_time - start_t
    for c in cues:
        if c["start"] <= rel_t <= c["end"]:
            return c["value"]
    return "X"

FPS = 30
total_frames = int(total_duration * FPS)

temp_raw = "temp_scene_render.mp4"
final_video = "scene_dialogue_animated.mp4"
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

writer = imageio_ffmpeg.write_frames(
    temp_raw,
    (W, H),
    fps=FPS,
    codec="libx264",
    pix_fmt_in="rgba",
    pix_fmt_out="yuv420p"
)
writer.send(None)

print(f"Rendering {total_frames} frames ({total_duration:.2f}s @ {FPS} FPS)...")

for frame_idx in range(total_frames):
    t = frame_idx / FPS
    frame = base_img.copy()
    
    # ----------------------------------------
    # 1. SINCHAN ANIMATION
    # ----------------------------------------
    sinchan_cue = get_active_cue(t, timeline["sinchan"]["start"], timeline["sinchan"]["end"], sinchan_cues)
    sinchan_speaking = (timeline["sinchan"]["start"] <= t <= timeline["sinchan"]["end"])
    
    # Subtle speech gesture bounce
    sinchan_dy = int(math.sin((t - timeline["sinchan"]["start"]) * 14) * 1.5) if sinchan_speaking else 0
    
    # Sinchan Mouth
    if sinchan_cue != "X" and sinchan_cue in sinchan_visemes:
        sm = sinchan_visemes[sinchan_cue]
        frame.paste(sm, (SINCHAN_MOUTH_POS[0], SINCHAN_MOUTH_POS[1] + sinchan_dy), sm)
    
    # Sinchan Blinks
    sinchan_blink = get_blink_overlay(t, sinchan_blinks, sinchan_blink_half, sinchan_blink_closed)
    if sinchan_blink:
        frame.paste(sinchan_blink, (SINCHAN_EYES_POS[0], SINCHAN_EYES_POS[1] + sinchan_dy), sinchan_blink)
        
    # ----------------------------------------
    # 2. GRANDFATHER ANIMATION
    # ----------------------------------------
    gf_cue = get_active_cue(t, timeline["grandfather"]["start"], timeline["grandfather"]["end"], gf_cues)
    gf_speaking = (timeline["grandfather"]["start"] <= t <= timeline["grandfather"]["end"])
    
    gf_dy = int(math.sin((t - timeline["grandfather"]["start"]) * 9) * 1.2) if gf_speaking else int(math.sin(t * 1.5) * 0.6)
    
    # GF Mouth
    if gf_cue != "X" and gf_cue in gf_visemes:
        gfm = gf_visemes[gf_cue]
        frame.paste(gfm, (GF_MOUTH_POS[0], GF_MOUTH_POS[1] + gf_dy), gfm)
        
    # GF Blinks
    gf_blink = get_blink_overlay(t, gf_blinks, gf_blink_half, gf_blink_closed)
    if gf_blink:
        frame.paste(gf_blink, (GF_EYES_POS[0], GF_EYES_POS[1] + gf_dy), gf_blink)
        
    # ----------------------------------------
    # 3. CAT ANIMATION
    # ----------------------------------------
    cat_cue = get_active_cue(t, timeline["cat"]["start"], timeline["cat"]["end"], cat_cues)
    cat_speaking = (timeline["cat"]["start"] <= t <= timeline["cat"]["end"])
    
    cat_dy = int(math.sin((t - timeline["cat"]["start"]) * 12) * 1.0) if cat_speaking else 0
    
    # Cat Mouth
    if cat_cue != "X" and cat_cue in cat_visemes:
        cm = cat_visemes[cat_cue]
        frame.paste(cm, (CAT_MOUTH_POS[0], CAT_MOUTH_POS[1] + cat_dy), cm)
        
    # Cat Blinks
    cat_blink = get_blink_overlay(t, cat_blinks, cat_blink_half, cat_blink_closed)
    if cat_blink:
        frame.paste(cat_blink, (CAT_EYES_POS[0], CAT_EYES_POS[1] + cat_dy), cat_blink)
        
    writer.send(frame.tobytes())

writer.close()

# ----------------------------------------
# 4. Mux Audio and Output Final Video
# ----------------------------------------
cmd = [
    ffmpeg_exe,
    "-y",
    "-i", temp_raw,
    "-i", "scene_master_dialogue.wav",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    final_video
]
subprocess.run(cmd, check=True)

if os.path.exists(temp_raw):
    os.remove(temp_raw)

print(f"SUCCESS! Rendered animated scene to: {os.path.abspath(final_video)}")
