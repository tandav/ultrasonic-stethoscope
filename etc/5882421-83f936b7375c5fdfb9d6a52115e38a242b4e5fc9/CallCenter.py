from array import array
import pyaudio
import sys
import numpy as np
import matplotlib.pyplot as plt

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
#RATE = 44100
RATE = 16000
RECORD_SECONDS = 20

p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros([1,1024])[0] # our sample window
plt.ion() # interactive plotting on
ax1=plt.axes()  
ii16 = np.iinfo(np.int16) # get the max/min of int16
plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits
plt.grid()
line, = plt.plot(signal) # get the plot
# open an audio stream
stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)

# while we want to grab data
for i in range(0, 44100 / chunk * RECORD_SECONDS):
    # get the data from the stream
    data = stream.read(chunk)
    # change the stream to a numpy format
    signal = np.fromstring(data, 'Int16')
    # plot the data
    line.set_xdata(np.arange(len(signal)))
    line.set_ydata(signal)
    plt.draw()

stream.stop_stream()
stream.close()
p.terminate()
