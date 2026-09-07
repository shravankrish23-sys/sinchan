from PIL import Image

img = Image.open("boy.png")
w, h = img.size
print(f"Image size: {w}x{h}")

# Let's crop the head region
head_crop = img.crop((int(w * 0.25), int(h * 0.05), int(w * 0.75), int(h * 0.45)))
head_crop.save("head_preview.png")
print("Saved head_preview.png")
