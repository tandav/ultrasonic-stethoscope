import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()
import numpy as np

import time
from circular_buffer import CircularBuffer

import struct
import threading
lock = threading.Lock()

import util
stop_flag = 0

def read():
    # port.read_all()
    packet = port.read(8)
    # bmp0 = np.frombuffer(packet[ :4], dtype=np.float32)[0]
    # bmp1 = np.frombuffer(packet[4:8], dtype=np.float32)[0]

    bmp0 = util.byte_to_float(packet[ :4])
    bmp1 = util.byte_to_float(packet[4:8])

    # bmp0_bytes = port.read(4)
    # bmp1_bytes = port.read(4)

    # bmp0, = struct.unpack('f', bmp0_bytes)
    # bmp1, = struct.unpack('f', bmp1_bytes)


    # bs = 128
    #
    # packet = port.read(bs * 4)
    #
    # bmp0 = np.frombuffer(packet[  :bs//2 * 4], dtype=np.float32)
    # bmp1 = np.frombuffer(packet[bs//2 * 4:], dtype=np.float32)

    return bmp0, bmp1



BUFFER_N = 2**10
bmp0_buffer = CircularBuffer(BUFFER_N, dtype=np.float32)
bmp1_buffer = CircularBuffer(BUFFER_N, dtype=np.float32)

packets_to_emit = 1


def run(signal):

    while True:
        if stop_flag:
            return
        for _ in range(packets_to_emit):


            bmp0, bmp1 = read()
            # print(time.time())

            bmp0_buffer.append(bmp0)
            bmp1_buffer.append(bmp1)
            # bmp0_buffer.extend(bmp0)
            # bmp1_buffer.extend(bmp1)

        signal.emit()



def get():
    n = 2 ** 8
    with lock:
        # return (
        #     bmp0_buffer.most_recent(n),
        #     bmp1_buffer.most_recent(n),
        # )
        #
        return (
            bmp0_buffer.buffer,
            bmp1_buffer.buffer,
        )
