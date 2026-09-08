import os
import cv2
import numpy as np
from PIL import Image

def create_scene_base_rest(input_scene="scene_main.jpg", output_scene="scene_base_rest.png"):
    print(f"Loading {input_scene} for clean resting state reconstruction...")
    scene = cv2.imread(input_scene)
    H, W, _ = scene.shape
    
    # ----------------------------------------------------
    # 1. IDENTIFY INTERIOR OPEN MOUTHS
    # ----------------------------------------------------
    mask_sinchan = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(mask_sinchan, (279, 572), (10, 9), 0, 0, 360, 255, -1)
    
    mask_gf = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(mask_gf, (685, 396), (25, 14), 0, 0, 360, 255, -1)
    
    mask_cat = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(mask_cat, (412, 554), (14, 13), 0, 0, 360, 255, -1)
    
    inpaint_mask = cv2.bitwise_or(mask_sinchan, cv2.bitwise_or(mask_gf, mask_cat))
    
    # Inpaint interior with surrounding skin/fur texture
    rest_scene = cv2.inpaint(scene, inpaint_mask, inpaintRadius=4, flags=cv2.INPAINT_TELEA)
    
    # ----------------------------------------------------
    # 2. DRAW NATURAL CLOSED RESTING LINE ART
    # ----------------------------------------------------
    # Sinchan: subtle curved closed smile line matching Crayon Shinchan 2D art
    cv2.ellipse(rest_scene, (278, 568), (11, 7), 0, 20, 160, (28, 20, 20), 2, cv2.LINE_AA)
    
    # Grandpa: gentle wrinkled resting smile matching original line color & chin crease
    cv2.ellipse(rest_scene, (685, 390), (32, 11), 0, 20, 160, (35, 22, 18), 2, cv2.LINE_AA)
    cv2.ellipse(rest_scene, (685, 412), (15, 6), 0, 30, 150, (45, 30, 25), 2, cv2.LINE_AA)
    
    # Cat: authentic Japanese anime 'w' muzzle resting lines
    cv2.ellipse(rest_scene, (405, 545), (7, 6), 0, 0, 180, (30, 20, 18), 2, cv2.LINE_AA)
    cv2.ellipse(rest_scene, (419, 545), (7, 6), 0, 0, 180, (30, 20, 18), 2, cv2.LINE_AA)
    cv2.line(rest_scene, (412, 538), (412, 545), (30, 20, 18), 2, cv2.LINE_AA)
    
    # Save output
    cv2.imwrite(output_scene, rest_scene)
    
    # ----------------------------------------------------
    # 3. EXTRACT ISOLATED HEAD LAYERS FOR ORGANIC RIGGING
    # ----------------------------------------------------
    # Sinchan Head Layer: (80..340, 370..630) -> 260x260 px
    sinchan_head_crop = rest_scene[370:630, 80:340]
    s_h_mask = np.zeros((260, 260), dtype=np.uint8)
    cv2.ellipse(s_h_mask, (135, 135), (105, 95), -15, 0, 360, 255, -1)
    cv2.ellipse(s_h_mask, (120, 70), (90, 60), -20, 0, 360, 255, -1)
    s_h_mask = cv2.GaussianBlur(s_h_mask, (5, 5), 1.5)
    s_h_rgba = np.zeros((260, 260, 4), dtype=np.uint8)
    s_h_rgba[:, :, :3] = sinchan_head_crop
    s_h_rgba[:, :, 3] = s_h_mask
    cv2.imwrite("scene_assets/sinchan/head_layer.png", s_h_rgba)
    
    # Grandpa Head Layer: (550..770, 260..480) -> 220x220 px
    gf_head_crop = rest_scene[260:480, 550:770]
    g_h_mask = np.zeros((220, 220), dtype=np.uint8)
    cv2.ellipse(g_h_mask, (115, 105), (85, 95), 0, 0, 360, 255, -1)
    g_h_mask = cv2.GaussianBlur(g_h_mask, (5, 5), 1.5)
    g_h_rgba = np.zeros((220, 220, 4), dtype=np.uint8)
    g_h_rgba[:, :, :3] = gf_head_crop
    g_h_rgba[:, :, 3] = g_h_mask
    cv2.imwrite("scene_assets/grandfather/head_layer.png", g_h_rgba)
    
    # Cat Head Layer: (325..495, 410..610) -> 200x170 px
    cat_head_crop = rest_scene[410:610, 325:495]
    c_h_mask = np.zeros((200, 170), dtype=np.uint8)
    cv2.ellipse(c_h_mask, (85, 105), (75, 75), 0, 0, 360, 255, -1)
    # Ears
    cv2.fillPoly(c_h_mask, [np.array([[15, 40], [40, 5], [65, 60]], np.int32)], 255)
    cv2.fillPoly(c_h_mask, [np.array([[110, 60], [135, 5], [160, 40]], np.int32)], 255)
    c_h_mask = cv2.GaussianBlur(c_h_mask, (5, 5), 1.5)
    c_h_rgba = np.zeros((200, 170, 4), dtype=np.uint8)
    c_h_rgba[:, :, :3] = cat_head_crop
    c_h_rgba[:, :, 3] = c_h_mask
    cv2.imwrite("scene_assets/cat/head_layer.png", c_h_rgba)

    print("SUCCESS: Inpainted scene_base_rest.png and created rigged character head layers!")
    return rest_scene

if __name__ == "__main__":
    create_scene_base_rest()
