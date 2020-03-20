import matplotlib.pyplot as plt
import numpy as np
import wave
import sys

def load( nomfichier ):
    folder="Audio_files/"
    extention=".wav"
    path=folder+nomfichier+extention
    spf = wave.open(path, "r")

    # Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, "Int16")

        

    plt.figure(1)
    plt.title(nomfichier)
    plt.plot(signal)
    plt.show()

load("FlowingWater")