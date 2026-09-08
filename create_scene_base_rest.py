import os
import cv2
import numpy as np
from PIL import Image

def create_scene_base_rest(input_scene="scene_main.jpg", output_scene="scene_base_rest.png"):
    print(f"Loading {input_scene} for organic base reconstruction...")
    scene = cv2.imread(input_scene)
    H, W, _ = scene.shape
    
    # ----------------------------------------------------
    # 1. IDENTIFY PRECISE INTERIOR MOUTH OPENINGS
    # ----------------------------------------------------
    # Sinchan interior mouth opening in scene_main.jpg: (center ~ 279, 571)
    mask_sinchan = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(mask_sinchan, (279, 572), (10, 9), 0, 0, 360, 255, -1)
    
    # Grandpa interior mouth opening in scene_main.jpg: (center ~ 685, 396)
    mask_gf = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(mask_gf, (685, 396), (25, 14), 0, 0, 360, 255, -1)
    
    # Cat interior mouth opening in scene_main.jpg: (center ~ 412, 554)
    mask_cat = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(mask_cat, (412, 554), (14, 13), 0, 0, 360, 255, -1)
    
    # Combined inpaint mask for interior openings ONLY
    inpaint_mask = cv2.bitwise_or(mask_sinchan, cv2.bitwise_or(mask_gf, mask_cat))
    
    # ----------------------------------------------------
    # 2. INPAINT INTERIOR WITH SURROUNDING SKIN/FUR GRADIENTS
    # ----------------------------------------------------
    # Using Telea inpainting with tight 4px radius to preserve surrounding shading & wrinkles
    rest_scene = cv2.inpaint(scene, inpaint_mask, inpaintRadius=4, flags=cv2.INPAINT_TELEA)
    
    # ----------------------------------------------------
    # 3. RECONSTRUCT NATURAL CLOSED RESTING LINE ART
    # ----------------------------------------------------
    # Sinchan: subtle curved closed smile line matching Crayon Shinchan 2D art
    cv2.ellipse(rest_scene, (278, 568), (11, 7), 0, 20, 160, (28, 20, 20), 2, cv2.LINE_AA)
    
    # Grandpa: gentle wrinkled resting smile matching original line color & chin crease
    cv2.ellipse(rest_scene, (685, 390), (32, 11), 0, 20, 160, (35, 22, 18), 2, cv2.LINE_AA)
    # Natural elderly chin crease below mouth
    cv2.ellipse(rest_scene, (685, 412), (15, 6), 0, 30, 150, (45, 30, 25), 2, cv2.LINE_AA)
    
    # Cat: authentic Japanese anime 'w' muzzle resting lines
    cv2.ellipse(rest_scene, (405, 545), (7, 6), 0, 0, 180, (30, 20, 18), 2, cv2.LINE_AA)
    cv2.ellipse(rest_scene, (419, 545), (7, 6), 0, 0, 180, (30, 20, 18), 2, cv2.LINE_AA)
    cv2.line(rest_scene, (412, 538), (412, 545), (30, 20, 18), 2, cv2.LINE_AA)
    
    # Save output
    cv2.imwrite(output_scene, rest_scene)
    print(f"SUCCESS: Saved natural neutral base scene to {output_scene}")
    return rest_scene

if __name__ == "__main__":
    create_scene_base_rest()
