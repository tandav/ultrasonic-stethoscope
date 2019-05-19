import serial # TODO: try del
import serial.tools.list_ports
import sys
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', action='store_true', help='no arduino, for quick tests')
args = parser.parse_args()

if args.n:
    pass
else:
    def arduino_due():
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

    port = arduino_due()



# # test
# while True:
#     print('.')
#     sensor_0_bytes = port.read(4)
#     sensor_1_bytes = port.read(4)
#     print(sensor_0_bytes)
#     time.sleep(0.1)


fig, ax = plt.subplots(figsize=(8, 6))
ax.set_facecolor((0,0,0,0.1))
# x = np.arange(0, 2*np.pi, 0.01)
x = np.arange(100)
y0 = np.zeros(x.shape)
y1 = np.zeros(x.shape)
yd = np.zeros(x.shape)

line0, = ax.plot(x,  y0, color='blue', label='sensor 0')
line1, = ax.plot(x,  y1, color='red' , label='sensor 1')
line_d, = ax.plot(x, yd, color='lime', label='differece')

lines = (line0, line1, line_d)

def animate(i):
    global y0, y1, yd

    # port.read_all()

    # sensor_0_bytes = port.read(4)
    # sensor_1_bytes = port.read(4)

    # f0, = struct.unpack('f', sensor_0_bytes)
    # f1, = struct.unpack('f', sensor_1_bytes)


    # f0 /= 100_000
    # f1 /= 100_000

    f0 = np.random.random()
    f1 = np.random.random()

    print(f0, f1)
    y0 = np.roll(y0, -1)
    y0[-1] = f0

    y1 = np.roll(y1, -1)
    y1[-1] = f1

    yd = np.roll(yd, -1)
    yd[-1] = abs(f0 - f1)

    # print(time.time())

    line0.set_ydata(y0)  # update the data
    line1.set_ydata(y1)  # update the data
    line_d.set_ydata(yd)  # update the data
    # return line0, line1
    # return lines
    return lines


ani = animation.FuncAnimation(
    fig      = fig    , 
    func     = animate, 
    interval = 10     ,
    blit     = True   ,
)

# plt.ylim(0, 120_000)
# plt.ylim(0.98, 1)
# plt.ylim(0.99, 1.01)
plt.ylim(0, 1)
plt.legend()
plt.show()










