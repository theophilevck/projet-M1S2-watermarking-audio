import wave
import matplotlib.pyplot as plt
import numpy as np
import time


def echo_single_apply(file: str, watermark: str, alpha: float = 0.1, delay_0: int = 5, delay_1: int = 10, segment_length: int = 100, bipolar: bool = False):
    """
    Cache un watermark dans un fichier audio par methode d'Echo Hiding SINGLE OU BIPOLAIRE
    :param file: Le nom du fichier a  watermarke
    :param watermark: Le Watermark a appliquer (String)
    :param alpha: amplitude des echos
    :param delay_0: Delai de decalage pour les bits 0
    :param delay_1: Delai de decalage pour les bits 1
    :param segment_length: Taille des segments dans lesquels nous cachons UN bit
    :param bipolar: Devons-nous utiliser la methode bipolaire?
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_watermarked_echo.wav', 'w')

    sound_new.setparams(sound.getparams())
    sample_size = sound.getsampwidth()
    channel_count = sound.getnchannels()
    frames_number = sound.getnframes()

    watermark_bin = ''
    for i in bytearray(watermark, encoding='utf-8'):
        for j in range(0, 8):
            # Nous faisons un & binaire entre le MSB et "128" pour savoir si nous écrivons un 1 ou 0
            # (Decalage de j pour s'occuper de chaque bit de l'octet)
            watermark_bin += '1' if ((i << j) & 128) > 0 else '0'

    watermark_segmented = ''
    amp_smoothing = []  # Mixer effectif
    for i in range(0, len(watermark_bin)):
        bit = 1 if watermark_bin[i] == '1' else 0
        if i == 0:
            bit_prev = 1 if i == '1' else 0
            bit_next = 1 if watermark_bin[i+1] == '1' else 0
        elif i == len(watermark_bin)-1:
            bit_prev = 1 if watermark_bin[i-1] == '1' else 0
            bit_next = 1 if i == '1' else 0
        else:
            bit_prev = 1 if watermark_bin[i-1] == '1' else 0
            bit_next = 1 if watermark_bin[i+1] == '1' else 0

        for k in range(0, segment_length):  # On allonge le watermark pour obtenir le mixer correct (cf doc)
            watermark_segmented += watermark_bin[i]
            if k < segment_length//4 and bit != bit_prev:
                amp_smoothing.append(0.5 + (bit-0.5) * np.cos((segment_length//4 - k) * np.pi / (2 * segment_length//4)))
            elif k > 3 * (segment_length//4) and bit != bit_next:
                amp_smoothing.append(0.5 + (bit-0.5) * np.cos((k - 3 * (segment_length//4))  * np.pi / (2 * segment_length//4)))
            else:
                amp_smoothing.append(bit)

            if bipolar:
                # Le principe du Bipolaire est de ne pas seulement ajouter un echo alpha selon le bit demande
                # Mais aussi de retirer l'echo du bit contraire de alpha/2 (On a juste a normaliser notre mixer entre -0.5 et 0.5)
                amp_smoothing[-1] -= 0.5

    print("Binary Watermark: " + watermark_bin)
    # print("Segmented Watermark: " + watermark_segmented)

    sound.setpos(0)
    water_cursor = 0
    signal_delayed = [[0, 0] for z in range(0, max(delay_0, delay_1))]  # Utilise pour les delais 1 et 0 ( Pour 1 on
    # fera signal_delayed[-delai_1]...)
    write_temp = bytearray(b'')
    read_temp = sound.readframes(-1)

    for i in range(0, frames_number):

        bit = 1 if watermark_segmented[water_cursor] == "1" else 0

        byte_4 = read_temp[sample_size * channel_count * i:sample_size * channel_count * (i+1)]
        int_4 = [int.from_bytes(byte_4[j * sample_size:(j+1) * sample_size], "little") for j in range(0, channel_count)]

        val = signal_delayed.pop()  # Ajoute les valeurs d'echo

        for k in range(0, channel_count):
            write_temp += bytearray((min(max(int_4[k] + val[k], 0), (1 << sample_size * 8) - 1)).to_bytes(sample_size, 'little'))

        # Calcul de l'amplification de l'echo
        amp_int1 = [int(int_4[j] * alpha * amp_smoothing[water_cursor]) for j in range(0, channel_count)]
        if not bipolar:
            amp_int0 = [int(int_4[j] * alpha * np.abs(1 - amp_smoothing[water_cursor])) for j in range(0, channel_count)]
        else:  # A normalisation differente, inverse different
            amp_int0 = [int(int_4[j] * alpha * (0 - amp_smoothing[water_cursor])) for j in range(0, channel_count)]

        # Application de l'echo dans la file d'attente
        signal_delayed.insert(0, [0, 0])  # Data vide

        # Si nous sommes a la fin de la chaine, on repete
        water_cursor = (water_cursor + 1) % len(watermark_segmented)

        # Add Mixage Bit 1
        for k in range(0, channel_count):
            signal_delayed[-delay_1][k] = min(max(signal_delayed[-delay_1][k] + amp_int1[k], 0), (1 << sample_size * 8) - 1)

        # Add Mixage bit 0
        for k in range(0, channel_count):
            signal_delayed[-delay_0][k] = min(max(signal_delayed[-delay_0][k] + amp_int0[k], 0), (1 << sample_size * 8) - 1)

    sound_new.writeframes(write_temp)
    return watermark_bin


def echo_backward_forward_apply(file: str, watermark: str, alpha: float = 0.1, delay_0: int = 5, delay_1: int = 10, segment_length: int = 100, bipolar: bool = False):
    """
    Cache un watermark dans un fichier audio par methode d'Echo Hiding BACKWARD FORWARD OU BACKWARD FORWARD BIPOLAIRE
    :param file: Le nom du fichier a  watermarke
    :param watermark: Le Watermark a appliquer (String)
    :param alpha: amplitude des echos
    :param delay_0: Delai de decalage pour les bits 0
    :param delay_1: Delai de decalage pour les bits 1
    :param segment_length: Taille des segments dans lesquels nous cachons UN bit
    :param bipolar: Devons-nous utiliser la methode bipolaire?
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_watermarked_bfecho.wav', 'w')

    sound_new.setparams(sound.getparams())
    sample_size = sound.getsampwidth()
    channel_count = sound.getnchannels()
    frames_number = sound.getnframes()

    sample_max_value = (1 << sample_size * 8) - 1

    watermark_bin = ''
    for i in bytearray(watermark, encoding='utf-8'):
        for j in range(0, 8):
            # Nous faisons un & binaire entre le MSB et "128" pour savoir si nous écrivons un 1 ou 0
            # (Decalage de j pour s'occuper de chaque bit de l'octet)
            watermark_bin += '1' if ((i << j) & 128) > 0 else '0'

    watermark_segmented = ''
    amp_smoothing = []  # Mixer effectif
    for i in range(0, len(watermark_bin)):
        bit = 1 if watermark_bin[i] == '1' else 0
        if i == 0:
            bit_prev = 1 if i == '1' else 0
            bit_next = 1 if watermark_bin[i + 1] == '1' else 0
        elif i == len(watermark_bin) - 1:
            bit_prev = 1 if watermark_bin[i - 1] == '1' else 0
            bit_next = 1 if i == '1' else 0
        else:
            bit_prev = 1 if watermark_bin[i - 1] == '1' else 0
            bit_next = 1 if watermark_bin[i + 1] == '1' else 0

        for k in range(0, segment_length):  # On allonge le watermark pour obtenir le mixer correct (cf doc)
            watermark_segmented += watermark_bin[i]
            if k < segment_length // 4 and bit != bit_prev:
                amp_smoothing.append(
                    0.5 + (bit - 0.5) * np.cos((segment_length // 4 - k) * np.pi / (2 * segment_length // 4)))
            elif k > 3 * (segment_length // 4) and bit != bit_next:
                amp_smoothing.append(
                    0.5 + (bit - 0.5) * np.cos((k - 3 * (segment_length // 4)) * np.pi / (2 * segment_length // 4)))
            else:
                amp_smoothing.append(bit)

            if bipolar:
                # Le principe du Bipolaire est de ne pas seulement ajouter un echo alpha selon le bit demande
                # Mais aussi de retirer l'echo du bit contraire de alpha/2 (On a juste a normaliser notre mixer entre -0.5 et 0.5)
                amp_smoothing[-1] -= 0.5

    print("Binary Watermark: " + watermark_bin)
    # print("Segmented Watermark: " + watermark_segmented)

    sound.setpos(0)
    water_cursor = 0
    # Transformation du signal octal en decimal:
    read_temp = sound.readframes(-1)
    read_decimal = []
    for i in range(0, frames_number):
        byte_4 = read_temp[sample_size * channel_count * i:sample_size * channel_count * (i + 1)]
        read_decimal.append([int.from_bytes(byte_4[j * sample_size:(j + 1) * sample_size], "little") for j in
                 range(0, channel_count)])

    write_temp = bytearray(b'')

    for i in range(0, frames_number):

        bit = 1 if watermark_segmented[water_cursor] == "1" else 0

        int_4 = read_decimal[i]

        # Calcul de l'amplification de l'echo
        amp_int1 = [int(int_4[j] * alpha * amp_smoothing[water_cursor] / 2) for j in range(0, channel_count)]
        if not bipolar:
            amp_int0 = [int(int_4[j] * alpha * np.abs(1-amp_smoothing[water_cursor]) / 2) for j in range(0, channel_count)]
        else:  # A normalisation differente, inverse different
            amp_int0 = [int(int_4[j] * alpha * (0 - amp_smoothing[water_cursor]) / 2) for j in range(0, channel_count)]

        # Si nous sommes a la fin de la chaine, on repete
        water_cursor = (water_cursor + 1) % len(watermark_segmented)

        # Add Mixage Bit 1
        for k in range(0, channel_count):
            if i-delay_1 >= 0:
                read_decimal[i-delay_1][k] = min(max(read_decimal[i-delay_1][k] + amp_int1[k], 0), sample_max_value)
            if i+delay_1 < frames_number:
                read_decimal[i+delay_1][k] = min(max(read_decimal[i+delay_1][k] + amp_int1[k], 0), sample_max_value)

        # Add Mixage bit 0
        for k in range(0, channel_count):
            if i-delay_0 >= 0:
                read_decimal[i-delay_0][k] = min(max(read_decimal[i-delay_0][k] + amp_int0[k], 0), sample_max_value)
            if i+delay_0 < frames_number:
                read_decimal[i+delay_0][k] = min(max(read_decimal[i+delay_0][k] + amp_int0[k], 0), sample_max_value)

    # Decimal Vers octal
    for val in read_decimal:
        for k in range(0, channel_count):
            write_temp += bytearray(val[k].to_bytes(sample_size, 'little'))

    sound_new.writeframes(write_temp)
    return watermark_bin


def echo_decode(file: str, delay_0: int = 5, delay_1: int = 10, segment_length: int = 100):
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sample_size = sound.getsampwidth()
    channel_count = sound.getnchannels()
    frames_number = sound.getnframes()

    signalD = []
    for i in range(0, frames_number):
        signalD.append(int.from_bytes(sound.readframes(1)[:sample_size], 'little'))

    decoded = ''
    for i in range(0, sound.getnframes()//segment_length):
        fft = np.fft.fft(signalD[segment_length*i:segment_length*(i+1)])
        cepstrum = np.fft.ifft(np.log(np.abs(fft)))
        #cepstrum[0] = 0
        decoded += '0' if (cepstrum[delay_0] > cepstrum[delay_1]) else '1'

        """plt.figure(figsize=(10, 5))
        plt.plot(cepstrum[:min(delay_1+delay_0,segment_length)], linewidth=0.5,)
        plt.show()"""

    print('Binary Watermark: ' + decoded)
    return decoded

a = echo_single_apply('../Audio_files/wilhelm', 'Bonjour', 0.1, 128, 256, 1024, False)

b = echo_decode('../Audio_files/wilhelm_watermarked_echo', 128, 256, 1024)

error = 0
for i in range(0, min(len(a), len(b))):
    if b[i] != a[i]:
        error += 1
error /= min(len(a), len(b))
print('Error rate: ', error)
