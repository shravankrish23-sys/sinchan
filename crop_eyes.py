from PIL import Image

img = Image.open("boy.png").convert("RGBA")
w, h = img.size

# Let's crop tight around both eyes (x: 350 to 650, y: 200 to 360)
eyes_crop = img.crop((350, 200, 650, 360))
eyes_crop.save("eyes_crop.png")
print(f"Saved eyes_crop.png! Image size: {w}x{h}")
