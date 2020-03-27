import wave
import matplotlib.pyplot as plt
import numpy as np


def echo_apply(file: str, watermark: str, alpha: float = 0.1, delay_0: int = 5, delay_1: int = 10, segment_length: int = 100):
    """
    Cache un watermark dans un fichier audio par methode d'Echo Hiding
    :param file: Le nom du fichier a  watermarke ( Ne pas mettre l'extension)
    :param watermark: Le Watermark a appliquer (String)
    :param alpha: amplitude des echos
    :param delay_0: Delai de decalage pour les bits 0
    :param delay_1: Delai de decalage pour les bits 1
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_watermarked_echo.wav', 'w')

    sound_new.setparams(sound.getparams())
    sample_size = sound.getsampwidth()
    channel_count = sound.getnchannels()

    watermark_bin = ''
    for i in bytearray(watermark, encoding='utf-8'):
        for j in range(0, 8):
            # Nous faisons un & binaire entre le MSB et "128" pour savoir si nous écrivons un 1 ou 0
            # (Decalage de j pour s'occuper de chaque bit de l'octet)
            watermark_bin += '1' if ((i << j) & 128) > 0 else '0'
    # Nous mettons le caractere de fin de chaine a la fin du watermark pour en faciliter la lecture apres coup '\00'
    watermark_bin += '00000000'

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

        for k in range(0, segment_length - 1):  # On allonge le watermark pour obtenir le mixer correct (cf doc)
            watermark_segmented += watermark_bin[i]
            if k < segment_length//4 and bit != bit_prev:
                amp_smoothing.append(0.5 + (bit-0.5) * np.cos((segment_length//4 - k) * np.pi / (2 * segment_length//4)))
            elif k > 3 * (segment_length//4) and bit != bit_next:
                amp_smoothing.append(0.5 + (bit-0.5) * np.cos((k - 3 * (segment_length//4))  * np.pi / (2 * segment_length//4)))
            else:
                amp_smoothing.append(bit)

    print("Binary Watermark: " + watermark_bin)
    # print("Segmented Watermark: " + watermark_segmented)

    sound.setpos(0)
    water_cursor = 0
    signal_delayed = [bytearray(sample_size * channel_count) for i in range(0, max(delay_0,
                                                         delay_1))]  # Utilise pour les delais 1 et 0 ( Pour 1 on fera signal_delayed[-delai_1]...)
    for i in range(0, sound.getnframes()):
        bit = 1 if watermark_segmented[water_cursor] == "1" else 0

        byte_4 = sound.readframes(1)

        val = signal_delayed.pop()  # Ajoute les valeurs d'echo
        byte_new = bytearray(sample_size * channel_count)
        for k in range(0, channel_count):
            retenue = 0
            for j in range(0, sample_size):
                byte_new[j + sample_size * k] = (byte_4[j + sample_size * k] + val[j + sample_size * k] + retenue) % 256
                retenue = (byte_4[j + sample_size * k] + val[j + sample_size * k]) // 256
            if retenue >= 1:  # Si on plafonne, on plafonne
                for j in range(0, sample_size):
                    byte_new[j + sample_size * k] = 255

        sound_new.writeframes(byte_new)

        # Calcul de l'amplification de l'echo
        amp_int1 = [int(np.frombuffer(byte_4[j * sample_size : (j * sample_size) + 2], np.int16)[0] * alpha * amp_smoothing[water_cursor]) for j in range(0, channel_count)]
        amp_int0 = [int(np.frombuffer(byte_4[j * sample_size : (j * sample_size) + 2], np.int16)[0] * alpha * np.abs(1 - amp_smoothing[water_cursor])) for j in range(0, channel_count)]
        amp_byte1 = bytearray(sample_size * channel_count)
        amp_byte0 = bytearray(sample_size * channel_count)
        for k in range(0, channel_count):
            for j in range(0, sample_size):
                amp_byte1[j + sample_size * k] = amp_int1[k] % 256
                amp_int1[k] = amp_int1[k] // 256
                amp_byte0[j + sample_size * k] = amp_int0[k] % 256
                amp_int0[k] = amp_int1[k] // 256

        # Application de l'echo dans la file d'attente
        signal_delayed.insert(0, bytearray(sample_size * channel_count))  # Data vide

        # Si nous sommes a la fin de la chaine, on repete
        water_cursor = (water_cursor + 1) % len(watermark_segmented)

        # Add Mixage Bit 1
        for k in range(0, channel_count):
            retenue = 0
            for j in range(0, sample_size):
                temp_retenue = (signal_delayed[-delay_1][j + sample_size * k] + amp_byte1[j + sample_size * k]) // 256 # D'abord la retenue car on change signal_delayed[...] apres!
                signal_delayed[-delay_1][j + sample_size * k] = (signal_delayed[-delay_1][j + sample_size * k] + amp_byte1[j + sample_size * k] + retenue) % 256
                retenue = temp_retenue
            if retenue >= 1:  # Si on plafonne, on plafonne
                for j in range(0, sample_size):
                    signal_delayed[-delay_1][j + sample_size * k] = 255

        # Add Mixage bit 0
        for k in range(0, channel_count):
            retenue = 0
            for j in range(0, sample_size):
                temp_retenue = (signal_delayed[-delay_0][j + sample_size * k] + amp_byte0[j + sample_size * k]) // 256 # D'abord la retenue car on change signal_delayed[...] apres!
                signal_delayed[-delay_0][j + sample_size * k] = (signal_delayed[-delay_0][j + sample_size * k] + amp_byte0[j + sample_size * k] + retenue) % 256
                retenue = temp_retenue
            if retenue >= 1:  # Si on plafonne, on plafonne
                for j in range(0, sample_size):
                    signal_delayed[-delay_0][j + sample_size * k] = 255
    return watermark_bin

def test(file: str, delay_0: int = 5, delay_1: int = 10, segment_length: int = 100):
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio

    signalD = bytearray(b'')
    for i in range(0, sound.getnframes()):
        signalD += sound.readframes(1)[:2]

    signal1 = np.frombuffer(bytes(signalD), np.int16)

    decoded = ''
    for i in range(0, sound.getnframes()//segment_length):
        fft = np.fft.fft(signal1[segment_length*i:segment_length*(i+1)])
        cepstrum = np.fft.ifft(np.log(np.abs(fft)))
        decoded += '0' if (cepstrum[delay_0 ] > cepstrum[delay_1 ]) else '1'

        """plt.figure(figsize=(10, 5))
        plt.ylabel("Amplitude")
        plt.xlabel("Frequency [Hz]")
        plt.plot(cepstrum[10:min(delay_1+delay_0,segment_length)], linewidth=0.5,)
        plt.show()"""

    print('Binary Watermark: ' + decoded)
    return decoded


def higher_sampwidth(file: str, new_width: int):
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + 'bigger_samps.wav', 'w')

    sound_new.setparams(sound.getparams())
    sound_new.setsampwidth(new_width)

    for i in range(0, sound.getnframes()):

        byte_4 = sound.readframes(1)

        byte_new = bytearray()
        for k in range(0, sound.getnchannels()):
            temp = 0
            for j in range(0, sound.getsampwidth()):
                byte_new += bytearray([byte_4[j + sound.getsampwidth() * k]])
                temp += 1
            byte_new += bytes(max(0, new_width - temp))

        sound_new.writeframes(byte_new)

a= echo_apply('../Audio_files/wilhelm', 'Echo hiding cest bien', 0.5, 64, 128, 512)

b= test('../Audio_files/wilhelm_watermarked_echo', 64, 128, 512)

error = 0
for i in range(0, len(b)):
    if b[i] != a[i]:
        error += 1
error /= len(b)
print('Error rate: ', error)
