
import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import random as random
from matplotlib import pyplot as plt
from matplotlib import animation

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 50), ylim=(0, 50))
line, = ax.plot([], [], lw=2)

n=5
a = [0,1,2,4,5,8,9,12,14,18,22,17,30,37,29,45]

x = []
y = []

# initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return line,

# animation function.  This is called sequentially
def animate(i):
    x.append(np.linspace(i,i+1,n))
    y.append(np.linspace(a[i],a[i+1],n))
    line.set_data(x,y)

    return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, np.arange(0,len(a)-1) ,init_func=init, 
                               interval=2, blit=True, repeat=False)

plt.show()