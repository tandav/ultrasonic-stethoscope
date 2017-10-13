from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
from scipy.fftpack import fft
from scipy.signal import decimate
from pathlib import Path
import pyqtgraph as pg
import numpy as np
import sys
import time
import threading
import serial
import serial.tools.list_ports

class AppGUI(QtGui.QWidget):
    def __init__(self, plot_points_x, plot_points_y=256, signal_source='usb'):
        super(AppGUI, self).__init__()
        self.rate = 1
        # self.plot_points = plotpoints
        self.plot_points_y = plot_points_y
        self.plot_points_x = plot_points_x
        self.img_array = np.zeros((self.plot_points_x, self.plot_points_y)) # rename to (plot_width, plot_height)

        self.init_ui()
        self.qt_connections()

        # self.hann_win = np.hanning(NFFT)
        self.hann_win = np.blackman(NFFT)

        self.avg_sum = 0
        self.avg_iters = 0

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot) # updateplot on each timertick
        self.updateplot()
        self.timer.start(0) # Timer tick. Set 0 to update as fast as possible

    def init_ui(self):
        global record_name, NFFT, chunkSize, overlap
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.setWindowTitle('Signal from stethoscope')
        self.layout = QtGui.QVBoxLayout()

        self.fft_slider_box = QtGui.QHBoxLayout()
        self.fft_chunks_slider = QtGui.QSlider()
        self.fft_chunks_slider.setOrientation(QtCore.Qt.Horizontal)
        self.fft_chunks_slider.setRange(1, 512) # max is ser_reader_thread.chunks
        self.fft_chunks_slider.setValue(8)
        # self.fft_chunks_slider.setValue(128)
        NFFT = self.fft_chunks_slider.value() * chunkSize
        self.fft_chunks_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.fft_chunks_slider.setTickInterval(1)
        self.fft_slider_label = QtGui.QLabel('FFT window: {}'.format(NFFT))
        self.fft_slider_box.addWidget(self.fft_slider_label)
        self.fft_slider_box.addWidget(self.fft_chunks_slider)
        self.layout.addLayout(self.fft_slider_box)

        self.plot_points_x_slider_box = QtGui.QHBoxLayout()
        self.plot_points_x_slider = QtGui.QSlider()
        self.plot_points_x_slider.setOrientation(QtCore.Qt.Horizontal)
        self.plot_points_x_slider.setRange(16, 8192) # max is ser_reader_thread.chunks
        self.plot_points_x_slider.setValue(256)
        self.plot_points_x = self.plot_points_x_slider.value()
        self.fft_chunks_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.plot_points_x_slider.setTickInterval(16)
        self.plot_points_x_slider_label = QtGui.QLabel('plot_points_x: {}'.format(self.plot_points_x))
        self.plot_points_x_slider_box.addWidget(self.plot_points_x_slider_label)
        self.plot_points_x_slider_box.addWidget(self.plot_points_x_slider)
        self.layout.addLayout(self.plot_points_x_slider_box)

        self.plot_points_y_slider_box = QtGui.QHBoxLayout()
        self.plot_points_y_slider = QtGui.QSlider()
        self.plot_points_y_slider.setOrientation(QtCore.Qt.Horizontal)
        self.plot_points_y_slider.setRange(16, 8192) # max is ser_reader_thread.chunks
        self.plot_points_y_slider.setValue(256)
        self.plot_points_y = self.plot_points_y_slider.value()
        self.fft_chunks_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.plot_points_y_slider.setTickInterval(16)
        self.plot_points_y_slider_label = QtGui.QLabel('plot_points_y: {}'.format(self.plot_points_y))
        self.plot_points_y_slider_box.addWidget(self.plot_points_y_slider_label)
        self.plot_points_y_slider_box.addWidget(self.plot_points_y_slider)
        self.layout.addLayout(self.plot_points_y_slider_box)

        self.signal_widget = pg.PlotWidget()
        self.signal_widget.showGrid(x=True, y=True, alpha=0.1)
        self.signal_widget.setYRange(-1, 1)
        self.signal_curve = self.signal_widget.plot(pen='b')

        self.fft_widget = pg.PlotWidget(title='FFT')
        self.fft_widget.showGrid(x=True, y=True, alpha=0.1)
        self.fft_widget.setLogMode(x=True, y=False)
        # self.fft_widget.setYRange(0, 0.1) # w\o np.log(a)
        self.fft_widget.setYRange(-15, 0) # w/ np.log(a)
        self.fft_curve = self.fft_widget.plot(pen='r')

        # self.layout.addWidget(self.signal_widget)
        # self.layout.addWidget(self.fft_widget)  # plot goes on right side, spanning 3 rows

        self.glayout = pg.GraphicsLayoutWidget()
        # self.view = self.glayout.addViewBox(lockAspect=False)
        self.view = self.glayout.addViewBox(lockAspect=True)
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # self.view.setAspectLocked()
        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], [0, 0, 255, 255], [255, 0, 0, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        # set colormap
        self.img.setLookupTable(lut)
        # self.img.setLevels([-140, -50])
        self.img.setLevels([-50, 20])
        self.layout.addWidget(self.glayout)

        self.setLayout(self.layout)
        self.setGeometry(10, 10, 1000, 600)
        self.show()

    def qt_connections(self):
        self.fft_chunks_slider.valueChanged.connect(self.fft_slider_changed)
        self.plot_points_x_slider.valueChanged.connect(self.plot_points_x_slider_changed)
        self.plot_points_y_slider.valueChanged.connect(self.plot_points_y_slider_changed)

    def fft_slider_changed(self):
        global NFFT, chunkSize
        # self.NFFT = self.fft_chunks_slider.value() * self.chunkSize
        # self.fft_slider_label.setText('FFT window: {}'.format(self.NFFT))
        NFFT = self.fft_chunks_slider.value() * chunkSize
        self.fft_slider_label.setText('FFT window: {}'.format(NFFT))
        # self.hann_win = np.hanning(NFFT)
        self.hann_win = np.blackman(NFFT)
        self.avg_sum = 0
        self.avg_iters = 0

    def plot_points_x_slider_changed(self):
        self.plot_points_x = self.plot_points_x_slider.value()
        self.plot_points_x_slider_label.setText('plot_points_x: {}'.format(self.plot_points_x))
        self.img_array = np.zeros((self.plot_points_x, self.plot_points_y)) # rename to (plot_width, plot_height)

    def plot_points_y_slider_changed(self):
        self.plot_points_y = self.plot_points_y_slider.value()
        self.plot_points_y_slider_label.setText('plot_points_y: {}'.format(self.plot_points_y))
        self.img_array = np.zeros((self.plot_points_x, self.plot_points_y)) # rename to (plot_width, plot_height)

    def overlap_slider_slider_changed(self):
        global overlap
        overlap = self.overlap_slider.value()
        self.overlap_slider_label.setText('FFT window overlap: {}'.format(overlap))

    def updateplot(self):
        t0 = time.time()
        global NFFT
        y = np.random.rand(NFFT) + np.hanning(NFFT)


        t = np.linspace(0, (NFFT - 1), NFFT)

        # calculate fft
        a = (fft(y * self.hann_win) / NFFT)[:NFFT//2] # fft + chose only real part

        rate = 44100
        f = np.fft.rfftfreq(NFFT - 1, d=1./rate)
        k = np.exp(t)
        try:
            a = np.abs(a) # magnitude
            # a = np.log(a) # часто ошибка - сделать try, else
            a = 20 * np.log10(a) # часто ошибка - сделать try, else
        except Exception as e:
            print('log(0) error', e)

        # spectrogram
        self.img_array = np.roll(self.img_array, -1, 0)
        if len(a) > self.plot_points_y:
            self.img_array[-1] = a[:self.plot_points_y]
        else:
            self.plot_points_y = len(a)
            self.img_array = np.zeros((self.plot_points_x, self.plot_points_y)) # rename to (plot_width, plot_height)
            self.img_array[-1] = a
        self.img.setImage(self.img_array, autoLevels=True)

        # n = len(t)
        # t = t.reshape((self.plot_points, n // self.plot_points)).mean(axis=1)
        # y = y.reshape((self.plot_points, n // self.plot_points)).mean(axis=1)

        # self.signal_curve.setData(t, y)
        # self.fft_curve.setData(f, a)

        # time measures
        t1 = time.time()
        self.avg_sum += t1 - t0
        self.avg_iters += 1
        print('avg_dt=', self.avg_sum / self.avg_iters, 'iters=', self.avg_iters)
        # print(t1 - t0)
        # print('>>>>>')



def main():
    # global params
    global gui, chunkSize
    plot_points_x    = 1024//2//2
    k                = 1
    chunkSize        = 1024 // k
    chunks           = 2000 * k
    # init gui
    app = QtGui.QApplication(sys.argv)
    gui = AppGUI(plot_points_x=plot_points_x, signal_source='usb') # create class instance
    gui.read_collected.connect(gui.updateplot)


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
