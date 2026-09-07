from PIL import Image

img = Image.open("boy.png").convert("RGBA")
# Let's crop tight around mouth area: x: 440 to 580, y: 340 to 420
mouth_crop = img.crop((440, 340, 580, 420))
mouth_crop.save("mouth_original.png")
print("Saved mouth_original.png")
