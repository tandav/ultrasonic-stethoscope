#!/usr/bin/env python
# Have a nice show!

# create an array of arrays 
# in a loop fill that array with signal
# and concatenate into one array
# and send return it to line,
import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyaudio, sys

def shrink(arr, n):
    chunk = len(arr) / n
    arr_out = []
    avg = 0.
    for i in xrange(len(arr)):
        if (i % chunk == 0 and i != 0):
            arr_out.append(avg / chunk)
            avg = 0
        avg += arr[i]
    arr_out.append(avg / chunk)
    return arr_out


chunk = 1500
# chunk = 1366
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
j = 60

p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros(chunk)# our sample window
arr_n = np.zeros((j, chunk))


fig, ax= plt.subplots()
ii16 = np.iinfo(np.int16) # get the max/min of int16
plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits
# plt.ylim([-100000,100000]) # peg our chart to those limits

plt.grid()
line, = plt.plot(np.zeros(chunk * j)) # get the plot

stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)


def animate(i):
    signal = np.fromstring(stream.read(chunk), 'Int16')

    # arr_n[i] = sum(signal) / 
    arr_n[i] = signal
    # for k in xrange(j):
        # arr[i] = shrink(signal, j)[k]

    line.set_ydata(np.hstack(arr_n))
    line.set_xdata(np.arange(chunk*j))
    if i == 0:
        line.set_ydata(np.zeros(chunk * j))
    return line,

def init():
    line.set_ydata(np.zeros(chunk * j))
    return line,

# ani = animation.FuncAnimation(fig, animate, np.arange(windowwidth), interval=5, blit=True)
ani = animation.FuncAnimation(fig, animate, np.arange(j), interval=5, blit=True)
plt.show()
stream.stop_stream()
stream.close()
p.terminate()