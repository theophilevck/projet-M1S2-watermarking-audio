from PIL import Image, ImageOps
import wave, math, array, argparse, sys, timeit

"""
definition des paramètres pour utiliser le programme spectrology.py : ./spectrology -r -i -o -t
"""
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT", help="Name of the image to be convected.")
    parser.add_argument("-r", "--rotate", help="Rotate image 90 degrees for waterfall spectrographs.", action='store_true')
    parser.add_argument("-i", "--invert", help="Invert image colors.", action='store_true')
    parser.add_argument("-o", "--output", help="Name of the output wav file. Default value: out.wav).")
    parser.add_argument("-b", "--bottom", help="Bottom frequency range. Default value: 200.", type=int)
    parser.add_argument("-t", "--top", help="Top frequency range. Default value: 20000.", type=int)
    parser.add_argument("-p", "--pixels", help="Pixels per second. Default value: 30.", type=int)
    parser.add_argument("-s", "--sampling", help="Sampling rate. Default value: 44100.", type=int)
    args = parser.parse_args()

#valeurs par défaut pour les fréquences, rotation, inversion des couleurs et pixels
    minfreq = 200
    maxfreq = 20000
    wavrate = 44100
    pxs     = 30
    output  = "out.wav"
    rotate  = False
    invert  = False

    if args.output:
        output = args.output
    if args.bottom:
        minfreq = args.bottom
    if args.top:
        maxfreq = args.top
    if args.pixels:
        pxs = args.pixels
    if args.sampling:
        wavrate = args.sampling
    if args.rotate:
        rotate = True
    if args.invert:
        invert = True

    print('Input file: %s.' % args.INPUT)
    print('Frequency range: %d - %d.' % (minfreq, maxfreq))
    print('Pixels per second: %d.' % pxs)
    print('Sampling rate: %d.' % wavrate)
    print('Rotate Image: %s.' % ('yes' if rotate else 'no'))

    return (args.INPUT, output, minfreq, maxfreq, pxs, wavrate, rotate, invert)

"""
Conversion image vers .wav ==> spectogram
"""
def convert(inpt, output, minfreq, maxfreq, pxs, wavrate, rotate, invert):
    img = Image.open(inpt).convert('L')

    # rotation de l'image de 90° si demandé
    if rotate:
      img = img.rotate(90)

    # inversion de l'image si demandé
    if invert:
      img = ImageOps.invert(img)

    # on écrit un fichier .wav avec les informations obtenues au dessus (image, rotation, couleurs, pixels, ...)
    output = wave.open(output, 'w')

    #Tuple qui prend en paramètres (nchannels, sampwidth, framerate, nframes, comptype, compname)
    output.setparams((1, 2, wavrate, 0, 'NONE', 'not compressed'))

    # calcul interval de fréquence
    freqrange = maxfreq - minfreq

    #pas entre chaque frequence possible selon la taille de l'image
    interval = freqrange / img.size[1]

    #taux d'onde/pixels
    fpx = wavrate // pxs

    #data=liste de int
    data = array.array('h')

    #calcul du temps de conversion image/spectre audio
    tm = timeit.default_timer()

    # on cherche chaque pixel x,y
    for x in range(img.size[0]):
        row = []
        for y in range(img.size[1]):
            yinv = img.size[1] - y - 1
            # récupére le canal de couleur du pixel (R,V,B)
            amp = img.getpixel((x,y))
            if (amp > 0):
                # génére un signal
                # pour chacun de ces pixel on créé la frequence associée 
                # l'amplitude doit etre déterminée selon la couleur du pixel
                row.append( genwave(yinv * interval + minfreq, amp, fpx, wavrate) )

        for i in range(fpx):
            for j in row:
                try:
                    data[i + x * fpx] += j[i]
                except(IndexError):
                    data.insert(i + x * fpx, j[i])
                except(OverflowError):
                    if j[i] > 0:
                      data[i + x * fpx] = 32767
                    else:
                      data[i + x * fpx] = -32768

        sys.stdout.write("Conversion progress: %d%%   \r" % (float(x) / img.size[0]*100) )
        sys.stdout.flush()

    output.writeframes(data.tostring())
    output.close()

    #calcul du temps de conversion image/spectre audio
    tms = timeit.default_timer()

    print("Conversion progress: 100%")
    print("Success. Completed in %d seconds." % int(tms-tm))

def genwave(frequency, amplitude, samples, samplerate):
    cycles = samples * frequency / samplerate
    a = []
    for i in range(samples):
        x = math.sin(float(cycles) * 2 * math.pi * i / float(samples)) * float(amplitude)
        a.append(int(math.floor(x)))
    return a

if __name__ == '__main__':
    inpt = parser()
    convert(*inpt)