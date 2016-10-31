#!/usr/bin/env python

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

def running_mean(x, N):
    cumsum = numpy.cumsum(numpy.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N # len(running_men(x, N)) = len(x) - (N - 1)


chunk = 1500
# chunk = 1366
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
# j = 200
j = 70

avg_len = 1500
p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros(chunk)# our sample window
# arr_n = np.zeros((j, chunk))
arr_n = np.zeros((j, avg_len))




fig, ax= plt.subplots()
ii16 = np.iinfo(np.int16) # get the max/min of int16
# plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits
plt.ylim([-10000,10000]) # peg our chart to those limits
plt.grid()
# line, = plt.plot(np.zeros(chunk * j)) # get the plot
# line, = plt.plot(np.zeros(avg_len*j)) # get the plot
line, = plt.plot(np.zeros(750)) # get the plot

stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)


def animate(i):
    # signal = np.fromstring(stream.read(chunk), 'Int16')
    signal = np.fromstring(stream.read(chunk), 'Int16')

    # arr_n[i] = shrink(signal, avg_len)
    arr_n[i] = signal
    # print len(arr_n[i]), len(np.fft.fft(arr_n[i]))
    # print len(shrink(signal, 100))
    
    # for k in xrange(j):
        # arr_n[i] = shrink(signal, j)[k]

    # line.set_xdata(np.arange(avg_len*j)) #norm
    # line.set_ydata(np.hstack(arr_n))     #norm
   
    # line.set_xdata(np.arange(avg_len*j))
    line.set_xdata(np.arange(750))
    line.set_ydata(np.fft.fft(arr_n[i])[750:])
    # ax.set_xscale('log')

    # line.set_ydata(arr_n[i])
    # line.set_xdata(np.arange(chunk*j))
    if i == 0:
        # line.set_ydata(np.zeros(avg_len*j))
        line.set_ydata(np.zeros(750))
    return line,

# def init():
#     line.set_ydata(np.zeros(chunk * j))
#     return line,

# ani = animation.FuncAnimation(fig, animate, np.arange(windowwidth), interval=5, blit=True)
ani = animation.FuncAnimation(fig, animate, np.arange(j), interval=1, blit=True)


plt.show()
stream.stop_stream()
stream.close()
p.terminate()