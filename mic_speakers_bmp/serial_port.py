import threading
import collections
import time
from circular_buffer import CircularBuffer
import numpy as np
import scipy.io.wavfile
import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()

header = b'\xd2\x02\x96I'

# lengths are in bytes
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
    bmp0 = np.frombuffer(packet[ :4], dtype=np.float32)[0] # frombuffer has offset and count args
    bmp1 = np.frombuffer(packet[4:8], dtype=np.float32)[0]
    is_tone_playing = np.frombuffer(packet[8:9], dtype=np.uint8)[0]
    # mic = np.frombuffer(packet[9:521], dtype=np.uint16)

    mic = np.empty(256, dtype=np.uint16)
    mic[:] = np.frombuffer(packet[9:521], dtype=np.uint16)

    # downsampling = 4
    # downsampling = 8x
    downsampling = 1


    mic =  (
        mic
        .reshape(len(mic) // downsampling, downsampling)
        .mean(axis=1)
    )
    # print(mic)
    # print(sum(mic == 0))

    return bmp0, bmp1, is_tone_playing, mic


lock = threading.Lock()


is_tone_playing = None



# mic_un = 2**16
mic_un = 2**15
# mic_un = 2**14
# mic_un = 2**13
# mic_un = 2**12
# mic_un = 2**11
# mic_un = 2**10
# mic_un = 2**9
# mic_un = 24576

# mic_buffer = CircularBuffer(mic_un * 32, dtype=np.uint16)
mic_buffer = CircularBuffer(mic_un * 128, dtype=np.uint16)

'''
bmp changes are slow so
every new pair (bmp0, bmp1) emiting plot update
'''


bmp_i = 0 # for callibration
normal_dp = 0
bmp0 = 0
bmp1 = 0
state = 'норм'
state_prev = 'норм'

rate = 0
_rate_arr = np.ones(10)
_rate_i = 0
rate_mean = 1


is_recording = False
values_recorded = 0
record_state = None

def start_record(state):
    global is_recording, values_recorded, record_state
    is_recording = True
    values_recorded = 0
    record_state = state


def stop_record():
    global is_recording, values_recorded
    is_recording = False

    if values_recorded > 0:

        timestamp = int(time.time() * 1000)

        signal = mic_buffer.most_recent(values_recorded).astype(np.float32) * (3.3 / 2**12) * 2 / 3.3 - 1
        # signal = mic_buffer.most_recent(values_recorded)
        print(type(signal), signal.dtype, signal.shape)

        with open(f'records/{timestamp}-{record_state}.wav', 'wb') as wav_file:
        # with open(f'records/wav/{timestamp}-{record_state}.npy', 'wb') as wav_file:
        #     np.save(wav_file, signal)


            scipy.io.wavfile.write(
                wav_file,
                int(rate_mean),
                signal,
            )

        values_recorded = 0




def run(bmp_signal, mic_signal):
    # global is_tone_playing
    global bmp0, bmp1, bmp_i, normal_dp, state, state_prev, rate, rate_mean, _rate_i, values_recorded

    bmp0_prev = 0
    bmp1_prev = 0
    mic_i = 0
    t0 = time.time()


    while True:

        if stop_flag:
            port.close()
            return

        bmp0, bmp1, is_tone_playing, mic = read_packet()


        # _mmm = (
        #     mic_buffer
        #     .most_recent(mic_un)
        # )
        #
        # print(sum(_mmm == 0))


        if bmp0 != bmp0_prev or bmp1 != bmp1_prev:

            bmp0_prev = bmp0
            bmp1_prev = bmp1

            bmp_i += 1

            if bmp_i == 8:
                normal_dp = bmp0 - bmp1
                print('normal_dp', normal_dp)

            bmp0 -= normal_dp

            if bmp_i > 5:
                dp = 20
                # dp = 10
                # print(bmp0 - bmp1)
                if bmp0 - bmp1 > dp:
                    state = 'выдох'
                elif bmp1 - bmp0 > dp:
                    state = 'вдох'
                else:
                    state = 'норм'

                if state != state_prev:
                    stop_record()

                    if state in ('выдох', 'вдох'):
                        start_record(state)
                    state_prev = state
                    print(state)




            # if not is_recording:
            bmp_signal.emit()

        # print(sum(mic == 0))

        mic_buffer.extend(mic)

        mic_i += len(mic)

        if is_recording:
            values_recorded += len(mic)

        if mic_i == mic_un:
            # print(mic_un, 'done')
            mic_i = 0

            t1 = time.time()
            dt = t1 - t0
            rate = mic_un / dt
            _rate_arr[_rate_i] = rate
            _rate_i += 1
            if _rate_i == len(_rate_arr):
                rate_mean = _rate_arr.mean()
                _rate_i = 0
            # print(rate)
            t0 = t1

            # if not is_recording:
            mic_signal.emit()



def get_bmp():
    with lock:
        return bmp0, bmp1, state



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


# nfft = 2**17
# nfft = 100_000
# nfft = 110_000
nfft = 300_000
# nfft = 90_000
# nfft = 70_000
# nfft = 2**16
# nfft = 2**16
# nfft = 2**15
# nfft = 40_000

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
        f = np.fft.rfftfreq(nfft, d=1/rate_mean/2)


        # mic_new = mic_raw[:-mic_un]
        # f = scipy.fftpack.rfftfreq(nfft, d=1/rate)
        # f = scipy.fftpack.rfftfreq(nfft, d=1/rate_mean)
        # a = scipy.fftpack.rfft(mic_for_fft * scipy.signal.hanning(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft * np.hanning(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft * np.blackman(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft * np.hamming(nfft))
        # a = scipy.fftpack.rfft(mic_for_fft)
        a = np.fft.rfft(mic_for_fft)
        a = np.abs(a)  # magnitude

        # a = 20 * np.log10(a)  # часто ошибка - сделать try, else
        a = 10 * np.log10(a)  # часто ошибка - сделать try, else


        hz_limit  = (f > 40) & (f < 40_000)
        # hz_limit  = (f > 40) & (f < 10_000)

        fft_f = f[hz_limit]
        fft_a = a[hz_limit]


        # fftpp = 2**12
        #
        # fft_f = f[80:fftpp]
        # fft_a = a[80:fftpp]



        return mic, fft_f, fft_a, rate_mean
