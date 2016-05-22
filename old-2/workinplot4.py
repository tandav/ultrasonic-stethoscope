#!/usr/bin/env python

import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyaudio, sys


chunk = 1366
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
# windowwidth = 2048/2/2/2/2

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

# arr = np.zeros([1,windowwidth])[0]

# def animate(i):
#     global arr
#     data = stream.read(chunk)
#     signal = np.fromstring(data, 'Int16')
#     # print signal
#     if i == windowwidth - 1:
#         arr = np.zeros([1, windowwidth])[0]
#     else:
#         arr[i] = signal[i]
#     line.set_xdata(np.arange(len(arr)))
#     line.set_ydata(arr)
#     return line,

def animate(i):
    global arr
    data = stream.read(chunk)
    signal = np.fromstring(data, 'Int16')
    # print signal
    if i == chunk - 1:
        line.set_ydata(np.zeros([1, chunk])[0])

    line.set_xdata(np.arange(len(signal)))
    line.set_ydata(signal)
    return line,

def init():
    line.set_ydata(np.ma.array(np.zeros([1,chunk])[0], mask=False))
    return line,



# ani = animation.FuncAnimation(fig, animate, np.arange(1, chunk), interval=1, blit=True)
ani = animation.FuncAnimation(fig, animate, np.arange(1, chunk), init_func=init, interval=1, blit=True, repeat=True)
# ani = animation.FuncAnimation(fig, animate, np.arange(1, windowwidth), init_func=init, interval=1, blit=True)
plt.show()
stream.stop_stream()
stream.close()
p.terminate()