import wave
import binascii

def lsb_apply(file, watermark):
    sound = wave.open(file + '.wav', 'r')  # lecture d'un fichier audio
    sound_new = wave.open(file + '_watermarked_lsb.wav', 'w')

    sound_new.setparams(sound.getparams())

    watermark_bin = ''.join(format(i, 'b') for i in bytearray(watermark, encoding='utf-8'))

    print("Binary Watermark: " + watermark_bin)

    sound.setpos(0)
    water_cursor = 0
    for i in range(0, sound.getnframes()):

        bit = 1 if watermark_bin[water_cursor] == "1" else 0

        water_cursor = (water_cursor + 1) % len(watermark_bin)

        byte_4 = sound.readframes(1)
        byte_new = bytes([byte_4[0], byte_4[1], byte_4[2], byte_4[3] - byte_4[3] % 2 + bit])  # On met le dernier bit du sample a notre valeur...

        sound_new.writeframes(byte_new)  # écriture frame

lsb_apply('Audio_files/wilhelm', 'Du vol Monsieur')

