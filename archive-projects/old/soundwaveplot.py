import matplotlib.pyplot as plt
import numpy as np
import wave

soundwave = wave.open('oo2.wav')
signal = soundwave.readframes(-1)
signal = np.fromstring(signal, 'Int16')

#If Stereo
if soundwave.getnchannels() == 2:
    print 'Just mono files'



# print signal

# thefile = open('textdata.txt', 'w')
# for x in signal:
#   print >> thefile, x

plt.plot(signal)
plt.show()