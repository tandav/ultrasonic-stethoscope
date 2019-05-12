'''
lengths are in bytes
'''
import threading
import collections
import time
import scipy.fftpack
import scipy.signal
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
        if n_good_packets % 5000 == 0:
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

    # downsampling = 4
    downsampling = 8

    mic =  (
        mic
        .reshape(len(mic) // downsampling, downsampling)
        .mean(axis=1)
    )

    return bmp0, bmp1, is_tone_playing, mic


lock = threading.Lock()


is_tone_playing = None


# packets_to_emit = 64
# packets_to_emit = 128

# mic_un = 2**16
# mic_un = 2**15
# mic_un = 2**14
# mic_un = 2**13
mic_un = 2**11
# mic_un = 2**10
# mic_un = 2**9
# mic_un = 24576

mic_buffer  = CircularBuffer(mic_un * 16, dtype=np.uint16)
# mic_buffer_export  = mic_buffer.buffer.reshape(pp, len(mic_buffer.buffer) // pp).mean(axis=1)

'''
bmp changes are slow so
every new pair (bmp0, bmp1) emiting plot update
'''

bmp0 = 0
bmp1 = 0

rate = 0



def run(bmp_signal, mic_signal):
    # global is_tone_playing
    global bmp0, bmp1, rate

    bmp0_prev = 0
    bmp1_prev = 0
    mic_i = 0
    t0 = time.time()


    while True:

        if stop_flag:
            port.close()
            return

        bmp0, bmp1, is_tone_playing, mic = read_packet()

        if bmp0 != bmp0_prev or bmp1 != bmp1_prev:

            bmp0_prev = bmp0
            bmp1_prev = bmp1

            bmp_signal.emit()


        mic_buffer.extend(mic)
        mic_i += len(mic)

        if mic_i == mic_un:
            mic_i = 0

            t1 = time.time()
            dt = t1 - t0
            rate = mic_un / dt
            # print(rate)
            t0 = t1

            mic_signal.emit()



def get_bmp():
    with lock:
        return bmp0, bmp1



# def get_mic(n):
#     with lock:
#         mic_raw = mic_buffer.most_recent(n) # with overlap (running window for STFT)
#         mic_new = mic_raw[:-mic_un]
#         return mic_raw, mic_new, rate
#


# def get_mic(n):
#     with lock:
#         mic_raw = mic_buffer.most_recent(n)  # with overlap (running window for STFT)
#         # mic_new = mic_raw[:-mic_un]
#         mic_new = mic_buffer.most_recent(mic_un)
#
#         return mic_raw, mic_new, rate


nfft = 2**13

def get_mic():
    with lock:
        pp = 8
        mic = (
            mic_buffer
            .most_recent(mic_un)
            .reshape(pp, mic_un // pp)
            .mean(axis=1)
        )

        mic_for_fft = mic_buffer.most_recent(nfft)  # with overlap (running window for STFT)
        # mic_new = mic_raw[:-mic_un]
        f = scipy.fftpack.rfftfreq(nfft, d=1./rate)
        a = scipy.fftpack.rfft(mic_for_fft * scipy.signal.hanning(nfft))
        a = np.abs(a)  # magnitude
        a = 20 * np.log10(a)  # часто ошибка - сделать try, else

        fft_pp = 2 ** 10

        fft_f = f[::nfft // fft_pp]
        fft_a = a[::nfft // fft_pp]


        return mic, fft_f, fft_a, rate
