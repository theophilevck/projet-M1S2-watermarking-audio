import matplotlib.pyplot as plt
from scipy import signal
import pylab
import numpy as np
import wave
import sys


def loadcompare( nomfichier: str, nomfichierwatermark: str ):
    folder="Audio_files/Spectrology/"
    extention=".wav"
    extention2=".mp3"
    path1=folder+nomfichier+extention
    path2=folder+nomfichierwatermark+extention
    

    spf1 = wave.open(path1, "r")
    spf2 = wave.open(path2, "r")
    fs = spf1.getframerate()

    # Extract Raw Audio from Wav File
    signal1 = spf1.readframes(-1)
    signal1 = np.fromstring(signal1, "Int16")

    signal2 = spf2.readframes(-1)
    signal2 = np.fromstring(signal2, "Int16")
        
    Time = np.linspace(0, len(signal1) / fs, num=len(signal1))
    
    figure = plt.figure(figsize = (10, 5))
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,
                           right = 0.9, top = 0.9, wspace = 0, hspace = 0.5)
    axes = figure.add_subplot(2, 1, 1)
    axes.set_xlabel('Time (s)')
    axes.set_ylabel('Frequence(Hz)')
    axes.set_title('without watermark')
    plt.plot(Time, signal1)
    
    axes = figure.add_subplot(2, 1, 2)
    axes.set_xlabel('Time (s)')
    axes.set_ylabel(' Frequence(Hz)')
    axes.set_title('with watermark')
    plt.plot(Time, signal2)

    plt.show()

    
def load( nomfichier: str ):
    folder="Audio_files/" #/Spectrology/
    extention=".wav"
    path1=folder+nomfichier+extention

    spf1 = wave.open(path1, "r")
    return spf1

def freqsignal (nomfichier: str):
    spf=load( nomfichier )
    fs = spf.getframerate()

    # Extract Raw Audio from Wav File
    signal1 = spf.readframes(-1)
    signal1 = np.fromstring(signal1, "Int16")

    Time = np.linspace(0, len(signal1) / fs, num=len(signal1))

    plt.figure(figsize = (10, 5))
    plt.title( nomfichier+' frequence' )
    plt.xlabel('Time (s)')
    plt.ylabel('Frequence(Hz)')
    
    plt.plot(Time, signal1,linewidth=0.5)
    
    

def FFTsignal (nomfichier: str):

    spf=load( nomfichier )
    fs = spf.getframerate()
    # Extract Raw Audio from Wav File
    signal1 = spf.readframes(-1)
    signal1 = np.fromstring(signal1, "Int16")
    rate=spf.getframerate()
    


    FFT = np.fft.fft(signal1)
    FFT =np.absolute(FFT)
    FFT=FFT/FFT.max()

    n = FFT.size
    freq = np.zeros(n)
    
    for k in range(n):
        freq[k] = 1.0/n*rate*k
    
    plt.figure(figsize = (10, 5))
    plt.vlines(freq,[0],FFT,'r')
    plt.xlabel('f (Hz)')
    plt.ylabel('A')
    plt.axis([0,0.5*rate,0,1])
    return




def graph_spectrogram(nomfichier: str):
    spf=load( nomfichier )
    frames = spf.readframes(-1)
    sound_info = pylab.fromstring(frames, 'int16')
    frame_rate = spf.getframerate()

   
    pylab.figure(num=None, figsize=(10, 5))
    
    pylab.title('spectrogram of %r' % spf)
    pylab.specgram(sound_info, Fs=frame_rate)
    
			

def analyse(nomfichier: str):

    freqsignal(nomfichier)
    FFTsignal(nomfichier)
    graph_spectrogram(nomfichier)
    plt.show() 


    
analyse("Spectrology\Mix2")

