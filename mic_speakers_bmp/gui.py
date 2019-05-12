import PyQt5.QtGui
import PyQt5.QtCore
import PyQt5.QtWidgets
import pyqtgraph as pg
import numpy as np

import util
# import serial_port
import time
import simple_reader as serial_port


class GUI(PyQt5.QtWidgets.QWidget):
    # bmp_signal = PyQt5.QtCore.pyqtSignal()
    mic_signal = PyQt5.QtCore.pyqtSignal()


    def __init__(self):
        super().__init__()

        self.cursor = 0
        # self.is_tone_playing = None

        self.init_ui()
        # self.bmp_signal.connect(self.bmp_update)
        self.mic_signal.connect(self.mic_update)


        # self.t_start = time.time()
        # self.ar_done = False
        # self.ar_dt = 2


        # self.timer = PyQt5.QtCore.QTimer()
        # self.timer.timeout.connect(self.update)
        # self.timer.start(0)


    def init_ui(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.layout = PyQt5.QtWidgets.QVBoxLayout()
        self.init_mic()
        # self.init_bmp()
        self.autorange_button = PyQt5.QtWidgets.QPushButton('AutoRange')
        self.autorange_button.clicked.connect(self.autorange)
        self.ar_counter = 0

        self.layout.addWidget(self.autorange_button)

        self.setLayout(self.layout)
        self.setGeometry(100, 100, 1200, 600)

    def autorange(self):
        self.fft_plot.autoRange()
        # print(self.fft_plot.viewRange())
        self.mic_plot.plotItem.autoRange()
        # self.bmp_plot.plotItem.autoRange()

    def init_mic(self):


        # self.mic_n =  2 ** 12
        # self.mic_n =  2 ** 12
        # self.mic_n =  2 ** 11
        self.mic_n =  2 ** 10
        # self.mic_n =  2 ** 9
        self.mic = np.full(self.mic_n, np.nan)

        self.mic_cursor = 0


        self.fft_reductor = 0


        self.fft_plot = pg.PlotWidget(disableAutoRange=True)
        self.fft_plot.showGrid(x=True, y=True, alpha=0.15)
        # self.fft_plot.setLogMode(x=True, y=False)
        self.fft_plot.setLogMode(x=True, y=True)
        self.fft_curve = self.fft_plot.plot(pen='b')

        # self.fft_plot.getPlotItem().setXRange(10, 11)
        # self.fft_plot.getPlotItem().setXRange(10, 110)
        # self.fft_plot.setLimits(xMin=10)
        # self.fft_plot.getPlotItem().setYRange(-20, 150)
        self.fft_plot.disableAutoRange()

        projections_height = 80
        self.mic_plot = pg.PlotWidget()
        self.mic_plot.showGrid(x=True, y=True, alpha=0.1)
        self.mic_curve = self.mic_plot.plot(pen='b')
        # self.mic_plot.setFixedSize(500, projections_height)

        self.fft_strip = pg.LinearRegionItem(values=[0, 0], movable=False, pen='r', brush=pg.mkBrush(255, 0, 0, 50))
        self.mic_plot.addItem(self.fft_strip)

        self.layout.addWidget(self.fft_plot)
        self.layout.addWidget(self.mic_plot)


    # def init_bmp(self):
    #
    #
    #     # self.bmp_n = 200
    #     self.bmp_n = 100
    #
    #     self.bmp0 = np.full(self.bmp_n, np.nan)
    #     self.bmp1 = np.full(self.bmp_n, np.nan)
    #
    #     self.bmp_cursor = 0
    #
    #     self.bmp_plot = pg.PlotWidget()
    #     self.bmp_plot.showGrid(x=True, y=True, alpha=0.1)
    #     self.bmp_plot.plotItem.disableAutoRange()
    #     self.bmp0_curve = self.bmp_plot.plot(pen='b')
    #     self.bmp1_curve = self.bmp_plot.plot(pen='r')
    #     self.layout.addWidget(self.bmp_plot)
    #
    #
    # @PyQt5.QtCore.pyqtSlot()
    # def bmp_update(self):
    #     bmp0, bmp1 = serial_port.get_bmp()
    #
    #     self.bmp0[self.bmp_cursor] = bmp0
    #     self.bmp1[self.bmp_cursor] = bmp1
    #
    #     self.bmp0_curve.setData(self.bmp0)
    #     self.bmp1_curve.setData(self.bmp1)
    #
    #     self.bmp_cursor += 1
    #     if self.bmp_cursor == self.bmp_n:
    #         self.bmp0[:] = np.nan
    #         self.bmp1[:] = np.nan
    #         self.bmp_cursor = 0

    @PyQt5.QtCore.pyqtSlot()
    def mic_update(self):

        # if not self.ar_done and time.time() - self.t_start > self.ar_dt:
        # if not self.ar_done and time.time() - self.t_start > self.ar_dt:
        #     print(f'autorange after {self.ar_dt} seconds')
        #     self.autorange()
        #     self.ar_done = True


        self.ar_counter += 1
        if self.ar_counter % 50 == 0:
        # if self.ar_counter % 25 == 0:
            self.autorange()
            self.ar_counter = 0

        # mic_raw, mic_new, rate = serial_port.get_mic(self.nfft) # with overlap (running window for STFT)
        # mic_raw, rate, bmp0, bmp1 = serial_port.get_mic(self.nfft)
        mic, fft_f, fft_a, rate = serial_port.get_mic()

        self.mic[self.mic_cursor : self.mic_cursor + len(mic)] = mic
        self.mic_curve.setData(self.mic)

        # if self.fft_reductor == 1:
        #     self.fft_reductor = 0

        # print(fft_f)
        self.fft_curve.setData(fft_f, fft_a)
        # self.fft_curve.setData(fft_a)

        # print(rate)
        # mic = mic_raw[:-serial_port.mic_un] # only new points
        # mic = mic_raw[:-serial_port.mic_un // serial_port.downsampling] # only new points

        # pp = self.mic_n // (2**7)

        # mic = mic_new.reshape(pp , len(mic_new) // pp).mean(axis=1)
        # print(len(mic))

        # self.mic[self.mic_cursor : self.mic_cursor + len(mic)] = mic
        # self.mic_curve.setData(self.mic)


        # if self.fft_reductor == 4:
        #     self.fft_strip.setRegion([self.mic_cursor - 100, self.mic_cursor])
        #
        #     self.fft_reductor = 0
        #     f = scipy.fftpack.rfftfreq(self.nfft, d=1./rate)
        #     a = scipy.fftpack.rfft(mic_raw * scipy.signal.hanning(self.nfft))
        #     a = np.abs(a) # magnitude
        #     a = 20 * np.log10(a) # часто ошибка - сделать try, else
        #
        #
        #     fft_pp = 2 ** 10
        #
        #     f_for_plot = f[::self.nfft // fft_pp]
        #     a_for_plot = a[::self.nfft // fft_pp]
        #     print(len(a), len(a_for_plot))
            # self.fft_curve.setData(f_for_plot, a_for_plot)
            # self.fft_curve.setData(a_for_plot)
            # self.fft_curve.setData(np.random.random(1024))


        # self.fft_reductor += 1

        self.mic_plot.setTitle(f'Sample Rate: {rate/1000:0.2f} kHz')

        self.mic_cursor += len(mic)


        if self.mic_cursor == self.mic_n:
            self.mic[:] = np.nan
            self.mic_cursor = 0


    def closeEvent(self, event):
        serial_port.stop_flag = True


