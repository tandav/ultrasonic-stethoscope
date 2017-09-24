from pyqtgraph.Qt import QtCore, QtGui
from scipy.fftpack import fft
from pathlib import Path
import pyqtgraph as pg
import numpy as np
import time
import threading
import sys
import serial
import serial.tools.list_ports
import socket
import os
import gzip
import shutil
import argparse
import generator
import pickle

class SerialReader(threading.Thread):  # inheritated from Thread
    """ Defines a thread for reading and buffering serial data.
    By default, about 5MSamples are stored in the buffer.
    Data can be retrieved from the buffer by calling get(N)"""
    def __init__(self, signal, chunkSize=1024, chunks=5000):
        threading.Thread.__init__(self)
        # circular buffer for storing serial data until it is
        # fetched by the GUI
        self.buffer = np.zeros(chunks*chunkSize, dtype=np.uint16)
        self.chunks = chunks        # number of chunks to store in the buffer
        self.chunkSize = chunkSize  # size of a single chunk (items, not bytes)
        self.ptr = 0                # pointer to most (recently collected buffer index) + 1
        # self.port = port            # serial port handle
        self.port = self.find_device_and_return_port()           # serial port handle
        self.sps = 0.0              # holds the average sample acquisition rate
        self.exitFlag = False
        self.exitMutex = threading.Lock()
        self.dataMutex = threading.Lock()
        self.values_recorded = 0
        self.signal = signal


    def find_device_and_return_port(self):
        for i in range(61):
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                if 'Arduino' in port.description: 
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

    def run(self):
        exitMutex = self.exitMutex
        dataMutex = self.dataMutex
        buffer = self.buffer
        port = self.port
        count = 0
        sps = None
        lastUpdate = time.time()
        # lastUpdate = pg.ptime.time()

        global record_buffer, recording, values_to_record, t2, record_end_time, NFFT, gui, downsample

        while True:
            # see whether an exit was requested
            with exitMutex:
                if self.exitFlag:
                    port.close()
                    break

            # read one full chunk from the serial port
            data = port.read(self.chunkSize*2) # *2 probably because of datatypes/bytes/things like that
            # convert data to 16bit int numpy array
            data = np.fromstring(data, dtype=np.uint16)

            # keep track of the acquisition rate in samples-per-second
            count += self.chunkSize
            # now = pg.ptime.time()
            now = time.time()

            dt = now-lastUpdate
            if dt > 1.0:
                # sps is an exponential average of the running sample rate measurement
                if sps is None:
                    sps = count / dt
                else:
                    sps = sps * 0.9 + (count / dt) * 0.1
                count = 0
                lastUpdate = now

            # write the new chunk into the circular buffer
            # and update the buffer pointer
            with dataMutex:
                buffer[self.ptr:self.ptr+self.chunkSize] = data
                self.ptr = (self.ptr + self.chunkSize) % buffer.shape[0]

                if sps is not None:
                    self.sps = sps

                # if self.ptr % NFFT// 2 == 0: # //2 because fft windows are overlapping at the half of NFFT
                #     self.signal.emit()

                if recording:
                    self.signal.emit()
                    # print(self.values_recorded -self.values_recorded + self.chunkSize, record_buffer.shape, data.shape)
                    record_buffer[self.values_recorded : self.values_recorded + self.chunkSize] = data
                    self.values_recorded += self.chunkSize

                    if self.values_recorded >= values_to_record: # maybe del second condition
                        record_end_time = time.time()
                        recording = False
                        self.values_recorded = 0
                        values_to_record = 0
                        t2 = threading.Thread(target=send_to_cuda)
                        t2.start()
                
                # elif self.ptr % NFFT // 2 == 0: # //2 because fft windows are overlapping at the half of NFFT
                elif self.ptr % (NFFT * downsample) // 2 == 0: # //2 because fft windows are overlapping at the half of NFFT
                    self.signal.emit()

    def get(self, num):
        """ Return a tuple (time_values, voltage_values, rate)
          - voltage_values will contain the *num* most recently-collected samples
            as a 32bit float array.
          - time_values assumes samples are collected at 1MS/s
          - rate is the running average sample rate.
        """
        with self.dataMutex:  # lock the buffer and copy the requested data out
            ptr = self.ptr
            if ptr-num < 0:
                data = np.empty(num, dtype=np.uint16)
                data[:num-ptr] = self.buffer[ptr-num:] # last N=ptr values of the buffer
                data[num-ptr:] = self.buffer[:ptr]
            else:
                data = self.buffer[self.ptr-num:self.ptr].copy()
            rate = self.sps

        # Convert array to float and rescale to voltage.
        # Assume 3.3V / 12bits
        # (we need calibration data to do a better job on this)
        data = data.astype(np.float32) * (3.3 / 2**12) * 2 / 3.3 - 1 # TODO normalise here to [-1, 1]
        return np.linspace(0, (num-1)*1e-6, num), data, rate

    def exit(self):
        """ Instruct the serial thread to exit."""
        with self.exitMutex:
            self.exitFlag = True


class AppGUI(QtGui.QWidget):
    read_collected = QtCore.pyqtSignal()
    def __init__(self, plot_points_x, plot_points_y=256, signal_source='usb'):
        super(AppGUI, self).__init__()
        self.rate = 1
        # self.plot_points = plotpoints
        self.plot_points_y = plot_points_y
        self.plot_points_x = plot_points_x
        self.img_array = np.zeros((self.plot_points_y, self.plot_points_x)) # rename to (plot_width, plot_height)

        self.init_ui()
        self.qt_connections()

        self.hann_win = np.hanning(NFFT)

        self.avg_sum = 0
        self.avg_iters = 0
        # self.timer = pg.QtCore.QTimer()
        # if signal_source == 'usb':
        #     self.timer.timeout.connect(self.updateplot) # updateplot on each timertick
        #     self.updateplot()
        # elif signal_source == 'virtual_generator':
        #     self.timer.timeout.connect(self.updateplot_virtual_generator) # updateplot on each timertick
        #     self.updateplot_virtual_generator()
        # else:
        #     print('no signal source')
        # self.timer.start(0) # Timer tick. Set 0 to update as fast as possible

    def init_ui(self):
        global record_name, NFFT, chunkSize
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.setWindowTitle('Signal from stethoscope')
        self.layout = QtGui.QVBoxLayout()

        self.fft_slider_box = QtGui.QHBoxLayout()
        self.fft_chunks_slider = QtGui.QSlider()
        self.fft_chunks_slider.setOrientation(QtCore.Qt.Horizontal)
        self.fft_chunks_slider.setRange(1, 128) # max is ser_reader_thread.chunks
        self.fft_chunks_slider.setValue(8)
        # self.fft_chunks_slider.setValue(128)
        NFFT = self.fft_chunks_slider.value() * chunkSize
        self.fft_chunks_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.fft_chunks_slider.setTickInterval(1)
        self.fft_slider_label = QtGui.QLabel('FFT window: {}'.format(self.fft_chunks_slider.value() * chunkSize))
        self.fft_slider_box.addWidget(self.fft_slider_label)
        self.fft_slider_box.addWidget(self.fft_chunks_slider)
        self.layout.addLayout(self.fft_slider_box)

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

        self.layout.addWidget(self.signal_widget)
        # self.layout.addWidget(self.fft_widget)  # plot goes on right side, spanning 3 rows

        self.record_box = QtGui.QHBoxLayout()
        self.spin = pg.SpinBox( value=chunkSize*1300, # if change, change also in suffix 
                                int=True,
                                bounds=[chunkSize*100, None],
                                suffix=' Values to record ({:.2f} seconds)'.format(chunkSize * 1300 / 666000),
                                step=chunkSize*100, decimals=12, siPrefix=True)
        self.record_box.addWidget(self.spin)
        self.record_name_textbox = QtGui.QLineEdit(self)
        self.record_name_textbox.setText('lungs')
        record_name = self.record_name_textbox.text()
        self.record_box.addWidget(self.record_name_textbox)
        self.record_values_button = QtGui.QPushButton('Record Values')
        self.record_box.addWidget(self.record_values_button)
        self.layout.addLayout(self.record_box)

        self.progress = QtGui.QProgressBar()
        self.layout.addWidget(self.progress)

        self.glayout = pg.GraphicsLayoutWidget()
        self.view = self.glayout.addViewBox()
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
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
        self.record_values_button.clicked.connect(self.record_values_button_clicked)
        self.spin.valueChanged.connect(self.spinbox_value_changed)
        self.fft_chunks_slider.valueChanged.connect(self.fft_slider_changed)
        self.record_name_textbox.textChanged.connect(self.record_name_changed)

    def fft_slider_changed(self):
        global NFFT, chunkSize
        # self.NFFT = self.fft_chunks_slider.value() * self.chunkSize
        # self.fft_slider_label.setText('FFT window: {}'.format(self.NFFT))
        NFFT = self.fft_chunks_slider.value() * chunkSize
        self.fft_slider_label.setText('FFT window: {}'.format(NFFT))
        self.hann_win = np.hanning(NFFT)
        self.avg_sum = 0
        self.avg_iters = 0

    def record_name_changed(self):
        global record_name
        record_name = self.record_name_textbox.text()

    def updateplot(self):
        t0 = time.time()
        global ser_reader_thread, recording, values_to_record, record_start_time, NFFT, downsample


        while recording:
            # while 
            # old
            self.progress.setValue(100 / (values_to_record / ser_reader_thread.sps) * (time.time() - record_start_time)) # map recorded/to_record => 0% - 100%
            time.sleep(0.3)
        else:
            self.progress.setValue(0)
            # n = ser_reader_thread.chunks * ser_reader_thread.chunkSize # get whole buffer from SerialReader
            # t, y, rate = ser_reader_thread.get(num=n) # MAX num=chunks*chunkSize (in SerialReader class)
            t, y, rate = ser_reader_thread.get(num=NFFT * downsample) # MAX num=chunks*chunkSize (in SerialReader class)

            if rate > 0:
                # downsampling (cutting high ultrasonics)
                n = len(y)
                y = y.reshape(n // downsample, downsample).mean(axis=1)
                n = len(y)
                t =  np.linspace(0, (n-1)*1e-6*downsample, n)
                rate /= downsample

                # # calculate fft
                # f = np.fft.rfftfreq(n - 1, d=1./rate)
                a = fft(y*np.hanning(n))[:n//2] # fft + chose only real part

                # calculate fft
                # f = np.fft.rfftfreq(NFFT - 1, d=1./rate)
                # a = fft(y * self.hann_win)[:NFFT//2] # fft + chose only real part
                
                # print(np.hanning(NFFT).shape, NFFT, y.shape)
                # sometimes there is a zero in the end of array
                # a = a[:-1] 
                # f = f[:-1]
                
                try:
                    a = np.abs(a) # magnitude
                    # a = np.log(a) # часто ошибка - сделать try, else
                    a = 20 * np.log10(a) # часто ошибка - сделать try, else
                except Exception as e:
                    print('log(0) error',e )

                # spectrogram
                self.img_array = np.roll(self.img_array, -1, 0)
                # self.img_array[-1:] = a
                self.img_array[-1:] = a[:self.plot_points_y]
                # self.img.setImage(self.img_array, autoLevels=False)
                self.img.setImage(self.img_array, autoLevels=True)
                # imadje = np.arange(10)*np.array([[1], [1], [1]]) + np.random.rand(3, 1)
                # self.img.setImage(imadje, autoLevels=True)
                # print(imadje)


                # print(self.img_array[0][0], self.img_array[0][-1])
                # n = len(t)
                # t = t.reshape((self.plot_points, n // self.plot_points)).mean(axis=1)
                # y = y.reshape((self.plot_points, n // self.plot_points)).mean(axis=1)

                self.signal_curve.setData(t, y)
                self.signal_widget.getPlotItem().setTitle('Sample Rate: %0.2f'%rate)
                # self.fft_curve.setData(f, a)
        t1 = time.time()
        self.avg_sum += t1 - t0
        self.avg_iters += 1
        print(self.avg_sum / self.avg_iters)
        # print(t1 - t0)

    def updateplot_virtual_generator(self):
        global ser_reader_thread, recording, values_to_record, record_start_time
        t, y, rate = generator.signal(freq=4000, rate=65536, seconds=1)

        if recording:
            self.progress.setValue(100 / (values_to_record / rate) * (time.time() - record_start_time)) # map recorded/to_record => 0% - 100%
        else:
            self.progress.setValue(0)

            if rate > 0:
                # calculate fft
                f = np.fft.rfftfreq(NFFT - 1, d=1./rate)
                a = fft(y[-NFFT:])[:NFFT//2] # fft + chose only real part


                a = np.abs(a / NFFT) # normalisation
                a = np.log(a)

                self.signal_curve.setData(t, y)
                self.signal_widget.getPlotItem().setTitle('Sample Rate: %0.2f'%rate)
                self.fft_curve.setData(f, a)

                # spectrogram
                self.img_array = np.roll(self.img_array, -1, 0)
                self.img_array[-1:] = a[:self.plot_points]
                # self.img.setImage(self.img_array, autoLevels=False)
                self.img.setImage(self.img_array, autoLevels=True)

    def spinbox_value_changed(self):
        self.spin.setSuffix(' Values to record' + ' ({:.2f} seconds)'.format(self.spin.value() / ser_reader_thread.sps))

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_Space:
            #here accept the event and do something
            self.record_values_button_clicked()
            event.accept()
        else:
            event.ignore()

    def record_values_button_clicked(self):
        global recording, values_to_record, record_start_time, record_buffer
        values_to_record = self.spin.value()
        record_buffer = np.empty(values_to_record)
        recording = True
        record_start_time = time.time()

    def closeEvent(self, event):
        global ser_reader_thread
        ser_reader_thread.exit()


def write_to_file(arr, ext, gzip=False):
        global file_index, record_name
        sys.stdout.write('start write to file ' + str(len(arr)) + ' values...')
        sys.stdout.flush()


        data_dir = 'child-hospital-n1-2/'
        # fileprefix = 'fio-disease-'
        fileprefix = record_name + '-'

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        filename = data_dir + fileprefix + str(file_index) + '.' + ext


        if ext == 'dat':
            with open(filename, 'w') as f:
                arr.tofile(f)
        elif ext == 'txt':
            np.savetxt(filename, arr)
        else:
            print('wrong file extension')

        file_index += 1

        filesize = os.stat(filename).st_size
        print(" done (", filesize, ' bytes)', sep='')
        print(filename)
        if gzip:
            sys.stdout.write('gzip data compression: ' + str(filesize / 1000000) + 'MB...')
            sys.stdout.flush()

            with open(filename, 'rb') as f_in, gzip.open(filename + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            gzfilesize = os.stat(filename + '.gz').st_size
            print(' done. File reduced to ', gzfilesize / 1000000, 'MB (%0.0f' % (gzfilesize/filesize*100), '% of uncompressed)', sep='')


def send_to_cuda():
        global record_buffer, record_time, rate, record_start_time, record_end_time
        
        # old 
        # record_buffer = record_buffer.astype(np.float32) * (3.3 / 2**12) # Convert array to float and rescale to voltage. Assume 3.3V / 12bits
        # new: add rescale to [-1, 1]
        record_buffer = record_buffer.astype(np.float32) * (3.3 / 2**12) * 2 / 3.3 - 1# Convert array to float and rescale to voltage. Assume 3.3V / 12bits
        

        n = len(record_buffer) # length of the signal

        record_time = np.float32(record_end_time - record_start_time)
        rate = np.float32(n / record_time)
        sys.stdout.write('record time: ' + str(record_time) + 's\t' + 'rate: ' + str(rate) + 'sps   ' + str(len(record_buffer)) + ' values\n')

        # calc_fft_localy(record_buffer, n, record_time, rate)
        record_buffer = np.insert(record_buffer, 0, [record_time, rate]) # first two entries in file are record_time and rate
        # write_to_file(record_buffer, compression=False)
        write_to_file(record_buffer, 'dat', gzip=False)

        # print('start sending data to CUDA server...')
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect(('192.168.119.170', 5005))  # (TCP_IP, TCP_PORT)
        # blocksize = 8192 # or some other size packet you want to transmit. Powers of 2 are good.
        # with open('signal.dat.gz', 'rb') as f:
        #     packet = f.read(blocksize)
        #     i = 0
        #     while packet:
        #         s.send(packet)
        #         packet = f.read(blocksize)
        #         i += 1
        #         if i % 100 == 0:
        #             print('data send: %0.0f' % (f.tell() / gzfilesize * 100), '%')
        # print('data send: 100% - success')
        # s.close()

        print('session end\n')


def main():
    # argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--plotpoints', help='number of points to draw')
    parser.add_argument('-g', '--generator', action='store_true' ,help='gets signal for plots from virtual generator')
    args = parser.parse_args()

    # global params
    global recording, values_to_record, file_index, gui, ser_reader_thread, chunkSize, downsample
    recording        = False
    values_to_record = 0
    file_index       = 0

    downsample = 16

    # init gui
    app = QtGui.QApplication(sys.argv)
    if args.generator:
        gui = AppGUI(plotpoints=2048, chunkSize=1024, signal_source='virtual_generator') # create class instance
    else:
        # serialreader params
        k = 1
        chunkSize = 1024 // k
        chunks    = 2000 * k

        plotpoints = 1024//2//2
        if args.plotpoints:
            if (chunkSize * chunks) % int(args.plotpoints) == 0:
                plotpoints = int(args.plotpoints)
            else:
                print('chunkSize * chunks \% plotpoints != 0. chunkSize={0}, chunks={1}. plotpoints was set to {2} (default)'.format(chunkSize, chunks, plotpoints))
        gui = AppGUI(plot_points_x=plotpoints, signal_source='usb') # create class instance

    gui.read_collected.connect(gui.updateplot)
    ser_reader_thread           = SerialReader(signal=gui.read_collected, chunkSize=chunkSize, chunks=chunks)
    ser_reader_thread.daemon    = True # without this line UI freezes when close app window, maybe this is wrong and you can fix freeze at some other place
    ser_reader_thread.start()


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
