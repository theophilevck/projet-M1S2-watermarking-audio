import wave
import math
import binascii
import winsound

nomFichier = 'son.wav'
monson = wave.open(nomFichier,'w') # écriture d'un fichier son.wav

nbCanal = 2    # stéreo
nbOctet = 1    # taille d'un échantillon : 1 octet = 8 bits
freqech = 44100   # fréquence d'échantillonnage

freqG = float(input('Fréquence du son du canal de gauche (Hz) ? '))
freqD = float(input('Fréquence du son du canal de droite (Hz) ? '))
niveauG = float(input('Niveau du son du canal de gauche (0 à 1) ? '))
niveauD = float(input('Niveau du son du canal de droite (0 à 1) ? '))
duree = float(input('Durée (en secondes) ? '))

nbEchantillon = int(duree*freqech)
print("Nombre d'échantillons :",nbEchantillon)

parametres = (nbCanal,nbOctet,freqech,nbEchantillon,'NONE','not compressed')# tuple
monson.setparams(parametres)    # création de l'en-tête (44 octets)

# niveau max dans l'onde positive : +1 -> 255 (0xFF)
# niveau max dans l'onde négative : -1 ->   0 (0x00)
# niveau sonore nul :                0 -> 127.5 (0x80 en valeur arrondi)

amplitudeG = 127.5*niveauG
amplitudeD = 127.5*niveauD

for i in range(0,nbEchantillon):
    # canal gauche
    # 127.5 + 0.5 pour arrondir à l'entier le plus proche
    valG = wave.struct.pack('B',int(128.0 + amplitudeG*math.sin(2.0*math.pi*freqG*i/freqech)))
    # canal droit
    valD = wave.struct.pack('B',int(128.0 + amplitudeD*math.sin(2.0*math.pi*freqD*i/freqech)))
    monson.writeframes(valG + valD) # écriture frame

monson.close()

Fichier = open(nomFichier,'rb')
data = Fichier.read()
tailleFichier = len(data)
print('\nTaille du fichier',nomFichier, ':', tailleFichier,'octets')
print("Lecture du contenu de l'en-tête (44 octets) :")
print(binascii.hexlify(data[0:44]))
print("Nombre d'octets de données :",tailleFichier - 44)
Fichier.close()

lecture=input("Voulez-vous écouter le son ? -yes/no-  ")
if lecture=="yes":
    winsound.PlaySound('son.wav',winsound.SND_FILENAME)