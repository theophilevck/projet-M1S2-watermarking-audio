import wave
import numpy as np


def echo_apply(file: str, watermark: str, alpha: float = 0.1, delay_0: int = 1, delay_1: int = 2):
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

    print("Binary Watermark: " + watermark_bin)

    sound.setpos(0)
    water_cursor = 0
    signal_delayed = [bytearray(sample_size * channel_count) for i in range(0, max(delay_0,
                                                         delay_1))]  # Utilise pour les delais 1 et 0 ( Pour 1 on fera signal_delayed[-delai_1]...)
    for i in range(0, sound.getnframes()):
        if i == sound.getnframes() // 2 and sound.getnchannels() == 2:
            water_cursor = 0  # Selon le wav, la seconde moitie des frames correspondent au channel 2, on reboot
        bit = 1 if watermark_bin[water_cursor] == "1" else 0

        byte_4 = sound.readframes(1)

        val = signal_delayed.pop()  # Ajoute les valeurs d'echo
        byte_new = bytearray(sample_size * channel_count)
        for k in range(0, channel_count):
            retenue = 0
            for j in range(0, sample_size):
                byte_new[j + sample_size * k] = (byte_4[j + sample_size * k] + val[j + sample_size * k] + retenue) % 256
                retenue = (byte_4[j + sample_size * k] + val[j + sample_size * k]) // 256

        sound_new.writeframes(byte_new)

        # Nous allons eviter de stocker des donnees dans des echos qui n'existent pas si le sample est vide...
        # Nous n'augmentons donc pas le curseur pour eviter de perdre des donnees
        bypass = True
        for i in byte_4:
            if i != 0:
                bypass = False
                break
        if bypass:
            signal_delayed.insert(0, bytearray(sample_size * channel_count))  # Rien... Octets vides
            continue

        # Si nous sommes a la fin de la chaine, on repete
        water_cursor = (water_cursor + 1) % len(watermark_bin)

        # Calcul de l'amplification de l'echo
        amp_int = [int(np.fromstring(byte_4[j * sample_size : (j * sample_size) + 2], "Int16")[0] * alpha) for j in range(0, channel_count)]
        amp_byte = bytearray(sample_size * channel_count)
        for k in range(0, channel_count):
            for j in range(0, sample_size):
                amp_byte[j + sample_size * k] = amp_int[k] % 256
                amp_int[k] = amp_int[k] // 256

        # Application de l'echo dans la file d'attente
        signal_delayed.insert(0, bytearray(sample_size * channel_count))  # Data vide

        delay_active = 0

        if bit == 1:
            delay_active = delay_1
        else:  # bit == 0
            delay_active = delay_0

        for k in range(0, channel_count):
            retenue = 0
            for j in range(0, sample_size):
                signal_delayed[-delay_1][j + sample_size * k] = (signal_delayed[-delay_active][j + sample_size * k] + amp_byte[j + sample_size * k] + retenue) % 256
                retenue = (signal_delayed[-delay_1][j + sample_size * k] + amp_byte[j + sample_size * k]) // 256


def test(file: str):
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_tested.wav', 'w')

    sound_new.setparams(sound.getparams())

    for i in range(0, sound.getnframes()):
        byte_new = bytearray(sound.readframes(1))
        byte_new[2] = 0
        byte_new[3] = 0
        sound_new.writeframes(byte_new)

echo_apply('Audio_files/wilhelm', 'Si on peut lire ca alors echo hiding cest bien', 0.1, 25, 30)
