import wave
import binascii

def lsb_apply(file: str, watermark: str):
    """
    Cache un watermark dans un fichier audio par methode LSB
    :param file: Le nom du fichier a  watermarke ( Ne pas mettre l'extension)
    :param watermark: Le Watermark a appliquer (String)
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_watermarked_lsb.wav', 'w')

    sound_new.setparams(sound.getparams())

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
    for i in range(0, sound.getnframes()):

        bit = 1 if watermark_bin[water_cursor] == "1" else 0

        # Si nous sommes a la fin de la chaine, on repete
        water_cursor = (water_cursor + 1) % len(watermark_bin)

        byte_4 = sound.readframes(1)
        # On met le dernier bit du sample a notre valeur du watermark...
        byte_new = bytes([byte_4[0], byte_4[1], byte_4[2], byte_4[3] - byte_4[3] % 2 + bit])

        sound_new.writeframes(byte_new)  # écriture frame


def lsb_read(file: str, stop_on_end: bool = True):
    """
    Lit le watermark cache dans un fichier par lsb
    :param file: Nom du fichier a decoder (Sans extension)
    :param stop_on_end: On arrete quand on decouvre un caractere de fin de ligne, si le fichier est corrompu ou modifie
    il vaut mieux le mettre a "False" et en lire l'ensemble des repetitions
    """
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio

    sound.setpos(0)
    water_cursor = 0
    bin_str = ''
    for i in range(0, sound.getnframes()):
        byte_4 = sound.readframes(1)

        # On ajoute le LSB du sample a notre chaine
        bin_str += str(byte_4[3] % 2)

        # Si nous decouvrons un caractere de fin de ligne, on coupe (ATTENTION, POSSIBLES ERREURS DE LECTURES ICI)
        if bin_str[-8:] == '00000000' and stop_on_end:
            break

    # Bin to STRING:
    byte_list = []
    for i in range(0, len(bin_str)//8):
        byte_list.append(0)
        for j in range(0, 8):
            # Simple transformation d'un octet binaire en octet int
            if bin_str[i*8 + j] == '1':
                byte_list[-1] += 2**(7-j)

    # Recreation d'un byte a partir des octets reformes
    watermark = bytes(byte_list).decode("utf-8")

    print("Watermark is: " + watermark)
    return watermark


lsb_apply('Audio_files/wilhelm', 'Du vol Monsieur')

lsb_read('Audio_files/wilhelm_watermarked_lsb', True)

