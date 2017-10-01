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
# RATE = 16000/2/2
j = 10
# windowwidth = 1500

p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros(chunk*j)# our sample window
# signal = np.zeros([1, chunk])[0] # our sample window

fig, ax= plt.subplots()
ii16 = np.iinfo(np.int16) # get the max/min of int16
# plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits
plt.ylim([-100000,100000]) # peg our chart to those limits

plt.grid()
line, = plt.plot(signal) # get the plot
stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)

# arr = np.zeros(chunk * j)
arr_n = np.zeros((j, chunk))
# arr_l = np.zeros(chunk * j)
# arr_n = np.array([[1, 2, 3], [4, 5, 6]], np.int16)

def animate(i):
    data = stream.read(chunk)
    signal = np.fromstring(data, 'Int16')

    arr_n[i] = signal

    # for k in xrange(j):
        # arr[i] = shrink(signal, j)[k]

    arr_l = np.hstack(arr_n)
    line.set_ydata(arr_l)
    # print np.arange(len(arr_l))
    line.set_xdata(np.arange(len(arr_l)))
    if i == 0:
        line.set_ydata(np.zeros(chunk * j))
    return line,

def init():
    # line.set_ydata(np.ma.array(np.zeros(chunk * j), mask=False))
    # line.set_ydata(np.ma.array(np.zeros(chunk * j), mask=False))
    line.set_ydata(np.zeros(chunk * j))
    return line,

# ani = animation.FuncAnimation(fig, animate, np.arange(windowwidth), interval=5, blit=True)
ani = animation.FuncAnimation(fig, animate, np.arange(j), interval=5, blit=True)
plt.show()
stream.stop_stream()
stream.close()
p.terminate()