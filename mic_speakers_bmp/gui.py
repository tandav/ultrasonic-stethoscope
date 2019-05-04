import PyQt5.QtGui
import PyQt5.QtCore
import PyQt5.QtWidgets
import pyqtgraph as pg
import numpy as np
import util
import serial_port


class GUI(PyQt5.QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # self.phase = 0 # todo: del
        # self.freq = 1 # todo: del
        # self.n = 256

        self.n = 32 # number of readings from arduino per screen

        self.cursor = 0

        self.mic  = np.full(self.n * serial_port.mic_chunk_size, np.nan)
        self.bmp0 = np.full(self.n, np.nan)
        self.bmp1 = np.full(self.n, np.nan)
        self.is_tone_playing = None

        self.init_ui()

        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)


    def init_ui(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.layout = PyQt5.QtWidgets.QVBoxLayout()
        # self.layout = PyQt5.QtWidgets.QHBoxLayout()
        # self.left   = PyQt5.QtWidgets.QVBoxLayout()
        # self.right  = PyQt5.QtWidgets.QVBoxLayout()

        self.init_mic()
        self.init_bmp()


        # self.right.addWidget(self.yplot)
        # self.right.addWidget(self.zplot)

        # self.layout.addLayout(self.left)
        # self.layout.addLayout(self.right)

        self.setLayout(self.layout)
        self.setGeometry(100, 100, 1200, 600)


    def init_mic(self):

        self.mic_fft_plot = pg.PlotWidget()
        self.mic_fft_plot.showGrid(x=True, y=True, alpha=0.1)
        self.mic_fft_plot.setLogMode(x=True, y=False)
        self.mic_fft_curve = self.mic_fft_plot.plot(pen='b')

        projections_height = 80
        self.mic_plot = pg.PlotWidget()
        self.mic_plot.showGrid(x=True, y=True, alpha=0.1)
        # self.mic_plot.enableAutoRange()
        self.mic_curve = self.mic_plot.plot(pen='b')
        # self.mic_plot.setFixedSize(500, projections_height)

        self.layout.addWidget(self.mic_fft_plot)
        self.layout.addWidget(self.mic_plot)


    def init_bmp(self):
        self.bmp_plot = pg.PlotWidget()
        self.bmp_plot.showGrid(x=True, y=True, alpha=0.1)
        # self.bmp_plot.enableAutoRange()
        self.bmp0_curve = self.bmp_plot.plot(pen='b')
        self.bmp1_curve = self.bmp_plot.plot(pen='r')
        self.layout.addWidget(self.bmp_plot)



    def update(self):
        bmp0, bmp1, is_tone_playing, mic = serial_port.read_packet()

        self.bmp0[self.cursor] = bmp0
        self.bmp1[self.cursor] = bmp1
        self.is_tone_playing = is_tone_playing


        self.mic[
            self.cursor      * serial_port.mic_chunk_size :
            (self.cursor + 1)* serial_port.mic_chunk_size
        ] = mic

        self.cursor = (self.cursor + 1) % self.n

        # t = np.linspace(0, 10, self.n)
        # mic = np.sin(self.freq * t + self.phase) + 0.1 * np.random.random(self.n)
        #
        # self.phase += 0.01
        # self.freq += 0.05 * np.random.uniform(low=-1, high=1)
        #
        # rate = 44100
        #
        # a = np.fft.rfft(mic * np.hanning(self.n))
        # a = np.abs(a) # magnitude
        # a = 20 * np.log10(a) # часто ошибка - сделать try, else
        #
        #
        # freqs = np.fft.rfftfreq(self.n, d = 1. / rate)
        #
        # self.mic_fft_curve.setData(freqs, a)
        self.bmp0_curve.setData(self.bmp0)
        self.bmp1_curve.setData(self.bmp1)
        self.mic_curve.setData(self.mic)

        #
        # packet = serial_port.read_packet
        #
        # b0 = np.frombuffer(packet[:4], dtype=np.float32)
        # b1 = np.frombuffer(packet[4:8], dtype=np.float32)
        # is_tone_playing = np.frombuffer(packet[8:9], dtype=np.uint8)[0]
        # # assert is_tone_playing == 0 or is_tone_playing == 1, f'error: packet offset, {is_tone_playing}'
        # mic = np.frombuffer(packet[9:], dtype=np.uint16)
        #
        # if not (is_tone_playing == 0 or is_tone_playing == 1):
        #     print(is_tone_playing)
        #






    # def mousePressEvent(self, QMouseEvent):
    #     print(QMouseEvent.pos())

    def mouseMoveEvent(self, QMouseEvent):
        print(QMouseEvent.pos())


