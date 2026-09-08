import os
import math
import json
import numpy as np
from PIL import Image, ImageOps
import imageio_ffmpeg
import subprocess

def load_rgba(path, scale=2):
    """Loads an RGBA image and optionally scales it for 2048x2048 supersampling."""
    im = Image.open(path).convert("RGBA")
    if scale != 1:
        w, h = im.size
        im = im.resize((w * scale, h * scale), Image.Resampling.LANCZOS)
    return im

def blend_images(im1, im2, factor):
    """Blends two RGBA images with factor [0..1] preserving alpha transparency."""
    if factor <= 0.0:
        return im1
    if factor >= 1.0:
        return im2
    arr1 = np.array(im1, dtype=float)
    arr2 = np.array(im2, dtype=float)
    blended = arr1 * (1.0 - factor) + arr2 * factor
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGBA")

def render_scene_dialogue():
    print("Initializing High-Resolution 2D Rigged Animation Compositor (2048x2048 Supersampled)...")
    
    # 1. Load Scene Base at 2048x2048
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
        
    # 3. Load Character Facial Assets at 2x Scale (for 2048x2048 Canvas)
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
    
    # Blinks
    sinchan_blink_half = load_rgba("scene_assets/sinchan/blink_half.png", scale=2)
    sinchan_blink_closed = load_rgba("scene_assets/sinchan/blink_closed.png", scale=2)
    
    gf_blink_half = load_rgba("scene_assets/grandfather/blink_half.png", scale=2)
    gf_blink_closed = load_rgba("scene_assets/grandfather/blink_closed.png", scale=2)
    
    cat_blink_half = load_rgba("scene_assets/cat/blink_half.png", scale=2)
    cat_blink_closed = load_rgba("scene_assets/cat/blink_closed.png", scale=2)
    cat_ear_twitch = load_rgba("scene_assets/cat/ear_twitch.png", scale=2)
    
    # 4. Calibrated 2048x2048 Anchor Positions (Exact 2x Landmark Positions)
    SINCHAN_MOUTH_POS_2X = (246 * 2, 542 * 2)    # (492, 1084)
    SINCHAN_EYES_POS_2X = (170 * 2, 482 * 2)     # (340, 964)
    
    GF_MOUTH_POS_2X = (643 * 2, 367 * 2)        # (1286, 734)
    GF_EYES_POS_2X = (620 * 2, 302 * 2)         # (1240, 604)
    
    CAT_MOUTH_POS_2X = (382 * 2, 528 * 2)       # (764, 1056)
    CAT_EYES_POS_2X = (365 * 2, 490 * 2)        # (730, 980)
    CAT_EAR_POS_2X = (338 * 2, 418 * 2)         # (676, 836)
    
    # 5. Independent Seeded Blink Timing (Center Timestamps)
    # Sinchan: 1.1s, 4.3s, 7.1s
    sinchan_blink_times = [1.12, 4.35, 7.15]
    # Grandpa: 0.85s, 2.85s, 5.85s
    gf_blink_times = [0.85, 2.85, 5.85]
    # Cat: 1.85s, 4.75s, 7.75s
    cat_blink_times = [1.85, 4.75, 7.75]
    
    # 5-Phase Blink Calculator
    # Phase durations (in seconds):
    # OPEN -> HALF (0.04s, 1 frame) -> CLOSED (0.08s, ~2.5 frames) -> HALF (0.04s, 1 frame) -> OPEN
    def get_5phase_blink(current_time, blink_list, half_img, closed_img):
        for bt in blink_list:
            dt = current_time - bt
            # Total blink window: -0.04s to +0.12s (approx 5 frames / 0.16s)
            if -0.04 <= dt < 0.00:
                # Easing into half-close
                factor = (dt + 0.04) / 0.04
                return half_img, factor
            elif 0.00 <= dt < 0.08:
                # Fully closed
                return closed_img, 1.0
            elif 0.08 <= dt < 0.12:
                # Easing out through half-close
                factor = 1.0 - (dt - 0.08) / 0.04
                return half_img, factor
        return None, 0.0

    # 6. Active Cue & Smooth Transition Calculator
    def get_cue_and_transition(current_time, start_t, end_t, cues, transition_dur=0.066):
        """
        Returns (current_cue, next_cue, blend_factor [0..1]).
        Implements 2-frame eased crossfade across phoneme boundaries.
        """
        if not (start_t <= current_time <= end_t):
            return "X", "X", 0.0
            
        rel_t = current_time - start_t
        for i, c in enumerate(cues):
            if c["start"] <= rel_t <= c["end"]:
                cur_cue = c["value"]
                # Check proximity to cue boundary for 2-frame transition easing
                time_to_end = c["end"] - rel_t
                if time_to_end < transition_dur and (i + 1 < len(cues)):
                    next_cue = cues[i + 1]["value"]
                    # Smooth ease factor [0..1]
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
    
    print(f"Rendering {total_frames} frames ({total_duration:.2f}s @ {FPS} FPS) with 2048x2048 supersampling...")
    
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        # Work at 2048x2048 canvas
        frame = base_2048.copy()
        
        # ----------------------------------------------------
        # 1. SINCHAN ANIMATION (Speech: 0.40s - 1.47s)
        # ----------------------------------------------------
        s_cur, s_next, s_blend = get_cue_and_transition(
            t, timeline["sinchan"]["start"], timeline["sinchan"]["end"], sinchan_cues
        )
        s_speaking = (timeline["sinchan"]["start"] <= t <= timeline["sinchan"]["end"])
        
        # Speech energy driven secondary vertical micro-bob (0.5 - 1.2px at 1024, 1.0 - 2.4px at 2048)
        s_dy = int(math.sin((t - timeline["sinchan"]["start"]) * 16) * 2.2) if s_speaking else 0
        
        # Mouth Viseme with 2-frame crossfade
        if s_cur in sinchan_visemes:
            s_m_cur = sinchan_visemes[s_cur]
            if s_blend > 0.0 and s_next in sinchan_visemes and s_next != s_cur:
                s_m_next = sinchan_visemes[s_next]
                s_m = blend_images(s_m_cur, s_m_next, s_blend)
            else:
                s_m = s_m_cur
            # Paste only when not X or when speaking
            if s_cur != "X" or s_speaking:
                frame.paste(s_m, (SINCHAN_MOUTH_POS_2X[0], SINCHAN_MOUTH_POS_2X[1] + s_dy), s_m)
                
        # 5-Phase Seeded Blink
        s_blink_img, s_blink_alpha = get_5phase_blink(t, sinchan_blink_times, sinchan_blink_half, sinchan_blink_closed)
        if s_blink_img is not None and s_blink_alpha > 0.05:
            if s_blink_alpha < 0.99:
                s_b_blended = blend_images(sinchan_blink_half, s_blink_img, s_blink_alpha)
            else:
                s_b_blended = s_blink_img
            frame.paste(s_b_blended, (SINCHAN_EYES_POS_2X[0], SINCHAN_EYES_POS_2X[1] + s_dy), s_b_blended)
            
        # ----------------------------------------------------
        # 2. GRANDPA ANIMATION (Speech: 2.07s - 3.65s)
        # ----------------------------------------------------
        g_cur, g_next, g_blend = get_cue_and_transition(
            t, timeline["grandfather"]["start"], timeline["grandfather"]["end"], gf_cues
        )
        g_speaking = (timeline["grandfather"]["start"] <= t <= timeline["grandfather"]["end"])
        
        # Elderly subtle speaking nod
        g_dy = int(math.sin((t - timeline["grandfather"]["start"]) * 10) * 1.8) if g_speaking else int(math.sin(t * 1.5) * 0.8)
        
        # Mouth Viseme with 2-frame crossfade
        if g_cur in gf_visemes:
            g_m_cur = gf_visemes[g_cur]
            if g_blend > 0.0 and g_next in gf_visemes and g_next != g_cur:
                g_m_next = gf_visemes[g_next]
                g_m = blend_images(g_m_cur, g_m_next, g_blend)
            else:
                g_m = g_m_cur
            if g_cur != "X" or g_speaking:
                frame.paste(g_m, (GF_MOUTH_POS_2X[0], GF_MOUTH_POS_2X[1] + g_dy), g_m)
                
        # 5-Phase Seeded Blink
        g_blink_img, g_blink_alpha = get_5phase_blink(t, gf_blink_times, gf_blink_half, gf_blink_closed)
        if g_blink_img is not None and g_blink_alpha > 0.05:
            if g_blink_alpha < 0.99:
                g_b_blended = blend_images(gf_blink_half, g_blink_img, g_blink_alpha)
            else:
                g_b_blended = g_blink_img
            frame.paste(g_b_blended, (GF_EYES_POS_2X[0], GF_EYES_POS_2X[1] + g_dy), g_b_blended)
            
        # ----------------------------------------------------
        # 3. CAT ANIMATION (Speech: 4.20s - 7.59s)
        # ----------------------------------------------------
        c_cur, c_next, c_blend = get_cue_and_transition(
            t, timeline["cat"]["start"], timeline["cat"]["end"], cat_cues
        )
        c_speaking = (timeline["cat"]["start"] <= t <= timeline["cat"]["end"])
        
        # Sassy cat head movement during speech
        c_dy = int(math.sin((t - timeline["cat"]["start"]) * 14) * 1.6) if c_speaking else 0
        
        # Mouth Viseme with 2-frame crossfade
        if c_cur in cat_visemes:
            c_m_cur = cat_visemes[c_cur]
            if c_blend > 0.0 and c_next in cat_visemes and c_next != c_cur:
                c_m_next = cat_visemes[c_next]
                c_m = blend_images(c_m_cur, c_m_next, c_blend)
            else:
                c_m = c_m_cur
            if c_cur != "X" or c_speaking:
                frame.paste(c_m, (CAT_MOUTH_POS_2X[0], CAT_MOUTH_POS_2X[1] + c_dy), c_m)
                
        # 5-Phase Seeded Blink
        c_blink_img, c_blink_alpha = get_5phase_blink(t, cat_blink_times, cat_blink_half, cat_blink_closed)
        if c_blink_img is not None and c_blink_alpha > 0.05:
            if c_blink_alpha < 0.99:
                c_b_blended = blend_images(cat_blink_half, c_blink_img, c_blink_alpha)
            else:
                c_b_blended = c_blink_img
            frame.paste(c_b_blended, (CAT_EYES_POS_2X[0], CAT_EYES_POS_2X[1] + c_dy), c_b_blended)
            
        # Secondary Motion: Cat Ear Twitch at 5.2s and 6.8s during speech
        for twitch_t in [5.2, 6.8]:
            dt_ear = t - twitch_t
            if 0.0 <= dt_ear < 0.14:
                ear_alpha = math.sin((dt_ear / 0.14) * math.pi)
                if ear_alpha > 0.2:
                    frame.paste(cat_ear_twitch, (CAT_EAR_POS_2X[0], CAT_EAR_POS_2X[1] + c_dy), cat_ear_twitch)
                break
                
        # ----------------------------------------------------
        # 4. DOWNSAMPLE 2048x2048 -> 1024x1024 VIA LANCZOS
        # ----------------------------------------------------
        frame_1024 = frame.resize((1024, 1024), Image.Resampling.LANCZOS)
        writer.send(frame_1024.tobytes())
        
    writer.close()
    
    # ----------------------------------------------------
    # 5. MUX AUDIO AND OUTPUT PRODUCTION VIDEO
    # ----------------------------------------------------
    print("Muxing animated video with scene_master_dialogue.wav...")
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
        
    print(f"\n=======================================================")
    print(f"SUCCESS: Rendered 1024x1024 30 FPS Master Video to: {os.path.abspath(final_video)}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    render_scene_dialogue()
