import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()
import numpy as np
import util

import struct
import time



tmp_prev = b''
t_last = time.time()



i = 0



while True:
    tmp = port.read_all()

    # time.sleep(0.1)
    # tmp = port.read(256)
    print(len(tmp))

    # print(tmp.split())
    time.sleep(0.2)

    # sensor_0_bytes = port.read(4)
    # sensor_1_bytes = port.read(4)
    #
    # s0, = struct.unpack('f', sensor_0_bytes)
    # s1, = struct.unpack('f', sensor_1_bytes)
    #
    # print(s0, s1)

    # if tmp:
        # print(tmp, np.frombuffer(tmp, dtype=np.float32))
        # print(np.frombuffer(tmp, dtype=np.float32))
    # if tmp:
    #     if tmp != tmp_prev:
    #         tmp_prev = tmp
    #
    #         print(i, np.frombuffer(tmp, dtype=np.float32))
    # i += 1
    # tmp = port.read(16)
    # print(tmp)

    # print(port.read(4), port.read(4))

    # if tmp != tmp_prev:
    #     print('----', end=' ')
    #     tmp_prev = tmp

    #     t_now = time.time()
    #     dt = t_now - t_last
    #     t_last = t_now

    # print(f'{util.byte_to_float(tmp[:4]):.5f} {util.byte_to_float(tmp[4:8]):.5f}')
    # print(f'{byte_to_float(tmp[:4]):.5f} {byte_to_float(tmp[4:8]):.5f} {dt:.5f}')

        # print(f'blue: {s0:.5f}, red {s1:.5f} {state}')


    # print(byte_to_float(tmp[:4]), byte_to_float(tmp[4:8]))
    # tmp = port.read(4)

    # arr = np.frombuffer(tmp, dtype=np.float32)
    # print()
    # print(arr)

    # print(len(tmp))




    # bps = len(tmp) / dt


    # print(len(tmp), dt, len(set(arr)))
    # print(bps, 'bps')
