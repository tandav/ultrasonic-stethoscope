#!/usr/bin/env python

import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyaudio, sys

chunk = 1366
# chunk = 1300
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
j = 3
windowwidth = chunk * j

p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros([1, chunk])[0] # our sample window
fig, ax= plt.subplots()



# plt.ion() # interactive plotting on
# ax1=plt.axes()  
ii16 = np.iinfo(np.int16) # get the max/min of int16
# plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits

# print ii16.max
plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits
# plt.ylim([0,10000000]) # peg our chart to those limits

plt.grid()
line, = plt.plot(signal) # get the plot
# open an audio stream
stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)

arr = np.zeros([1, windowwidth])[0]

def animate(i):
    # global arr
    data = stream.read(chunk)
    signal = np.fromstring(data, 'Int16')

    for k in xrange(chunk):
        arr[i * chunk + k] = signal[k]

    line.set_ydata(arr)
    line.set_xdata(np.arange(windowwidth))
    if i == 0:
        line.set_ydata(np.zeros([1, windowwidth])[0])

    return line,

def init():
    line.set_ydata(np.ma.array(np.zeros([1, windowwidth])[0], mask=False))
    return line,



# ani = animation.FuncAnimation(fig, animate, np.arange(j), init_func=init, interval=1, blit=True)
ani = animation.FuncAnimation(fig, animate, np.arange(j), interval=5, blit=True)
plt.show()
stream.stop_stream()
stream.close()
p.terminate()