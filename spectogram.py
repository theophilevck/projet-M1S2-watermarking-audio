import matplotlib.pyplot as plt
from scipy.io import wavfile

# lecture du fichier avec les différentes données de fréquences, ...
samplingFrequency, signalData = wavfile.read('Audio_files\Spectrology\Mix2.wav')

# Affiche le signal ==> Spectogramme
plt.specgram(signalData[:,0],Fs=samplingFrequency)
#plot.specgram(signalData[:,1],Fs=samplingFrequency)
plt.xlabel('Time')
plt.ylabel('Frequency')

plt.show()