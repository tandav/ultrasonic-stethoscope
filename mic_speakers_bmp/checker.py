import numpy as np
import serial_port

i = 0

while True:
    packet = serial_port.read_packet()

    # print(packet)
    # print(len(packet), '\n')

    b0 = np.frombuffer(packet[ :4], dtype=np.float32)
    b1 = np.frombuffer(packet[4:8], dtype=np.float32)
    is_tone_playing = np.frombuffer(packet[8:9], dtype=np.uint8)
    # buffer = np.frombuffer(packet[9:], dtype=np.uint16)


    # print(b0, b1, is_tone_playing)

    # print(b0, b1, is_tone_playing, buffer, i)
    # print(b0, b1, is_tone_playing, i)

    # print(data, [i for i in data])
    # print([i for i in data])
    # print('-' * 72)


    # wait_header(arduino, header)





    # with util.DelayedKeyboardInterrupt():
    #     packet = arduino.read(521)
        # packet = arduino.read(132)
    #
    #
    # header = packet[:4]
    # buffer = np.frombuffer(packet[4:], np.uint8)
    #
    # print(header, buffer)


    # assert is_tone_playing == 0 or is_tone_playing == 1, f'error: packet offset, {is_tone_playing}'
    #
    # print(b0, b1, is_tone_playing, buffer, i)
    # print(z, len(z), [int(x) for x in z])
    # print(z, len(z), np.frombuffer(z, dtype=np.uint32))
    # print(z, len(z), np.frombuffer(z, dtype=np.float32))
    # print(np.frombuffer(z, dtype=np.float32), i)
    i += 1
    # print(z, z.decode())
    # time.sleep(1)
