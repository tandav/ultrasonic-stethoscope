import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from time import time

P = np.random.random((16, 16, 16))


fig, ax = plt.subplots()

ax.imshow(P[7])


def step(event):
    t0 = time()
    P = np.random.random((16, 16, 16))
    ax.imshow(P[7])
    # plt.draw()
    print(f'step {time() - t0}')


step_ax = plt.axes([0.7, 0.05, 0.1, 0.075]) # rect = [left, bottom, width, height]
bnext = Button(step_ax, 'Step')
bnext.on_clicked(step)

plt.show()
