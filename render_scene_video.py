import os
import math
import json
import numpy as np
from PIL import Image, ImageOps
import imageio_ffmpeg
import subprocess

def load_rgba(path, scale=2):
    """Loads an RGBA image and scales it for 2048x2048 supersampling."""
    im = Image.open(path).convert("RGBA")
    if scale != 1:
        w, h = im.size
        im = im.resize((w * scale, h * scale), Image.Resampling.LANCZOS)
    return im

def blend_images(im1, im2, factor):
    """Blends two RGBA images preserving alpha transparency."""
    if factor <= 0.0:
        return im1
    if factor >= 1.0:
        return im2
    arr1 = np.array(im1, dtype=float)
    arr2 = np.array(im2, dtype=float)
    blended = arr1 * (1.0 - factor) + arr2 * factor
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGBA")

def rotate_layer_around_pivot(layer_img, angle_deg, pivot_xy, offset_xy=(0, 0)):
    """Rotates a layer around its local pivot and returns the rotated image and paste position."""
    # Rotate with high quality bicubic resampling
    rot = layer_img.rotate(angle_deg, resample=Image.Resampling.BICUBIC, center=pivot_xy, expand=False)
    return rot

def render_scene_dialogue():
    print("Initializing Professional 2D Rigged Animation Compositor (2048x2048 Supersampled)...")
    
    # 1. Load Clean Resting Scene Base
    base_1024 = Image.open("scene_base_rest.png").convert("RGBA")
    base_2048 = base_1024.resize((2048, 2048), Image.Resampling.LANCZOS)
    
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
        
    # 3. Load Visemes at 2x Scale (2048x2048 Canvas)
    def load_char_visemes(char_folder):
        vis = {}
        for cue in ["A", "B", "C", "D", "E", "F", "G", "H", "X"]:
            p = f"scene_assets/{char_folder}/viseme_{cue}.png"
            if os.path.exists(p):
                vis[cue] = load_rgba(p, scale=2)
        return vis

    sinchan_visemes = load_char_visemes("sinchan")
    gf_visemes = load_char_visemes("grandfather")
    cat_visemes = load_char_visemes("cat")
    
    # Load Blinks & Expression Assets
    sinchan_blink_half = load_rgba("scene_assets/sinchan/blink_half.png", scale=2)
    sinchan_blink_closed = load_rgba("scene_assets/sinchan/blink_closed.png", scale=2)
    
    gf_blink_half = load_rgba("scene_assets/grandfather/blink_half.png", scale=2)
    gf_blink_closed = load_rgba("scene_assets/grandfather/blink_closed.png", scale=2)
    gf_glasses = load_rgba("scene_assets/grandfather/glasses_foreground.png", scale=2)
    
    cat_blink_half = load_rgba("scene_assets/cat/blink_half.png", scale=2)
    cat_blink_closed = load_rgba("scene_assets/cat/blink_closed.png", scale=2)
    cat_blink_angry = load_rgba("scene_assets/cat/blink_angry.png", scale=2)
    cat_whiskers = load_rgba("scene_assets/cat/whiskers_foreground.png", scale=2)
    cat_ear_isolated = load_rgba("scene_assets/cat/ear_isolated.png", scale=2)
    
    # 4. Load Head Layers
    sinchan_head = load_rgba("scene_assets/sinchan/head_layer.png", scale=2)
    gf_head = load_rgba("scene_assets/grandfather/head_layer.png", scale=2)
    cat_head = load_rgba("scene_assets/cat/head_layer.png", scale=2)
    
    # Head crop anchor offsets on 2048 canvas
    SINCHAN_HEAD_ORIGIN = (80 * 2, 370 * 2)     # (160, 740)
    GF_HEAD_ORIGIN = (550 * 2, 260 * 2)         # (1100, 520)
    CAT_HEAD_ORIGIN = (325 * 2, 410 * 2)        # (650, 820)
    
    # Relative feature coordinates on local head layers (2048 scale)
    SINCHAN_LOCAL_MOUTH = ((246 - 80) * 2, (542 - 370) * 2)    # (332, 344)
    SINCHAN_LOCAL_EYES = ((170 - 80) * 2, (482 - 370) * 2)     # (180, 224)
    
    GF_LOCAL_MOUTH = ((643 - 550) * 2, (367 - 260) * 2)        # (186, 214)
    GF_LOCAL_EYES = ((620 - 550) * 2, (302 - 260) * 2)         # (140, 84)
    GF_LOCAL_GLASSES = ((615 - 550) * 2, (300 - 260) * 2)      # (130, 80)
    
    CAT_LOCAL_MOUTH = ((382 - 325) * 2, (528 - 410) * 2)       # (114, 236)
    CAT_LOCAL_EYES = ((365 - 325) * 2, (490 - 410) * 2)        # (80, 160)
    CAT_LOCAL_WHISKERS = ((345 - 325) * 2, (520 - 410) * 2)    # (40, 220)
    CAT_LOCAL_EAR = ((335 - 325) * 2, (415 - 410) * 2)         # (20, 10)
    
    # 5. Context-Aware Dialogue Blink Schedule
    # Sinchan: 0.18s (pre-speech) and 1.62s (post-speech)
    sinchan_blinks = [0.18, 1.62]
    # Grandpa: 1.75s (listening) and 3.85s (post-speech)
    gf_blinks = [1.75, 3.85]
    # Cat: 4.05s (pre-glare) and 7.85s (post-speech)
    cat_blinks = [4.05, 7.85]
    
    def get_5phase_blink(current_time, blink_list, half_img, closed_img):
        for bt in blink_list:
            dt = current_time - bt
            if -0.04 <= dt < 0.00:
                factor = (dt + 0.04) / 0.04
                return half_img, factor
            elif 0.00 <= dt < 0.08:
                return closed_img, 1.0
            elif 0.08 <= dt < 0.12:
                factor = 1.0 - (dt - 0.08) / 0.04
                return half_img, factor
        return None, 0.0

    def get_cue_and_transition(current_time, start_t, end_t, cues, transition_dur=0.066):
        if not (start_t <= current_time <= end_t):
            return "X", "X", 0.0
        rel_t = current_time - start_t
        for i, c in enumerate(cues):
            if c["start"] <= rel_t <= c["end"]:
                cur_cue = c["value"]
                time_to_end = c["end"] - rel_t
                if time_to_end < transition_dur and (i + 1 < len(cues)):
                    next_cue = cues[i + 1]["value"]
                    blend_factor = (transition_dur - time_to_end) / transition_dur
                    return cur_cue, next_cue, blend_factor
                return cur_cue, cur_cue, 0.0
        return "X", "X", 0.0

    FPS = 30
    total_frames = int(total_duration * FPS)
    
    temp_raw = "temp_scene_render.mp4"
    final_video = "scene_dialogue_animated.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    writer = imageio_ffmpeg.write_frames(
        temp_raw,
        (1024, 1024),
        fps=FPS,
        codec="libx264",
        pix_fmt_in="rgba",
        pix_fmt_out="yuv420p"
    )
    writer.send(None)
    
    print(f"Rendering {total_frames} frames ({total_duration:.2f}s @ {FPS} FPS) with 2D character rigging...")
    
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        frame = base_2048.copy()
        
        # Ambient Micro-Breathing (0.4px vertical drift for alive feel)
        ambient_breath_dy = int(math.sin(t * 2.2) * 1.0)
        
        # ----------------------------------------------------
        # 1. RIGGED SINCHAN HEAD & FACIAL COMPOSITING
        # ----------------------------------------------------
        s_speaking = (timeline["sinchan"]["start"] <= t <= timeline["sinchan"]["end"])
        s_cur, s_next, s_blend = get_cue_and_transition(
            t, timeline["sinchan"]["start"], timeline["sinchan"]["end"], sinchan_cues
        )
        
        # Assemble local head layer
        s_head_comp = sinchan_head.copy()
        
        # Dynamic Jaw Drop on open vowels (D, H = 3px, C, E = 1.5px)
        jaw_drop_y = 0
        if s_cur in ["D", "H"]:
            jaw_drop_y = 3
        elif s_cur in ["C", "E"]:
            jaw_drop_y = 1
            
        # Sinchan Mouth with 2-frame crossfade
        if s_cur in sinchan_visemes and (s_cur != "X" or s_speaking):
            s_m_cur = sinchan_visemes[s_cur]
            if s_blend > 0.0 and s_next in sinchan_visemes and s_next != s_cur:
                s_m = blend_images(s_m_cur, sinchan_visemes[s_next], s_blend)
            else:
                s_m = s_m_cur
            s_head_comp.paste(s_m, (SINCHAN_LOCAL_MOUTH[0], SINCHAN_LOCAL_MOUTH[1] + jaw_drop_y), s_m)
            
        # Sinchan Eyelids / Blink
        s_b_img, s_b_alpha = get_5phase_blink(t, sinchan_blinks, sinchan_blink_half, sinchan_blink_closed)
        if s_b_img is not None and s_b_alpha > 0.05:
            if s_b_alpha < 0.99:
                s_b = blend_images(sinchan_blink_half, s_b_img, s_b_alpha)
            else:
                s_b = s_b_img
            s_head_comp.paste(s_b, SINCHAN_LOCAL_EYES, s_b)
            
        # Unified Head Motion (speech nod & subtle tilt applied to WHOLE head)
        s_speech_dy = int(math.sin((t - timeline["sinchan"]["start"]) * 14) * 2.4) if s_speaking else ambient_breath_dy
        s_head_angle = math.sin((t - timeline["sinchan"]["start"]) * 12) * 0.35 if s_speaking else math.sin(t * 1.5) * 0.1
        
        s_head_rot = rotate_layer_around_pivot(s_head_comp, s_head_angle, pivot_xy=(260, 260))
        frame.paste(s_head_rot, (SINCHAN_HEAD_ORIGIN[0], SINCHAN_HEAD_ORIGIN[1] + s_speech_dy), s_head_rot)

        # ----------------------------------------------------
        # 2. RIGGED GRANDPA HEAD & LAYER-ORDERED GLASSES
        # ----------------------------------------------------
        g_speaking = (timeline["grandfather"]["start"] <= t <= timeline["grandfather"]["end"])
        g_cur, g_next, g_blend = get_cue_and_transition(
            t, timeline["grandfather"]["start"], timeline["grandfather"]["end"], gf_cues
        )
        
        g_head_comp = gf_head.copy()
        
        # Grandpa Eyelids (Layer 1: Behind glasses)
        g_b_img, g_b_alpha = get_5phase_blink(t, gf_blinks, gf_blink_half, gf_blink_closed)
        if g_b_img is not None and g_b_alpha > 0.05:
            if g_b_alpha < 0.99:
                g_b = blend_images(gf_blink_half, g_b_img, g_b_alpha)
            else:
                g_b = g_b_img
            g_head_comp.paste(g_b, GF_LOCAL_EYES, g_b)
            
        # Grandpa Mouth (Layer 2)
        if g_cur in gf_visemes and (g_cur != "X" or g_speaking):
            g_m_cur = gf_visemes[g_cur]
            if g_blend > 0.0 and g_next in gf_visemes and g_next != g_cur:
                g_m = blend_images(g_m_cur, gf_visemes[g_next], g_blend)
            else:
                g_m = g_m_cur
            g_head_comp.paste(g_m, GF_LOCAL_MOUTH, g_m)
            
        # Grandpa Foreground Glasses (Layer 3: Renders over eyelids to prevent clipping!)
        g_head_comp.paste(gf_glasses, GF_LOCAL_GLASSES, gf_glasses)
        
        # Unified Grandpa Head Motion
        g_speech_dy = int(math.sin((t - timeline["grandfather"]["start"]) * 9) * 2.0) if g_speaking else ambient_breath_dy
        g_head_angle = math.sin((t - timeline["grandfather"]["start"]) * 8) * 0.25 if g_speaking else math.sin(t * 1.2) * 0.08
        
        g_head_rot = rotate_layer_around_pivot(g_head_comp, g_head_angle, pivot_xy=(220, 220))
        frame.paste(g_head_rot, (GF_HEAD_ORIGIN[0], GF_HEAD_ORIGIN[1] + g_speech_dy), g_head_rot)

        # ----------------------------------------------------
        # 3. RIGGED CAT HEAD, ANGRY GLARE, WHISKERS & ELASTIC EAR
        # ----------------------------------------------------
        c_speaking = (timeline["cat"]["start"] <= t <= timeline["cat"]["end"])
        c_cur, c_next, c_blend = get_cue_and_transition(
            t, timeline["cat"]["start"], timeline["cat"]["end"], cat_cues
        )
        
        c_head_comp = cat_head.copy()
        
        # Cat Eye Emotion: Angry Squint/Glare during insult (4.6s - 5.3s)
        if 4.60 <= t <= 5.30:
            c_head_comp.paste(cat_blink_angry, CAT_LOCAL_EYES, cat_blink_angry)
        else:
            # Natural Blinks
            c_b_img, c_b_alpha = get_5phase_blink(t, cat_blinks, cat_blink_half, cat_blink_closed)
            if c_b_img is not None and c_b_alpha > 0.05:
                if c_b_alpha < 0.99:
                    c_b = blend_images(cat_blink_half, c_b_img, c_b_alpha)
                else:
                    c_b = c_b_img
                c_head_comp.paste(c_b, CAT_LOCAL_EYES, c_b)
                
        # Cat Mouth
        if c_cur in cat_visemes and (c_cur != "X" or c_speaking):
            c_m_cur = cat_visemes[c_cur]
            if c_blend > 0.0 and c_next in cat_visemes and c_next != c_cur:
                c_m = blend_images(c_m_cur, cat_visemes[c_next], c_blend)
            else:
                c_m = c_m_cur
            c_head_comp.paste(c_m, CAT_LOCAL_MOUTH, c_m)
            
        # Foreground Whiskers (Renders over open mouth)
        c_head_comp.paste(cat_whiskers, CAT_LOCAL_WHISKERS, cat_whiskers)
        
        # Elastic Ear Twitch (Physical rotation at 5.2s and 6.8s)
        ear_angle = 0.0
        for twitch_t in [5.2, 6.8]:
            dt_ear = t - twitch_t
            if 0.0 <= dt_ear < 0.18:
                # Damped oscillation: -5deg -> +2deg -> 0deg
                ear_angle = -5.0 * math.sin(dt_ear * 35.0) * math.exp(-dt_ear * 12.0)
                break
                
        if abs(ear_angle) > 0.1:
            ear_rot = rotate_layer_around_pivot(cat_ear_isolated, ear_angle, pivot_xy=(60, 65))
            c_head_comp.paste(ear_rot, CAT_LOCAL_EAR, ear_rot)
            
        # Unified Cat Head Motion
        c_speech_dy = int(math.sin((t - timeline["cat"]["start"]) * 14) * 2.2) if c_speaking else ambient_breath_dy
        c_head_angle = math.sin((t - timeline["cat"]["start"]) * 10) * 0.40 if c_speaking else 0.0
        
        c_head_rot = rotate_layer_around_pivot(c_head_comp, c_head_angle, pivot_xy=(170, 200))
        frame.paste(c_head_rot, (CAT_HEAD_ORIGIN[0], CAT_HEAD_ORIGIN[1] + c_speech_dy), c_head_rot)

        # ----------------------------------------------------
        # 4. DOWNSAMPLE 2048x2048 -> 1024x1024 VIA LANCZOS
        # ----------------------------------------------------
        frame_1024 = frame.resize((1024, 1024), Image.Resampling.LANCZOS)
        writer.send(frame_1024.tobytes())
        
    writer.close()
    
    # 5. Mux with Audio
    print("Muxing video with scene_master_dialogue.wav...")
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
        
    print(f"\nSUCCESS: Rendered Master Video to: {os.path.abspath(final_video)}")

if __name__ == "__main__":
    render_scene_dialogue()
