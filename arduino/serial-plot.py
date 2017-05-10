from multiprocessing import Process
import numpy as np
import serial
import matplotlib
matplotlib.use('TKAgg')
from matplotlib import pyplot as plt
from matplotlib import animation



buffer = []


#init serial device
try:
    ser = serial.Serial('/dev/cu.usbmodem1421', 250000)
except Exception as e:
    print("Can't connect to serial port")


def gather_data():
    global buffer
    while True:
        try:
            # bytesToRead = ser.inWaiting()
            # raw_bytes = ser.read(bytesToRead)
            raw_bytes = ser.read_all()
            
            if len(raw_bytes) > 1:
                # print(raw_bytes)
                bytes_array = raw_bytes.split(b'\r\n')
                for b in bytes_array:
                    try:
                        buffer.append(float(b))
                    except Exception as e:
                        pass
                        # print("float conversion error:", e)
                print(len(buffer))
                print("----------------")
        except Exception as e:
            # pass
            # print(e)
            print("Serial readline() error:", e)



p1 = Process(target=gather_data)
p1.start()
p1.join()

x_axis_points = 1000
y = np.zeros(x_axis_points)

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 2), ylim=(-3, 3))
line, = ax.plot(np.linspace(0, 2, x_axis_points), y, lw=2)






# # initialization function: plot the background of each frame
# def init():
#     line.set_data(np.linspace(0, 2, 10000), np.linspace(0, 2, 10000))
#     return line,

# animation function.  This is called sequentially
def animate(i):
    global y
    global buffer
    x = np.linspace(0, 2, x_axis_points)
    # y = np.sin(2 * np.pi * (x - 0.01 * i))
    y = y[len(buffer):]
    # y.extend(buffer)
    np.append(y, buffer)
    buffer = []

    line.set_data(x, y)
    return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, frames=200, interval=20, blit=True)
# anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=True)

plt.show()

# while True:
    # bytesToRead = ser.inWaiting()
    # print(ser.read(bytesToRead))
    # print(ser.readline())
