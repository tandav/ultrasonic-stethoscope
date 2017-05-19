import serial
import numpy as np
import matplotlib
matplotlib.use('TKAgg')
from matplotlib import pyplot as plt
from matplotlib import animation
import serial

#init serial device
ser = serial.Serial('/dev/cu.usbmodem1421', 9600)
y = np.zeros(10000)

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 2), ylim=(-3, 3))
line, = ax.plot(np.linspace(0, 2, 10000), y, lw=2)


# # initialization function: plot the background of each frame
# def init():
#     line.set_data(np.linspace(0, 2, 10000), np.linspace(0, 2, 10000))
#     return line,

# animation function.  This is called sequentially
def animate(i):
    global y
    for x in xrange(1,10):
        pass
    np.delete(y, 0)
    np.append(y, ser.readline())
    line.set_ydata(y)
    return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, frames=200, interval=20, blit=True)
# anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=True)

plt.show()

# while True:
    # bytesToRead = ser.inWaiting()
    # print(ser.read(bytesToRead))
    # print(ser.readline())
