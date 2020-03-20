import matplotlib.pyplot as plt
import numpy as np
import wave
import sys

def load( nomfichier: str, nomfichierwatermark: str ):
    folder="Audio_files/"
    extention=".wav"
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
                           right = 0.9, top = 0.9, wspace = 0, hspace = 1)
    axes = figure.add_subplot(2, 1, 1)
    axes.set_xlabel('Time (s)')
    axes.set_ylabel('Frequence(Hz)')
    axes.set_title('titre du graphe 1')
    plt.plot(Time, signal1)
    
    axes = figure.add_subplot(2, 1, 2)
    axes.set_xlabel('Time (s)')
    axes.set_ylabel(' Frequence(Hz)')
    axes.set_title('titre du graphe 2')
    plt.plot(Time, signal2)

    plt.show()

    


    
    

load("wilhelm","wilhelm_watermarked_lsb")