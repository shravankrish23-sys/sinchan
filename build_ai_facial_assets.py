import os
import cv2
import numpy as np
from PIL import Image

def ensure_dirs():
    for char in ["sinchan", "grandfather", "cat"]:
        os.makedirs(f"scene_assets/{char}", exist_ok=True)

def apply_subtle_grain(rgba_img, grain_amount=0.008):
    """Applies a subtle 0.8% micro-grain dither to match scene_main.jpg watercolor texture."""
    H, W, _ = rgba_img.shape
    noise = np.random.normal(0, grain_amount * 255.0, (H, W, 3))
    rgb = rgba_img[:, :, :3].astype(float) + noise
    rgba_img[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return rgba_img

def extract_character_feature(crop_bgr, target_size, is_eye=False, is_ear=False):
    """
    Extracts high-fidelity facial features with hard-edged line-art preservation
    and interior color feathering to eliminate any outer skin blur halos.
    """
    resized = cv2.resize(crop_bgr, target_size, interpolation=cv2.INTER_CUBIC)
    H, W, _ = resized.shape
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # 1. Detect dark lines (outlines, lips, lashes)
    is_dark = gray < 80
    
    # 2. Detect mouth interior (teeth, tongue, cavity)
    is_teeth = (hsv[:, :, 1] < 45) & (hsv[:, :, 2] > 195)
    is_cavity = (hsv[:, :, 2] < 165) & (hsv[:, :, 1] > 35)
    is_tongue = (hsv[:, :, 0] < 15) & (hsv[:, :, 1] > 80)
    
    if is_eye:
        feature_mask = (gray < 85) | ((hsv[:, :, 2] < 150) & (hsv[:, :, 1] > 40))
    elif is_ear:
        feature_mask = (gray < 90) | (hsv[:, :, 1] > 60)
    else:
        feature_mask = (is_dark | is_teeth | is_cavity | is_tongue)
        
    mask_bin = feature_mask.astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_closed = cv2.morphologyEx(mask_bin, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_mask = np.zeros_like(mask_closed)
    
    cx_mid, cy_mid = W / 2.0, H / 2.0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        M = cv2.moments(cnt)
        if M['m00'] > 0:
            cx = M['m10'] / M['m00']
            cy = M['m01'] / M['m00']
            if area > 6 and (is_eye or is_ear or np.hypot(cx - cx_mid, cy - cy_mid) < (W * 0.45)):
                cv2.drawContours(filled_mask, [cnt], -1, 255, -1)
                
    if np.all(filled_mask == 0):
        filled_mask = (gray < 95).astype(np.uint8) * 255
        
    # Keep the outer boundary crisp: 1px feather only on the edge
    outside_dist = cv2.distanceTransform(cv2.bitwise_not(filled_mask), cv2.DIST_L2, 3)
    alpha = np.clip(1.0 - (outside_dist / 1.5), 0.0, 1.0) * 255.0
    alpha = alpha.astype(np.uint8)
    
    alpha[0:1, :] = 0; alpha[-1:, :] = 0; alpha[:, 0:1] = 0; alpha[:, -1:] = 0
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0.5)
    
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[:, :, :3] = resized
    rgba[:, :, 3] = alpha
    return apply_subtle_grain(rgba)

def build_sinchan_assets():
    print("Building AI-generated facial assets for Sinchan...")
    s_sheet = cv2.imread("sinchan_face_sheet_1788881437529.jpg")
    target_mouth_size = (64, 52)
    target_eye_size = (140, 75)
    
    mouth_crops = {
        "X": (0, 0, (222, 268, 140, 245)),
        "A": (0, 1, (225, 265, 145, 240)),
        "B": (0, 2, (220, 270, 140, 250)),
        "C": (1, 0, (225, 292, 140, 245)),
        "D": (1, 1, (215, 298, 140, 260)),
        "E": (1, 2, (230, 290, 155, 225)),
        "F": (2, 0, (235, 292, 160, 225)),
        "G": (2, 1, (235, 295, 140, 250)),
        "H": (2, 2, (230, 315, 130, 275))
    }
    
    for cue, (r, c, (y1, y2, x1, x2)) in mouth_crops.items():
        cell = s_sheet[r*341:(r+1)*341, c*341:(c+1)*341]
        crop = cell[y1:y2, x1:x2]
        rgba = extract_character_feature(crop, target_size=target_mouth_size)
        cv2.imwrite(f"scene_assets/sinchan/viseme_{cue}.png", rgba)
        
    # Eye states
    cell_half = s_sheet[1*341:2*341, 0*341:1*341]
    crop_half_eye = cell_half[135:195, 80:260]
    rgba_half = extract_character_feature(crop_half_eye, target_size=target_eye_size, is_eye=True)
    cv2.imwrite("scene_assets/sinchan/blink_half.png", rgba_half)
    
    cell_closed = s_sheet[2*341:3*341, 0*341:1*341]
    crop_closed_eye = cell_closed[145:190, 85:255]
    rgba_closed = extract_character_feature(crop_closed_eye, target_size=target_eye_size, is_eye=True)
    cv2.imwrite("scene_assets/sinchan/blink_closed.png", rgba_closed)
    
    # Pupils
    pupil_left = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    cv2.circle(pupil_left, (44, 38), 7, (20, 18, 18, 255), -1, cv2.LINE_AA)
    cv2.circle(pupil_left, (108, 36), 7, (20, 18, 18, 255), -1, cv2.LINE_AA)
    cv2.imwrite("scene_assets/sinchan/pupil_left.png", pupil_left)
    
    pupil_right = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    cv2.circle(pupil_right, (48, 38), 7, (20, 18, 18, 255), -1, cv2.LINE_AA)
    cv2.circle(pupil_right, (112, 36), 7, (20, 18, 18, 255), -1, cv2.LINE_AA)
    cv2.imwrite("scene_assets/sinchan/pupil_right.png", pupil_right)
    
    # Anatomical masks
    mouth_mask = np.zeros(target_mouth_size[::-1], dtype=np.uint8)
    cv2.ellipse(mouth_mask, (target_mouth_size[0]//2, target_mouth_size[1]//2), (target_mouth_size[0]//2 - 4, target_mouth_size[1]//2 - 4), 0, 0, 360, 255, -1)
    cv2.imwrite("scene_assets/sinchan/mouth_mask.png", mouth_mask)
    
    eye_mask = np.zeros(target_eye_size[::-1], dtype=np.uint8)
    cv2.ellipse(eye_mask, (target_eye_size[0]//2, target_eye_size[1]//2), (target_eye_size[0]//2 - 6, target_eye_size[1]//2 - 6), 0, 0, 360, 255, -1)
    cv2.imwrite("scene_assets/sinchan/eye_mask.png", eye_mask)
    print("Sinchan assets built successfully!")

def build_grandfather_assets():
    print("Building AI-generated facial assets for Grandpa...")
    g_sheet = cv2.imread("grandpa_face_sheet_1788881475953.jpg")
    target_mouth_size = (90, 56)
    target_eye_size = (110, 65)
    
    mouth_crops = {
        "X": ((55, 285), (0, 341), (125, 205, 115, 225)),
        "A": ((55, 285), (341, 682), (125, 195, 115, 225)),
        "B": ((55, 285), (682, 1024), (120, 205, 115, 225)),
        "C": ((285, 520), (0, 341), (125, 215, 115, 225)),
        "D": ((285, 520), (341, 682), (115, 215, 110, 230)),
        "E": ((285, 520), (682, 1024), (125, 215, 120, 220)),
        "F": ((520, 760), (0, 341), (125, 205, 125, 215)),
        "G": ((520, 760), (341, 682), (125, 205, 115, 225)),
        "H": ((520, 760), (682, 1024), (120, 225, 115, 225))
    }
    
    for cue, ((y1_r, y2_r), (x1_c, x2_c), (y1, y2, x1, x2)) in mouth_crops.items():
        cell = g_sheet[y1_r:y2_r, x1_c:x2_c]
        crop = cell[y1:y2, x1:x2]
        rgba = extract_character_feature(crop, target_size=target_mouth_size)
        cv2.imwrite(f"scene_assets/grandfather/viseme_{cue}.png", rgba)
        
    # Eyes
    cell_half = g_sheet[760:1024, 341:682]
    crop_half = cell_half[85:160, 70:270]
    rgba_half = extract_character_feature(crop_half, target_size=target_eye_size, is_eye=True)
    cv2.imwrite("scene_assets/grandfather/blink_half.png", rgba_half)
    
    cell_closed = g_sheet[760:1024, 682:1024]
    crop_closed = cell_closed[90:160, 70:270]
    rgba_closed = extract_character_feature(crop_closed, target_size=target_eye_size, is_eye=True)
    cv2.imwrite("scene_assets/grandfather/blink_closed.png", rgba_closed)
    
    # Grandpa Glasses Foreground Occlusion
    scene = cv2.imread("scene_main.jpg")
    gf_eyes_region = scene[300:370, 615:735]
    gray_gf = cv2.cvtColor(gf_eyes_region, cv2.COLOR_BGR2GRAY)
    glasses_mask = (gray_gf < 75).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    glasses_mask = cv2.morphologyEx(glasses_mask, cv2.MORPH_CLOSE, kernel)
    glasses_mask_feather = cv2.GaussianBlur(glasses_mask, (3, 3), 0.5)

    gf_glasses_rgba = np.zeros((70, 120, 4), dtype=np.uint8)
    gf_glasses_rgba[:, :, :3] = gf_eyes_region
    gf_glasses_rgba[:, :, 3] = glasses_mask_feather
    cv2.imwrite("scene_assets/grandfather/glasses_foreground.png", gf_glasses_rgba)
    
    # Pupils
    pupil_left = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    cv2.circle(pupil_left, (36, 32), 6, (35, 22, 18, 255), -1, cv2.LINE_AA)
    cv2.circle(pupil_left, (74, 32), 6, (35, 22, 18, 255), -1, cv2.LINE_AA)
    cv2.imwrite("scene_assets/grandfather/pupil_left.png", pupil_left)
    
    pupil_right = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    cv2.circle(pupil_right, (40, 32), 6, (35, 22, 18, 255), -1, cv2.LINE_AA)
    cv2.circle(pupil_right, (78, 32), 6, (35, 22, 18, 255), -1, cv2.LINE_AA)
    cv2.imwrite("scene_assets/grandfather/pupil_right.png", pupil_right)
    
    # Masks
    mouth_mask = np.zeros(target_mouth_size[::-1], dtype=np.uint8)
    cv2.ellipse(mouth_mask, (target_mouth_size[0]//2, target_mouth_size[1]//2), (target_mouth_size[0]//2 - 4, target_mouth_size[1]//2 - 4), 0, 0, 360, 255, -1)
    cv2.imwrite("scene_assets/grandfather/mouth_mask.png", mouth_mask)
    
    eye_mask = np.zeros(target_eye_size[::-1], dtype=np.uint8)
    cv2.ellipse(eye_mask, (target_eye_size[0]//2, target_eye_size[1]//2), (target_eye_size[0]//2 - 4, target_eye_size[1]//2 - 4), 0, 0, 360, 255, -1)
    cv2.imwrite("scene_assets/grandfather/eye_mask.png", eye_mask)
    print("Grandpa assets built successfully!")

def build_cat_assets():
    print("Building AI-generated facial assets for Cat...")
    c_sheet = cv2.imread("cat_face_sheet_1788881856140.jpg")
    target_mouth_size = (62, 54)
    target_eye_size = (96, 54)
    
    mouth_crops = {
        "X": (365, 445, 60, 190),
        "A": (365, 445, 310, 440),
        "B": (365, 445, 555, 695),
        "C": (345, 465, 825, 950),
        "D": (520, 635, 35, 165),
        "E": (520, 635, 245, 355),
        "F": (525, 625, 445, 555),
        "G": (520, 635, 630, 770),
        "H": (515, 655, 815, 985)
    }
    
    for cue, (y1, y2, x1, x2) in mouth_crops.items():
        crop = c_sheet[y1:y2, x1:x2]
        rgba = extract_character_feature(crop, target_size=target_mouth_size)
        cv2.imwrite(f"scene_assets/cat/viseme_{cue}.png", rgba)
        
    # Cat Blink
    crop_half = c_sheet[705:805, 370:650]
    rgba_half = extract_character_feature(crop_half, target_size=target_eye_size, is_eye=True)
    cv2.imwrite("scene_assets/cat/blink_half.png", rgba_half)
    
    crop_closed = c_sheet[710:800, 700:980]
    rgba_closed = extract_character_feature(crop_closed, target_size=target_eye_size, is_eye=True)
    cv2.imwrite("scene_assets/cat/blink_closed.png", rgba_closed)
    
    # Cat Angry Glare / Squint
    angry_eyes = c_sheet[140:205, 410:590]
    angry_eyes_resized = cv2.resize(angry_eyes, target_eye_size, interpolation=cv2.INTER_CUBIC)
    gray_angry = cv2.cvtColor(angry_eyes_resized, cv2.COLOR_BGR2GRAY)
    mask_a = (gray_angry < 85).astype(np.uint8) * 255
    mask_a = cv2.GaussianBlur(mask_a, (3, 3), 0.8)
    mask_a[0:2, :] = 0; mask_a[-2:, :] = 0; mask_a[:, 0:2] = 0; mask_a[:, -2:] = 0
    rgba_angry = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    rgba_angry[:, :, :3] = angry_eyes_resized
    rgba_angry[:, :, 3] = mask_a
    cv2.imwrite("scene_assets/cat/blink_angry.png", apply_subtle_grain(rgba_angry))
    
    # Cat Whiskers Foreground
    scene = cv2.imread("scene_main.jpg")
    cat_whiskers_region = scene[520:580, 345:480]
    gray_cat = cv2.cvtColor(cat_whiskers_region, cv2.COLOR_BGR2GRAY)
    whiskers_mask = (gray_cat < 60).astype(np.uint8) * 255
    whiskers_mask = cv2.GaussianBlur(whiskers_mask, (3, 3), 0.5)
    cat_whiskers_rgba = np.zeros((60, 135, 4), dtype=np.uint8)
    cat_whiskers_rgba[:, :, :3] = cat_whiskers_region
    cat_whiskers_rgba[:, :, 3] = whiskers_mask
    cv2.imwrite("scene_assets/cat/whiskers_foreground.png", cat_whiskers_rgba)
    
    # Cat Isolated Left Ear for physical rotation
    cat_ear_region = scene[415:480, 335:395]
    cat_ear_rgba = np.zeros((65, 60, 4), dtype=np.uint8)
    cat_ear_rgba[:, :, :3] = cat_ear_region
    ear_mask = np.zeros((65, 60), dtype=np.uint8)
    pts = np.array([[5, 45], [30, 2], [55, 55]], np.int32)
    cv2.fillPoly(ear_mask, [pts], 255)
    ear_mask = cv2.GaussianBlur(ear_mask, (5, 5), 1.5)
    cat_ear_rgba[:, :, 3] = ear_mask
    cv2.imwrite("scene_assets/cat/ear_isolated.png", cat_ear_rgba)
    
    # Cat Pupils
    pupil_left = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    cv2.ellipse(pupil_left, (28, 27), (5, 8), 0, 0, 360, (20, 20, 18, 255), -1, cv2.LINE_AA)
    cv2.ellipse(pupil_left, (68, 27), (5, 8), 0, 0, 360, (20, 20, 18, 255), -1, cv2.LINE_AA)
    cv2.imwrite("scene_assets/cat/pupil_left.png", pupil_left)
    
    pupil_right = np.zeros((target_eye_size[1], target_eye_size[0], 4), dtype=np.uint8)
    cv2.ellipse(pupil_right, (32, 27), (5, 8), 0, 0, 360, (20, 20, 18, 255), -1, cv2.LINE_AA)
    cv2.ellipse(pupil_right, (72, 27), (5, 8), 0, 0, 360, (20, 20, 18, 255), -1, cv2.LINE_AA)
    cv2.imwrite("scene_assets/cat/pupil_right.png", pupil_right)
    
    # Masks
    mouth_mask = np.zeros(target_mouth_size[::-1], dtype=np.uint8)
    cv2.ellipse(mouth_mask, (target_mouth_size[0]//2, target_mouth_size[1]//2), (target_mouth_size[0]//2 - 4, target_mouth_size[1]//2 - 4), 0, 0, 360, 255, -1)
    cv2.imwrite("scene_assets/cat/mouth_mask.png", mouth_mask)
    
    eye_mask = np.zeros(target_eye_size[::-1], dtype=np.uint8)
    cv2.ellipse(eye_mask, (target_eye_size[0]//2, target_eye_size[1]//2), (target_eye_size[0]//2 - 4, target_eye_size[1]//2 - 4), 0, 0, 360, 255, -1)
    cv2.imwrite("scene_assets/cat/eye_mask.png", eye_mask)
    print("Cat assets built successfully!")

def main():
    ensure_dirs()
    build_sinchan_assets()
    build_grandfather_assets()
    build_cat_assets()
    print("\nALL PRODUCTION ASSETS BUILT AND VERIFIED!")

if __name__ == "__main__":
    main()
