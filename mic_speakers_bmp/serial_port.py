'''
lengths are in bytes
'''
import threading
import collections
import time

from circular_buffer import CircularBuffer
import numpy as np
import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()

header = b'\xd2\x02\x96I'

bmp_pressure_length    =   4 # float32 number
mic_length             = 512 # 256 uint16
mic_chunk_size         = mic_length // 2 # uint16 takes 2 bytes

is_tone_playing_length =   1 # uint8 (used like bool)

payload_length         =   2 * bmp_pressure_length + is_tone_playing_length + mic_length
packet_length          = len(header) + payload_length

stop_flag = 0

n_good_packets = 0


def wait_header():
    deque = collections.deque(maxlen=len(header))

    while b''.join(deque) != header:
        deque.append(port.read())

    print('wait done', b''.join(deque), '==', header)


def read_packet_bytes():
    '''
    packet_length: packet length in bytes
    returns packet (as bytes) without header
    '''

    global n_good_packets

    packet = port.read(packet_length)

    if packet.startswith(header):
        n_good_packets += 1
        if n_good_packets % 4000 == 0:
            print(f'n_good_packets = {n_good_packets}')
        return packet[len(header):]
    else:
        print(f'wrong header {packet[:len(header)]} before: n_good_packets = {n_good_packets}')
        n_good_packets = 0
        # time.sleep(1)
        wait_header()
        return port.read(payload_length) # rest of packet


def read_packet():
    packet = read_packet_bytes()
    # parse data from bytes packet
    bmp0 = np.frombuffer(packet[ :4], dtype=np.float32)[0]
    bmp1 = np.frombuffer(packet[4:8], dtype=np.float32)[0]
    is_tone_playing = np.frombuffer(packet[8:9], dtype=np.uint8)[0]
    mic = np.frombuffer(packet[9:521], dtype=np.uint16)

    return bmp0, bmp1, is_tone_playing, mic


lock = threading.Lock()

# BUFFER_N = 2 ** 12



# pp = 4096 // 2  # number of points to plot


is_tone_playing = None


# packets_to_emit = 64
# packets_to_emit = 128

# mic_un = 2**16
# mic_un = 2**15
# mic_un = 2**14
mic_un = 2**13
# mic_un = 24576

mic_buffer  = CircularBuffer(mic_un, dtype=np.uint16)
# mic_buffer_export  = mic_buffer.buffer.reshape(pp, len(mic_buffer.buffer) // pp).mean(axis=1)

'''
bmp changes are slow so
every new pair (bmp0, bmp1) emiting plot update
'''

bmp0 = 0
bmp1 = 0

mic_i = 0


def run(bmp_signal, mic_signal):
    # global is_tone_playing
    global bmp0, bmp1, mic_i


    bmp0_prev = 0
    bmp1_prev = 0

    # last_change = time.time()

    # with lock here??
    while True:
        # for _ in range(packets_to_emit):

        if stop_flag:
            port.close()
            return

        bmp0, bmp1, is_tone_playing, mic = read_packet()

        mic_buffer.extend(mic)
        mic_i += len(mic)

        if mic_i == mic_un:

            mic_i = 0
            mic_signal.emit()


        if bmp0 != bmp0_prev or bmp1 != bmp1_prev:

            bmp0_prev = bmp0
            bmp1_prev = bmp1

            bmp_signal.emit()




            # print(bmp0, bmp1, time.time() - last_change)
            # last_change = time.time()

        mic_buffer.extend(mic)

        # with lock:
        #     bmp0_buffer_export = bmp0_buffer.buffer.copy()
        #     bmp1_buffer_export = bmp1_buffer.buffer.copy()
        #     mic_buffer_export  = mic_buffer.buffer.reshape(pp, len(mic_buffer.buffer) // pp).mean(axis=1)

        # signal.emit()


def get_bmp():
    with lock:
        return bmp0, bmp1

def get_mic():
    with lock:
        return mic_buffer.most_recent(mic_un)


def get_buffers():
    with lock:
        return (
            bmp0_buffer.buffer.copy(),
            bmp1_buffer.buffer.copy(),
            mic_buffer.buffer.reshape(pp, len(mic_buffer.buffer) // pp).mean(axis=1),
        )

        # return (
        #     bmp0_buffer_export,
        #     bmp1_buffer_export,
        #     mic_buffer_export,
        # )


    # def get(n):
#     bmp0 = bmp0_buffer.most_recent(n)
#     bmp1 = bmp1_buffer.most_recent(n)
#     mic  = mic_buffer.most_recent(n * mic_chunk_size)
#
#     return bmp0, bmp1, is_tone_playing, mic
#



