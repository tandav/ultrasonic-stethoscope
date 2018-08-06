import serial # TODO: try del
import serial.tools.list_ports
import numpy as np
import signal

def find_device_and_return_port():
    for i in range(61):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if 'Arduino' in port.description or \
               'Устройство с последовательным интерфейсом USB' in port.description or \
               'USB Serial Device' in port.description: 
            # if ('Устройство с последовательным интерфейсом USB') in port.description: 
                # try / except
                ser = serial.Serial(port.device)
                print('device connected')
                break
        else:
            if i == 60:
                print('\nDevice not found. Check the connection.')
                sys.exit()
            sys.stdout.write('\rsearching device' + '.'*i + ' ')
            sys.stdout.flush()
            time.sleep(0.05)
            continue  # executed if the loop ended normally (no break)
        break  # executed if 'continue' was skipped (break)
    return ser



port = find_device_and_return_port()

while True:
    # data = port.read(512)

    # print(np.frombuffer(data, dtype=np.uint32)[:6])

    # data = port.read(512)

    # if b'\xd2\x02\x96I' in data:  
        # timings = np.frombuffer(data, dtype=np.uint32)
        # print(timings[:6])

    # else:
        # data = np.frombuffer(data, dtype=np.uint16)

    data = port.read_until(b'\xd2\x02\x96I')

    t_data = port.read(508)
    print(np.frombuffer(t_data, dtype=np.uint32)[:6])

    # some mic data processing

    # tone_playing = port.read(8)
    # print(np.frombuffer(tone_playing, dtype=np.uint32))

    # current_tone_i = port.read(4)
    # print(np.frombuffer(current_tone_i, dtype=np.uint32))
    # time_data = port.read(511)
    # timings = np.frombuffer(time_data, dtype=np.uint32)
    # print(timings[:6])



port.close()
