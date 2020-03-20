from PIL import Image
im = Image.open("Image_files\eye.png")
im.rotate(45).show()