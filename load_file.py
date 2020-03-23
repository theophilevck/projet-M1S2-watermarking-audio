import matplotlib.pyplot as plt
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
    folder="Audio_files/Spectrology/" #/Spectrology/
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
    
    plt.plot(Time, signal1)
    
    plt.show()

def FFTsignal (nomfichier: str):

    spf=load( nomfichier )
    fs = spf.getframerate()
    # Extract Raw Audio from Wav File
    signal1 = spf.readframes(-1)
    signal1 = np.fromstring(signal1, "Int16")
    


    Time = np.linspace(0, len(signal1) / fs, num=len(signal1))
    
    fft = np.fft.fft(signal1)
    


    T = Time[1] - Time[0]  # sampling interval 
    N = signal1.size

    # 1/T = frequency
    f = np.linspace(0, 1 / T, N)
    
    plt.figure(figsize = (10, 5))
    plt.title( nomfichier+' FFT' )
    plt.ylabel("Amplitude")
    plt.xlabel("Frequency [Hz]")
    plt.plot(np.abs(fft)[:N // 2] * 1 / N,linewidth=0.5)
    #plt.bar(f[:N // 2], np.abs(fft)[:N // 2] * 1 / N, width=1.5)  # 1 / N is a normalization factor// trop long

    

    plt.show() 


    
#freqsignal("sample-music-clean")
#freqsignal("Mix2")
#loadcompare("sample-music-clean","Mix2")
FFTsignal("Mix2")

