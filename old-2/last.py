# !/usr/bin/env python

import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyaudio, sys
import socket
import struct

TCP_IP = '192.168.137.1'
TCP_PORT = 5005
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# chunk = 4096
# chunk = 4096/2
chunk = 1366
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
# RATE = 44100
RECORD_SECONDS = 40
windowwidth = 1024/2/2/2

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

arr = np.zeros([1,windowwidth])[0]

def animate(i):
    global arr
    data = stream.read(chunk)
    signal = np.fromstring(data, 'Int16')
    # s.send((chunk).to_bytes(4, byteorder='little'))
    
    # for x in signal:
        # s.send(struct.pack("<i", x))
    
    # n = int.from_bytes(s.recv(4), byteorder='little')
   
    # for i in range(n):
    #     data = s.recv(4)
    #     data = struct.unpack('f', data)
    #     print("received data:", data)
    # # print signal
    if i == windowwidth - 1:
        arr = np.zeros([1,windowwidth])[0]
    else:
        arr[i] = sum([abs(j) for j in signal])
    # arr[i] = sum([abs(j) for j in signal])
    line.set_ydata(arr)  # update the data
    return line,

# def init():
#     line.set_ydata(np.ma.array(arr, mask=True))
#     return line,

# s.close()


ani = animation.FuncAnimation(fig, animate, np.arange(1, windowwidth), interval=1, blit=True)
# ani = animation.FuncAnimation(fig, animate, np.arange(1, windowwidth), init_func=init, interval=1, blit=True)
plt.show()

stream.stop_stream()
stream.close()
p.terminate()


