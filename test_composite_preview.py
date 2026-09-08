import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def validate_assets():
    print("Running Automated Quality Assurance (QA) Checks...")
    errors = []
    
    chars = ["sinchan", "grandfather", "cat"]
    visemes = ["A", "B", "C", "D", "E", "F", "G", "H", "X"]
    other_assets = ["blink_half.png", "blink_closed.png", "pupil_left.png", "pupil_right.png", "mouth_mask.png", "eye_mask.png"]
    
    for c in chars:
        # Check visemes
        for v in visemes:
            path = f"scene_assets/{c}/viseme_{v}.png"
            if not os.path.exists(path):
                errors.append(f"Missing asset: {path}")
            else:
                img = Image.open(path)
                if img.mode != "RGBA":
                    errors.append(f"Asset {path} is not RGBA mode!")
                # Check for transparent alpha presence
                alpha = np.array(img)[:, :, 3]
                if np.all(alpha == 255):
                    errors.append(f"Asset {path} is 100% opaque (missing transparency alpha)!")
                    
        # Check blinks and masks
        for o in other_assets:
            path = f"scene_assets/{c}/{o}"
            if not os.path.exists(path):
                errors.append(f"Missing asset: {path}")
                
    if os.path.exists("scene_assets/cat/ear_twitch.png"):
        ear_img = Image.open("scene_assets/cat/ear_twitch.png")
        if ear_img.mode != "RGBA":
            errors.append("cat/ear_twitch.png is not RGBA!")
    else:
        errors.append("Missing scene_assets/cat/ear_twitch.png")
        
    if not os.path.exists("scene_base_rest.png"):
        errors.append("Missing scene_base_rest.png!")
        
    if not os.path.exists("scene_master_dialogue.wav"):
        errors.append("Missing scene_master_dialogue.wav!")

    if errors:
        print("\n[FAIL] QA VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("[PASS] All character assets, alpha channels, and masks PASSED automated checks!")
        return True

def generate_zoom_previews():
    print("\nGenerating 100% Zoom Crop Inspection Previews...")
    base = Image.open("scene_base_rest.png").convert("RGBA")
    
    # ----------------------------------------------------
    # 1. SINCHAN ZOOM PREVIEW GRID
    # ----------------------------------------------------
    # Sinchan face crop box: (120, 440, 340, 620) -> 220x180 px
    sinchan_mouth_pos = (246, 542)
    sinchan_eye_pos = (170, 482)
    
    sinchan_visemes = ["X", "A", "B", "C", "D", "E", "F", "G", "H"]
    sinchan_panels = []
    
    # Rest face
    rest_sinchan = base.crop((120, 440, 340, 620))
    sinchan_panels.append(("Rest / X", rest_sinchan))
    
    for v in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        frame = base.copy()
        vm = Image.open(f"scene_assets/sinchan/viseme_{v}.png").convert("RGBA")
        frame.paste(vm, sinchan_mouth_pos, vm)
        crop = frame.crop((120, 440, 340, 620))
        sinchan_panels.append((f"Viseme {v}", crop))
        
    # Blink states
    for b_name, b_file in [("Half Blink", "blink_half.png"), ("Closed Blink", "blink_closed.png")]:
        frame = base.copy()
        b_img = Image.open(f"scene_assets/sinchan/{b_file}").convert("RGBA")
        frame.paste(b_img, sinchan_eye_pos, b_img)
        crop = frame.crop((120, 440, 340, 620))
        sinchan_panels.append((b_name, crop))
        
    # Build 3x4 grid image for Sinchan
    cols, rows = 4, 3
    panel_w, panel_h = 220, 180
    grid_img = Image.new("RGBA", (cols * panel_w, rows * (panel_h + 30)), (18, 19, 28, 255))
    draw = ImageDraw.Draw(grid_img)
    
    for idx, (label, p_img) in enumerate(sinchan_panels):
        r, c = idx // cols, idx % cols
        x = c * panel_w
        y = r * (panel_h + 30)
        grid_img.paste(p_img, (x, y))
        draw.rectangle([x, y + panel_h, x + panel_w, y + panel_h + 30], fill=(28, 30, 44, 255))
        draw.text((x + 10, y + panel_h + 8), label, fill=(240, 240, 250, 255))
        
    grid_img.save("preview_sinchan_zoom.png")
    print("Saved preview_sinchan_zoom.png")
    
    # ----------------------------------------------------
    # 2. GRANDPA ZOOM PREVIEW GRID
    # ----------------------------------------------------
    # Grandpa face crop box: (570, 270, 770, 470) -> 200x200 px
    gf_mouth_pos = (643, 367)
    gf_eye_pos = (620, 302)
    
    gf_panels = []
    rest_gf = base.crop((570, 270, 770, 470))
    gf_panels.append(("Rest / X", rest_gf))
    
    for v in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        frame = base.copy()
        vm = Image.open(f"scene_assets/grandfather/viseme_{v}.png").convert("RGBA")
        frame.paste(vm, gf_mouth_pos, vm)
        crop = frame.crop((570, 270, 770, 470))
        gf_panels.append((f"Viseme {v}", crop))
        
    for b_name, b_file in [("Half Blink", "blink_half.png"), ("Closed Blink", "blink_closed.png")]:
        frame = base.copy()
        b_img = Image.open(f"scene_assets/grandfather/{b_file}").convert("RGBA")
        frame.paste(b_img, gf_eye_pos, b_img)
        crop = frame.crop((570, 270, 770, 470))
        gf_panels.append((b_name, crop))
        
    grid_gf = Image.new("RGBA", (cols * 200, rows * (200 + 30)), (18, 19, 28, 255))
    draw_gf = ImageDraw.Draw(grid_gf)
    for idx, (label, p_img) in enumerate(gf_panels):
        r, c = idx // cols, idx % cols
        x = c * 200
        y = r * (200 + 30)
        grid_gf.paste(p_img, (x, y))
        draw_gf.rectangle([x, y + 200, x + 200, y + 200 + 30], fill=(28, 30, 44, 255))
        draw_gf.text((x + 10, y + 200 + 8), label, fill=(240, 240, 250, 255))
    grid_gf.save("preview_grandfather_zoom.png")
    print("Saved preview_grandfather_zoom.png")

    # ----------------------------------------------------
    # 3. CAT ZOOM PREVIEW GRID
    # ----------------------------------------------------
    # Cat face crop box: (330, 440, 500, 620) -> 170x180 px
    cat_mouth_pos = (382, 528)
    cat_eye_pos = (365, 490)
    cat_ear_pos = (338, 418)
    
    cat_panels = []
    rest_cat = base.crop((330, 440, 500, 620))
    cat_panels.append(("Rest / X", rest_cat))
    
    for v in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        frame = base.copy()
        vm = Image.open(f"scene_assets/cat/viseme_{v}.png").convert("RGBA")
        frame.paste(vm, cat_mouth_pos, vm)
        crop = frame.crop((330, 440, 500, 620))
        cat_panels.append((f"Viseme {v}", crop))
        
    for b_name, b_file in [("Half Blink", "blink_half.png"), ("Closed Blink", "blink_closed.png")]:
        frame = base.copy()
        b_img = Image.open(f"scene_assets/cat/{b_file}").convert("RGBA")
        frame.paste(b_img, cat_eye_pos, b_img)
        crop = frame.crop((330, 440, 500, 620))
        cat_panels.append((b_name, crop))
        
    # Ear twitch preview
    frame_ear = base.copy()
    ear_img = Image.open("scene_assets/cat/ear_twitch.png").convert("RGBA")
    frame_ear.paste(ear_img, cat_ear_pos, ear_img)
    cat_panels.append(("Ear Twitch", frame_ear.crop((330, 440, 500, 620))))
    
    grid_cat = Image.new("RGBA", (cols * 170, rows * (180 + 30)), (18, 19, 28, 255))
    draw_cat = ImageDraw.Draw(grid_cat)
    for idx, (label, p_img) in enumerate(cat_panels):
        r, c = idx // cols, idx % cols
        x = c * 170
        y = r * (180 + 30)
        grid_cat.paste(p_img, (x, y))
        draw_cat.rectangle([x, y + 180, x + 170, y + 180 + 30], fill=(28, 30, 44, 255))
        draw_cat.text((x + 8, y + 180 + 8), label, fill=(240, 240, 250, 255))
    grid_cat.save("preview_cat_zoom.png")
    print("Saved preview_cat_zoom.png")

if __name__ == "__main__":
    if validate_assets():
        generate_zoom_previews()
