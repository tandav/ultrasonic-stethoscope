import sys
import pyqtgraph as pg
import numpy as np
import PyQt5.QtWidgets
import PyQt5.QtCore
import time
import matplotlib.cm
import PIL.Image



# HUMAN_BODY_PATH = '../cube-full-460-512-512.npy'
# c = np.load(HUMAN_BODY_PATH)[::-1][30:250, 289, 125:390].T[:,::-1]

c = np.array(PIL.Image.open('normal-chest-ct-lung-window-1.jpg'))[:,:,0].T[:,::-1]
density = 1e-5 + 1.24e-3 * c - 2.83e-7 * c * c + 2.79e-11 * c * c * c
# density *= 10

class Window(PyQt5.QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')


        # self.NX = 300  # 空間セル数 X [pixels]
        # self.NY = 400  # 空間セル数 Y [pixels]

        self.NX = c.shape[0]
        self.NY = c.shape[1]

        self.dx = 0.01  # 空間刻み [m]
        self.dt = 20.0e-6  # 時間刻み [s]

        self.Nstep = 5_000  # 計算ステップ数 [回]

        self.freq = 1.0e3  # 初期波形の周波数 [Hz]

        # self.density = 1.3  # [kg/m^3]
        # self.density = 1.3 + 0.7 * np.random.random((self.NX, self.NY)).astype('float128')
        self.density = density
        # self.density = np.full((self.NX, self.NY), 1.3, "float128")

        self.kappa = 142.0e3  # 体積弾性率κ [Pa] Bulk modulus κ

        self.Vx = np.zeros((self.NX + 1, self.NY), "float128")  # x Directional particle velocity [m/s]
        self.Vy = np.zeros((self.NX, self.NY + 1), "float128")  # y Directional particle velocity [m/s]
        self.P = np.zeros((self.NX, self.NY), "float128")  # Sound pressure [Pa]

        # self.shape = (32, 32)
        self.shape = (self.NX, self.NY)

        # self.a = np.random.random(self.shape)
        self.glayout = pg.GraphicsLayoutWidget()
        # self.glayout.ci.layout.setContentsMargins(0, 0, 0, 0)

        self.density_img = pg.ImageItem(self.density, autoLevels=False, levels=(0, 0.3))

        self.img = pg.ImageItem(self.P, autoLevels=False, levels=(0, 1), border=pg.mkPen(color='b', width=1))

        # Get the colormap
        colormap = matplotlib.cm.magma
        colormap._init()
        lut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt

        # Apply the colormap
        self.img.setLookupTable(lut)

        self.pplot = self.glayout.addPlot()

        self.pplot.setAspectLocked()
        # self.pplot.setMouseEnabled(x=False, y=False)
        # self.pplot.setMenuEnabled(False)
        # self.pplot.setXRange(0, 200, padding=0)
        # self.pplot.setYRange(0, 400, padding=0)

        # self.pplot.invertY(True)
        # self.img.setRect(pg.QtCore.QRectF(0, 0, self.a.shape[0] - 1, self.a.shape[1] - 1))
        self.pplot.addItem(self.density_img)
        self.pplot.addItem(self.img)

        # set the layout
        layout = PyQt5.QtWidgets.QVBoxLayout()
        # layout.addWidget(self.plot)
        layout.addWidget(self.glayout)

        # layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.setGeometry(0, 0, 1300, 900)

        # updating the plots
        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0) # Timer tick. Set 0 to update as fast as possible
        self.n = 0

    def update(self):
        # Update particle velocity
        # self.Vx[1:self.NX, :] += - self.dt / self.density / self.dx * (self.P[1:self.NX, :] - self.P[0:self.NX - 1, :])
        # self.Vy[:, 1:self.NY] += - self.dt / self.density / self.dx * (self.P[:, 1:self.NY] - self.P[:, 0:self.NY - 1])

        self.Vx[1:self.NX, :] += - self.dt / self.density[1:self.NX, :] / self.dx * (self.P[1:self.NX, :] - self.P[0:self.NX - 1, :])
        self.Vy[:, 1:self.NY] += - self.dt / self.density[:, 1:self.NY] / self.dx * (self.P[:, 1:self.NY] - self.P[:, 0:self.NY - 1])

        # Sound pressure update

        A = - (self.kappa * self.dt / self.dx)
        B = (self.Vx[1:self.NX + 1] - self.Vx[0:self.NX, :])
        C = (self.Vy[:, 1:self.NY + 1] - self.Vy[:, 0:self.NY])

        # self.P[0:self.NX, 0:self.NY] += A * (B + C)
        # self.P[:, :] += A * (B + C)

        MY_DUMMY_COEFF = 0.05

        self.P += A * (B + C) * MY_DUMMY_COEFF

        # Prepare initial waveform (Sine wave × 1 wave with window)
        if self.n < (1.0 / self.freq) / self.dt:
            sig = (1.0 - np.cos(2.0 * np.pi * self.freq * self.n * self.dt)) / 2.0 * np.sin(2.0 * np.pi * self.freq * self.n * self.dt)
            # sound source
            # self.P[int(self.NX / 4), int(self.NY / 3)] = sig
            # self.P[220, 160] = sig
            # self.P[410, 350] = sig
            self.P[310, 285] = sig

            print(f'{time.time()} still waving')

        self.P[self.density < 0.1] = 0
        # self.P[self.density < 0.01] = 0

        # borders
        self.P[ 0,  :] = 0
        self.P[-1,  :] = 0
        self.P[ :,  0] = 0
        self.P[ :, -1] = 0

        if self.n % 50 == 0:
            print(f'mean pressure: {self.P.mean()}')
        self.img.setImage(self.P, opacity=0.5)
        self.n += 1


if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec())
