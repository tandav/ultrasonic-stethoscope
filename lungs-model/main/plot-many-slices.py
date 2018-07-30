import numpy as np
import matplotlib
# matplotlib.use('Qt5Agg')
matplotlib.use('macosx')
import matplotlib.pyplot as plt

P = np.random.random((16, 16, 16))

def cube_slices(cube, rows=4, cols=4):
    fig, ax = plt.subplots(rows, cols, figsize=(8,8))

    k = 0
    for row in range(rows):
        for col in range(cols):
            ax[row, col].set_title(f'slice {k}')
            ax[row, col].imshow(cube[k], cmap='viridis')
            ax[row, col].axis('off')
            k += 1

    # you can adjust it from plt.show() dialog
    plt.subplots_adjust(wspace=.01, hspace=0.3)
    plt.subplots_adjust(left=0, right=1, top=0.95, bottom=0.05)
    plt.show()
    # plt.savefig('slices.png')
    # plt.savefig('slices.pdf')


cube_slices(P, rows=4, cols=4)

# --------------------------------------------------------------

# class IndexTracker(object):
#     def __init__(self, ax, X):
#         self.ax = ax

#         self.X = X
#         rows, cols, self.slices = X.shape
#         self.ind = self.slices//2

#         self.im = ax.imshow(self.X[:, :, self.ind])
#         self.update()

#     def onscroll(self, event):
#         print("%s %s" % (event.button, event.step))
#         if event.button == 'up':
#             self.ind = np.clip(self.ind + 1, 0, self.slices - 1)
#         else:
#             self.ind = np.clip(self.ind - 1, 0, self.slices - 1)
#         self.update()

#     def update(self):
#         self.im.set_data(self.X[:, :, self.ind])
#         ax.set_title(f'slice {self.ind} | use scroll wheel')
#         self.im.axes.figure.canvas.draw()


# fig, ax = plt.subplots(1, 1)


# tracker = IndexTracker(ax, P)


# fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
# plt.show()
