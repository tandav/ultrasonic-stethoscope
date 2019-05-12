import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()
import numpy as np

import time
from circular_buffer import CircularBuffer

import struct
import threading
lock = threading.Lock()
import scipy.fftpack
import scipy.signal
import util
stop_flag = 0

def read():
    # port.read_all()
    packet = port.read(512)
    mic = np.frombuffer(packet, dtype=np.uint16)

    # downsampling = 8
    downsampling = 1
    # downsampling = 2
    # downsampling = 4

    mic =  (
        mic
        .reshape(len(mic) // downsampling, downsampling)
        .mean(axis=1)
    )

    return mic


    # bmp0 = np.frombuffer(packet[ :4], dtype=np.float32)[0]
    # bmp0 = np.frombuffer(packet[ :4], dtype=np.float32)[0]
    # bmp1 = np.frombuffer(packet[4:8], dtype=np.float32)[0]

    # bmp0 = util.byte_to_float(packet[ :4])
    # bmp1 = util.byte_to_float(packet[4:8])

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

    # return bmp0, bmp1



# mic_un = 2**16
mic_un = 2**15
# mic_un = 2**12
# mic_un = 2**11
# mic_un = 2**10
# mic_un = 2**9
# mic_un = 24576

mic_buffer  = CircularBuffer(mic_un * 32, dtype=np.uint16)

rate = 0
_rate_arr = np.ones(10)
_rate_i = 0
rate_mean = 1

def run(mic_signal):
    # global is_tone_playing
    global bmp0, bmp1, rate, rate_mean, _rate_i

    mic_i = 0
    t0 = time.time()


    while True:

        if stop_flag:
            port.close()
            return

        mic = read()


        mic_buffer.extend(mic)
        mic_i += len(mic)

        if mic_i == mic_un:
            mic_i = 0

            now = time.time()
            dt = now - t0
            t0 = now

            rate = mic_un / dt
            _rate_arr[_rate_i] = rate
            _rate_i += 1
            if _rate_i == len(_rate_arr):
                rate_mean = _rate_arr.mean()
                _rate_i = 0
            # print(rate)

            mic_signal.emit()

# nfft = 2**18
# nfft = 100_000
# nfft = 200_000
nfft = 300_000


def get_mic():
    with lock:
        pp = 16
        mic = (
            mic_buffer
            .most_recent(mic_un)
            .reshape(pp, mic_un // pp)
            .mean(axis=1)
        )

        mic_for_fft = mic_buffer.most_recent(nfft)  # with overlap (running window for STFT)
        # mic_new = mic_raw[:-mic_un]
        # f = scipy.fftpack.rfftfreq(nfft, d=1/rate)
        # f = np.fft.rfftfreq(nfft, d=1/rate)
        # f = np.fft.rfftfreq(nfft, d=1/rate_mean)
        f = np.fft.rfftfreq(nfft, d=1/rate_mean/2)
        # f = np.fft.rfftfreq(nfft, d=1/rate/2)
        # f = scipy.fftpack.rfftfreq(nfft, d=1/rate_mean)
        # a = scipy.fftpack.rfft(mic_for_fft * scipy.signal.hanning(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft * np.hanning(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft * np.blackman(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft * np.hamming(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft)
        a = np.fft.rfft(mic_for_fft)
        a = np.abs(a)  # magnitude
        a = 20 * np.log10(a)  # часто ошибка - сделать try, else


        hz_limit  = (f > 40) & (f < 40_000)
        # hz_limit  = (f > 40) & (f < 10_000)
        # hz_limit  = (f > 500) & (f < 10_000)
        fft_f = f[hz_limit]
        fft_a = a[hz_limit]

        # fft_f = f
        # fft_a = a

        # fftpp = 2**12
        # fft_f = f[80:fftpp]
        # fft_a = a[80:fftpp]



        return mic, fft_f, fft_a, rate_mean


# def get():
#     n = 2 ** 8
#     with lock:
#         # return (
#         #     bmp0_buffer.most_recent(n),
#         #     bmp1_buffer.most_recent(n),
#         # )
#         #
#         return (
#             bmp0_buffer.buffer,
#             bmp1_buffer.buffer,
#         )
