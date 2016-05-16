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

# def running_mean(x, N):
#     cumsum = np.cumsum(np.insert(x, 0, 0)) 
#     return (cumsum[N:] - cumsum[:-N]) / N # len(running_men(x, N)) = len(x) - (N - 1)


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(abs(x), 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N # len(running_men(x, N)) = len(x) - (N - 1)


chunk = 1500
# chunk = 1366
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
# chunks_per_window = 200
chunks_per_window = 115

run_mean_N = 100 # N in running_mean(x, N)
p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros(chunk)# our sample window
signal_prev = np.zeros(chunk)
# matrix = np.zeros((chunks_per_window, chunk))
matrix = np.zeros((chunks_per_window, chunk))

fig, ax= plt.subplots()
ii16 = np.iinfo(np.int16) # get the max/min of int16
# plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits
plt.ylim([-10000,10000]) # peg our chart to those limits

plt.grid()
# line, = plt.plot(np.zeros(chunk * chunks_per_window)) # get the plot
line, = plt.plot(np.zeros(chunk*chunks_per_window)) # get the plot

stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)


def animate(i): # todo add seconds on x_axis instead of arange
    signal = np.fromstring(stream.read(chunk), 'Int16')
    global signal_prev 
    matrix[i] = running_mean(np.concatenate((signal_prev[-(run_mean_N - 1):], signal)), run_mean_N)
    signal_prev = signal
    line.set_xdata(np.arange(chunk*chunks_per_window))
    line.set_ydata(np.hstack(matrix))

    # line.set_ydata(matrix[i])
    # line.set_xdata(np.arange(chunk*chunks_per_window))
    if i == 0: #mb remake that shit
        line.set_ydata(np.zeros(chunk*chunks_per_window))
    return line,

# def init():
#     line.set_ydata(np.zeros(chunk * chunks_per_window))
#     return line,

# ani = animation.FuncAnimation(fig, animate, np.arange(windowwidth), interval=5, blit=True)
ani = animation.FuncAnimation(fig, animate, np.arange(chunks_per_window), interval=1, blit=True)
plt.show()
stream.stop_stream()
stream.close()
p.terminate()