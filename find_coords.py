from PIL import Image, ImageDraw, ImageFont

img = Image.open("boy.png")
draw = ImageDraw.Draw(img)

# Draw a grid across the face region (y from 100 to 600, x from 300 to 700)
for y in range(100, 600, 50):
    draw.line([(300, y), (724, y)], fill="red", width=1)
    draw.text((310, y+2), f"Y={y}", fill="red")

for x in range(300, 750, 50):
    draw.line([(x, 100), (x, 600)], fill="blue", width=1)
    draw.text((x+2, 110), f"X={x}", fill="blue")

img.crop((300, 100, 724, 600)).save("face_grid.png")
print("Saved face_grid.png with coordinate grid")
