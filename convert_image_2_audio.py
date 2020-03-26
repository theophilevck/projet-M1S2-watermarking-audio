from PIL import Image, ImageOps
import wave, math, array, argparse, sys, timeit

minfreq = 200
maxfreq = 20000
wavrate = 44100
pxs     = 30

#im = Image.open("Image_files\eye.png")
#im.rotate(45).show()

extension=".bmp"
img = Image.open("Image_files\eye"+extension).convert('L')
img.show()

a=input("Voulez-vous faire une rotation de l'image ? yes-no  ")
if a==("yes"):
    img=img.rotate(90)
    img.show()

b=input("Voulez-vous mettre l'image en nuances de noir et blanc ? yes-no  ")
if b==("yes"):
    img = ImageOps.invert(img)
    img.show()


extension=".wav"
output = wave.open("Image_files\eye"+extension, 'w')

intervalfreq = maxfreq - minfreq
interval = intervalfreq / img.size[1]

fpx = wavrate // pxs     # Hz // px
data = array.array('h')  # array de int


