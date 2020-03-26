import matplotlib.pyplot as plt
from scipy import signal
import pylab
import numpy as np
import wave
import sys


    
def load( nomfichier: str ): #fonction qui permet le chargement du .wav
    folder="Audio_files/" 
    extention=".wav"
    path1=folder+nomfichier+extention

    spf1 = wave.open(path1, "r")
    return spf1

def freqsignal (nomfichier: str): 

    sound=load( nomfichier )#on charge le fichier
    rate=sound.getframerate() #on recupere la frequence d echantillonage du fichier

    signalD = bytearray(b'')
    for i in range(0, sound.getnframes()):
        signalD += sound.readframes(1)[:2]

    signal1 = np.fromstring(bytes(signalD), "Int16")

    Time = np.linspace(0, len(signal1) / rate, num=len(signal1)) #on calcule la longeur du fichier pour l axe 

    plt.figure(figsize = (10, 5))   #creation et taille de la figure
    plt.title( nomfichier+' frequence' ) #titre
    plt.xlabel('Time (s)')
    plt.ylabel('Frequence(Hz)')
    
    plt.plot(Time, signal1,linewidth=0.5) #on trace la representation frequentielle
    
    

def FFTsignal (nomfichier: str):

    sound=load( nomfichier )
    rate=sound.getframerate() 

    signalD = bytearray(b'')
    for i in range(0, sound.getnframes()):
        signalD += sound.readframes(1)[:2]

    signal1 = np.fromstring(bytes(signalD), "Int16")

    FFT = np.fft.fft(signal1)       #on effectue une fast fourier transform sur le signale
    FFT =np.absolute(FFT)           #on prend la valleur absolue de la FFT 
    FFT=FFT/FFT.max()               

    n = FFT.size
    freq = np.zeros(n)
    
    for k in range(n):              #on calcule chaque frequence
        freq[k] = 1.0/n*rate*k
    
    plt.figure(figsize = (10, 5))       #creation et taille de la figure
    plt.vlines(freq,[0],FFT,'r')        #on trace les frequence avec comme dubut 0 et comme fin la FFT
    plt.xlabel('f (Hz)')
    plt.ylabel('A')
    plt.axis([0,0.5*rate,0,1])          #on met a l echelle 
    




def graph_spectrogram(nomfichier: str):
    sound=load( nomfichier ) 

    signalD = bytearray(b'')
    for i in range(0, sound.getnframes()):
        signalD += sound.readframes(1)[:2]

    frames = sound.readframes(-1)
    sound_info = np.fromstring(bytes(signalD), "Int16")
    frame_rate = sound.getframerate()             #identique a la premeire fonction

   
    pylab.figure(num=None, figsize=(10, 5))     #creation et taille de la figure
    pylab.title('spectrogram of %r' % sound)      
    pylab.specgram(sound_info, Fs=frame_rate)   #on appele la fonction specgram qui trace le spertrograme
    
			

def analyse(nomfichier: str):

    freqsignal(nomfichier)
    FFTsignal(nomfichier)
    graph_spectrogram(nomfichier)
    plt.show()                      #on affiche les different graphique qui on etait cree dans les fonction appeler


    
analyse("Spectrology\Mix2")

