import wave
import binascii

NomFichier = input('Entrer le nom du fichier : ')
Monson = wave.open(NomFichier,'r')	# lecture d'un fichier audio

print("\nNombre de canaux :",Monson.getnchannels())
print("Taille d'un échantillon (en octets):",Monson.getsampwidth())
print("Fréquence d'échantillonnage (en Hz):",Monson.getframerate())
print("Nombre d'échantillons :",Monson.getnframes())
print("Type de compression :",Monson.getcompname())

TailleData = Monson.getnchannels()*Monson.getsampwidth()*Monson.getnframes()

print("Taille du fichier (en octets) :",TailleData + 44)
print("Nombre d'octets de données :",TailleData)

print("\nAffichage d'une plage de données (dans l'intervalle 0 -",Monson.getnframes()-1,")")

echDebut = int(input('N° échantillon (début) : '))
echFin = int(input('N° échantillon (fin) : '))

print("\nN° échantillon	Contenu")

Monson.setpos(echDebut)
plage = echFin - echDebut + 1
for i in range(0,plage):
    print(Monson.tell(),'\t\t',binascii.hexlify(Monson.readframes(1)))

Monson.close()