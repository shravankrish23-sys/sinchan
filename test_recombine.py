from PIL import Image

legs = Image.open("layer_legs.png")
torso = Image.open("layer_torso.png")
head = Image.open("layer_head.png")

comp = Image.new("RGBA", legs.size, (0, 0, 0, 0))
comp.paste(legs, (0, 0), legs)
comp.paste(torso, (0, 0), torso)
comp.paste(head, (0, 0), head)

comp.save("layers_recombined_test.png")
print("Saved layers_recombined_test.png")
