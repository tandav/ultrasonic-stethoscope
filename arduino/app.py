from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
from scipy.fftpack import fft
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

class SerialReader(threading.Thread):  # inheritated from Thread
    """ Defines a thread for reading and buffering serial data.
    By default, about 5MSamples are stored in the buffer.
    Data can be retrieved from the buffer by calling get(N)"""
    def __init__(self, chunkSize=1024, chunks=5000):
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

    def find_device_and_return_port(self):
        for i in range(61):
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                if 'Arduino' in port.description: 
                    # try / except
                    ser = serial.Serial(port.device)
                    print('device connected\n')
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

        global record_buffer, recording, values_to_record, t2, time1

        while True:
            # see whether an exit was requested
            with exitMutex:
                if self.exitFlag:
                    port.close()
                    break

            # read one full chunk from the serial port
            data = port.read(self.chunkSize*2) # *2 probably becaus of datatypes/bytes/things like that
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

                if recording:
                    # print(self.values_recorded -self.values_recorded + self.chunkSize, record_buffer.shape, data.shape)
                    record_buffer[self.values_recorded : self.values_recorded + self.chunkSize] = data
                    self.values_recorded += self.chunkSize

                    if self.values_recorded >= values_to_record: # maybe del second condition
                        time1 = time.time()
                        recording = False
                        self.values_recorded = 0
                        values_to_record = 0
                        t2 = threading.Thread(target=send_to_cuda)
                        t2.start()

    def get(self, num, downsample=1):
        """ Return a tuple (time_values, voltage_values, rate)
          - voltage_values will contain the *num* most recently-collected samples
            as a 32bit float array.
          - time_values assumes samples are collected at 1MS/s
          - rate is the running average sample rate.
        If *downsample* is > 1, then the number of values returned will be
        reduced by averaging that number of consecutive samples together. In
        this case, the voltage array will be returned as 32bit float.
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
        data = data.astype(np.float32) * (3.3 / 2**12) # TODO normalise here to [-1, 1]
        if downsample > 1:  # if downsampling is requested, average N samples together
            # data = data.reshape(num // downsample,downsample).mean(axis=1)
            data = data.reshape((num // downsample, downsample)).mean(axis=1)
            num = data.shape[0]
            return np.linspace(0, (num-1)*1e-6*downsample, num), data, rate
        else:
            return np.linspace(0, (num-1)*1e-6, num), data, rate

    def exit(self):
        """ Instruct the serial thread to exit."""
        with self.exitMutex:
            self.exitFlag = True


class AppGUI(QtGui.QWidget):
    def __init__(self, chunkSize, downsampling):
        super(AppGUI, self).__init__()

        self.chunkSize = chunkSize
        self.rate = 0
        self.signal_plot_points = 1000 * chunkSize
        self.signal_values_t = np.zeros(self.signal_plot_points)
        self.signal_values_y = np.zeros(self.signal_plot_points)
        # self.signal_values_v = np.zeros(self.chunkSize * 1000)
        # self.ptr = 0

        self.init_ui()
        self.qt_connections()

        self.updateplot()
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot) # updateplot on each timertick
        self.timer.start(0) # Timer tick. Set 0 to update as fast as possible

    def init_ui(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.setWindowTitle('Signal from Arduino\'s ADC')


        self.signal_widget = pg.PlotWidget()
        self.signal_widget.showGrid(x=True, y=True, alpha=0.12)
        self.signal_widget.setYRange(0, 3.3)
        self.signal_curve = self.signal_widget.plot(pen='b')


        self.fft_widget = pg.PlotWidget(title='FFT')
        self.fft_widget.showGrid(x=True, y=True, alpha=0.12)
        self.fft_widget.setLogMode(x=True, y=False)
        # self.fft_widget.setYRange(0, 0.1) # w\o np.log(a)
        self.fft_widget.setYRange(-15, 0) # w/ np.log(a)
        self.fft_curve = self.fft_widget.plot(pen='r')


        self.hbox = QtGui.QVBoxLayout()
        self.setLayout(self.hbox)
        
        self.progress = QtGui.QProgressBar()
        self.hbox.addWidget(self.progress)

        self.hbox.addWidget(self.signal_widget)
        self.hbox.addWidget(self.fft_widget)  # plot goes on right side, spanning 3 rows

        self.record_start_button = QtGui.QPushButton('Record')
        self.hbox.addWidget(self.record_start_button)

        self.spin = pg.SpinBox(value=self.chunkSize*100, int=True, bounds=[self.chunkSize*100, None], suffix=' Values to record', step=self.chunkSize*100, decimals=12, siPrefix=True)
        self.hbox.addWidget(self.spin)

        self.seconds_to_record_label = QtGui.QLabel('about {:.2f} seconds'.format(self.spin.value()/666000))
        self.hbox.addWidget(self.seconds_to_record_label)

        self.record_values_button = QtGui.QPushButton('Record Values')
        self.hbox.addWidget(self.record_values_button)

        self.setGeometry(10, 10, 1000, 600)
        self.show()

    def qt_connections(self):
        self.record_start_button.clicked.connect(self.record_start_button_clicked)
        self.record_values_button.clicked.connect(self.record_values_button_clicked)
        self.spin.valueChanged.connect(self.spinbox_value_changed)

    def updateplot(self):
        global thread, recording, values_to_record, time0
        
        if not recording:
            self.progress.setValue(0)
            self
            # t, v, rate, f, a = get_data_to_draw(values=300*self.chunkSize, downsampling=self.downsampling) # downsampling = 100
            # t, v, rate, f, a = get_data_to_draw(values=600*self.chunkSize, downsampling=self.downsampling) # downsampling = 300
            # t, v, rate, f, a = self.get_data_to_draw(values=1000*self.chunkSize, downsampling=self.downsampling) # downsampling = 200!!!!!!
            # t, v, rate, f, a = self.get_data_to_draw(values=self.chunkSize, downsampling=1) # downsampling = 500
            
            t, y, rate = thread.get(num=100*self.chunkSize, downsample=1)
            n = len(t)
            self.rate = rate

            temp_signal_values_t = self.signal_values_t
            self.signal_values_t[:-n] = temp_signal_values_t[n:]
            self.signal_values_t[-n:] = t

            temp_signal_values_y = self.signal_values_y
            self.signal_values_y[:-n] = temp_signal_values_y[n:]
            self.signal_values_y[-n:] = y

            
            if rate == 0:  # occurs on start
                f = np.arange(n//2)
                a = np.arange(n//2)
                return t, y, rate, f, a
            else:  # calculate fft
                # # numpy.fft
                # f = np.fft.rfftfreq(n, d=1./rate)
                # a = np.fft.rfft(v)



                # scipy.fftpack
                f = np.fft.rfftfreq(n - 1, d=1./rate)
                a = fft(y)[:n//2] # fft + chose only real part

                # pyFFTW
                # TODO ...

                a = np.abs(a / n) # normalisation
                a = np.log(a)


            # downsample
            # t = t.reshape((n//downsampling, downsampling)).mean(axis=1)
            # v = v.reshape((n//downsampling, downsampling)).mean(axis=1)
            # f = f.reshape((n//2//downsampling, downsampling)).mean(axis=1)
            # a = a.reshape((n//2//downsampling, downsampling)).mean(axis=1)
            # f = f[:n//downsampling]
            # a = a[:n//downsampling]

            # print(t.shape, v.shape, f.shape, a.shape)

            self.signal_curve.setData(t, y)
            self.fft_curve.setData(f, a)
            self.signal_widget.getPlotItem().setTitle('Sample Rate: %0.2f'%rate)
        else:
            self.progress.setValue(100 / (values_to_record / self.rate) * (time.time() - time0))

    def spinbox_value_changed(self):
        self.seconds_to_record_label.setText('about {:.2f} seconds'.format(self.spin.value()/self.rate))
        # self.spin.suffix = ' Values to record (about )' + str(self.spin.value()/666000) + 'seconds'

    def record_start_button_clicked(self):
        global recording
        if recording == 0:
            recording = 1
            self.record_start_button.setText("Stop")
            # print ("Record started...")
            sys.stdout.write('Record start... ')
            sys.stdout.flush()
        elif recording == 1:
            recording = 2
            self.record_start_button.setText("Record")
            sys.stdout.write('\rRecord start... stop\n')

    def record_values_button_clicked(self):
        global recording, values_to_record, time0, record_buffer
        values_to_record = self.spin.value()
        print(values_to_record)
        record_buffer = np.empty(values_to_record)
        recording = True
        time0 = time.time()

    def closeEvent(self, event):
        global thread
        thread.exit()


def write_to_file(arr, ext, gzip=False):
        global file_index
        sys.stdout.write('start write to file ' + str(len(arr)) + ' values...')
        sys.stdout.flush()


        data_dir = 'child-hospital-n1/'
        fileprefix = 'fio-disease-'

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
        global record_buffer, record_time, rate, time0, time1
        
        # old 
        # record_buffer = record_buffer.astype(np.float32) * (3.3 / 2**12) # Convert array to float and rescale to voltage. Assume 3.3V / 12bits
        # new: add rescale to [-1, 1]
        record_buffer = record_buffer.astype(np.float32) * (3.3 / 2**12) * 2 / 3.3 - 1# Convert array to float and rescale to voltage. Assume 3.3V / 12bits
        

        n = len(record_buffer) # length of the signal

        record_time = np.float32(time1 - time0)
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
    parser.add_argument('-d', '--downsample', help='defines how much to reduce plots points')
    args = parser.parse_args()
    if args.downsample:
        print('downsample={}'.format(args.downsample))

    global thread, chunkSize # thread to read and buffer serial data.
    chunkSize        = 1024 # 1000 instead of 1024 because of Vakhtin's CUDA.FFT bugs
    thread           = SerialReader(chunkSize=chunkSize, chunks=5000) # rename it to serialreader or sth like that
    thread.daemon    = True # without this line UI freezes when close app window, maybe this is wrong and you can fix freeze at some other place
    thread.start()

    global recording, values_to_record, file_index
    recording        = False
    values_to_record = 0
    file_index       = 0

    app = QtGui.QApplication(sys.argv)
    gui = AppGUI(chunkSize=chunkSize, downsampling=args.downsample) # create class instance
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
