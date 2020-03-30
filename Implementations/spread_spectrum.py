import wave
import matplotlib.pyplot as plt
import numpy as np
import random

def correlation(x, y):
    """
    Calcule la correlation entre x et y
    """
    sumx = 0
    sumy = 0
    sumx_square = 0
    sumy_square = 0
    sum_product = 0
    nvalues = min(len(x), len(y))
    for i in range(0, nvalues):
        sumx += x[i]
        sumy += y[i]
        sumx_square += x[i]**2
        sumy_square += y[i]**2
        sum_product += x[i] * y[i]

    return nvalues * sum_product - (sumx * sumy) / np.sqrt((nvalues * sumx_square - sumx**2) * (nvalues * sumy_square - sumy**2))


def dss_apply(file: str, watermark: str, skey: int, alpha: float = 1):
    """
    Cache un watermark dans un fichier audio par methode de Direct Spread Spectrum
    :param file: Le nom du fichier a  watermarke ( Ne pas mettre l'extension)
    :param watermark: Le Watermark a appliquer (String)
    :param alpha: amplitude des pseudobruits
    :param skey: cle de generation des bruits
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_watermarked_dss.wav', 'w')

    sound_new.setparams(sound.getparams())
    sample_size = sound.getsampwidth()
    channel_count = sound.getnchannels()

    watermark_bin = ''
    for i in bytearray(watermark, encoding='utf-8'):
        for j in range(0, 8):
            # Nous faisons un & binaire entre le MSB et "128" pour savoir si nous écrivons un 1 ou 0
            # (Decalage de j pour s'occuper de chaque bit de l'octet)
            watermark_bin += '1' if ((i << j) & 128) > 0 else '0'

    print("Binary Watermark: " + watermark_bin)

    sound.setpos(0)
    bloc_size = sound.getnframes() // len(watermark_bin)
    random.seed(skey)

    for ii in range(0, len(watermark_bin)):
        bit = 1 if watermark_bin[ii] == "1" else 0

        pseudonoise = random.getrandbits(bloc_size)

        for ij in range(0, bloc_size):
            byte_4 = sound.readframes(1)
            byte_new = bytearray(b'')

            adding_int = int(alpha * (2 * (pseudonoise % 2) - 1) * (bit - 0.5) * (-2))  # Normalization

            # Calculate new byte following, actual sound, pseudo noise and alpha
            for k in range(0, channel_count):
                byte_int = int.from_bytes(byte_4[sample_size * k:sample_size * k + 2], "little")

                byte_int += adding_int
                if byte_int < 0:
                    byte_int = 0

                if byte_int >= (1 << 8*sample_size):
                    for j in range(0, sample_size):
                        byte_new += bytes([255])
                    continue

                # Else
                byte_new += byte_int.to_bytes(sample_size, "little")

            sound_new.writeframes(bytes(byte_new))
            pseudonoise /= 2

    # On ajoute les derniers samples
    sound_new.writeframes(sound.readframes(sound.getnframes() - bloc_size * len(watermark_bin)))


def dss_read(file: str, skey: int, size_watermark: int):
    """
    Lit le watermark cache dans un fichier par Direct Spread Spectrum
    :param file: Nom du fichier a decoder (Sans extension)
    :param skey: cle de generation des bruits
    :param size_watermark: taille du watermark a rechercher
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio

    sample_size = sound.getsampwidth()
    channel_count = sound.getnchannels()

    sound.setpos(0)
    bloc_size = sound.getnframes() // size_watermark
    random.seed(skey)

    watermark_bin = ''

    for ii in range(0, size_watermark):
        pseudonoise = random.getrandbits(bloc_size)

        # Recup Big sample
        pn = []
        cw = []
        for i in range(0, bloc_size):
            # Lire les samples en int
            cw += [int.from_bytes(sound.readframes(1)[:sample_size], "little")]
            pn += [2 * (pseudonoise % 2) - 1]
            pseudonoise /= 2

        watermark_bin += '1' if correlation(cw, pn) < 0 else '0'

    return watermark_bin


dss_apply('../Audio_files/wilhelm', 'Bonjour', 42, 10000)
print('Binary Wat Found: ' + dss_read('../Audio_files/wilhelm_watermarked_dss', 42, 7*8))