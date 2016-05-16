#!/usr/bin/env python
import socket
import struct

import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyaudio, sys

TCP_IP = '192.168.137.1'
TCP_PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ####
s.connect((TCP_IP, TCP_PORT)) ####

chunk = 1600 # try to change this value if "[Errno -9981] Input overflowed" , min1366
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
# RATE = 44100
RECORD_SECONDS = 40
# windowwidth = 1024/2/2/2
windowwidth = 128

p = pyaudio.PyAudio() # pyaduio init
signal = np.zeros([1, windowwidth])[0] # our sample window
fig, ax= plt.subplots()


# plt.ion() # interactive plotting on
# ax1=plt.axes()
# ii16 = np.iinfo(np.int16) # get the max/min of int16
# plt.ylim([ii16.min,ii16.max]) # peg our chart to those limits

# print ii16.max
# plt.ylim([0,ii16.max]) # peg our chart to those limits
plt.ylim([0,10000000]) # peg our chart to those limits

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

s.send((windowwidth).to_bytes(4, byteorder='little')) #######



def animate(i):
    global arr
    data = stream.read(chunk)
    signal = np.fromstring(data, 'Int16')

    for x in signal:
        s.send(struct.pack("<i", x))

    n = int.from_bytes(s.recv(4), byteorder='little')
    arr = np.zeros([1, n])[0]

    for i in range(n):
        recv_data = s.recv(4)
        recv_data = struct.unpack('f', recv_data)
        # print(recv_data)
        arr[i] = recv_data[0]
        # print("received data:", data)
        print(arr[i])


    # print signal
    if i == windowwidth - 1:
        arr = np.zeros([1,windowwidth])[0]
    else:
        arr[i] = sum([abs(j) for j in recv_data])
    # arr[i] = sum([abs(j) for j in signal])
    line.set_ydata(arr)  # update the data
    return line,

# def init():
#     line.set_ydata(np.ma.array(arr, mask=True))
#     return line,




ani = animation.FuncAnimation(fig, animate, np.arange(1, windowwidth), interval=50, blit=True)
# ani = animation.FuncAnimation(fig, animate, np.arange(1, windowwidth), init_func=init, interval=1, blit=True)
plt.show()

stream.stop_stream()
stream.close()
p.terminate()
