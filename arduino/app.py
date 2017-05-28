import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import time, threading, sys, serial, socket, os
import gzip, shutil

class SerialReader(threading.Thread): # inheritated from Thread
    """ Defines a thread for reading and buffering serial data.
    By default, about 5MSamples are stored in the buffer.
    Data can be retrieved from the buffer by calling get(N)"""
    def __init__(self, port, chunkSize=1024, chunks=5000):
        threading.Thread.__init__(self)
        # circular buffer for storing serial data until it is
        # fetched by the GUI
        self.buffer = np.zeros(chunks*chunkSize, dtype=np.uint16)
        self.chunks = chunks        # number of chunks to store in the buffer
        self.chunkSize = chunkSize  # size of a single chunk (items, not bytes)
        self.ptr = 0                # pointer to most (recently collected buffer index) + 1
        self.port = port            # serial port handle
        self.sps = 0.0              # holds the average sample acquisition rate
        self.exitFlag = False
        self.exitMutex = threading.Lock()
        self.dataMutex = threading.Lock()
        self.values_recorded = 0

    def run(self):
        exitMutex = self.exitMutex
        dataMutex = self.dataMutex
        buffer = self.buffer
        port = self.port
        count = 0
        sps = None
        lastUpdate = time.time()
        # lastUpdate = pg.ptime.time()

        global record_buffer, recording, record_time, values_to_record, rate, t2, time1

        while True:
            # see whether an exit was requested
            with exitMutex:
                if self.exitFlag:
                    port.close()
                    break

            # read one full chunk from the serial port
            data = port.read(self.chunkSize*2)
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
                    record_buffer[self.values_recorded : self.values_recorded + self.chunkSize] = data
                    self.values_recorded += self.chunkSize

                    if self.values_recorded >= values_to_record: # maybe del second condition
                        time1 = time.time()
                        recording = False
                        self.values_recorded = 0
                        values_to_record = 0
                        t2 = threading.Thread(target=send_to_cuda)
                        t2.start()

                # if recording == 2:


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
        data = data.astype(np.float32) * (3.3 / 2**12)
        if downsample > 1:  # if downsampling is requested, average N samples together
            data = data.reshape(num // downsample,downsample).mean(axis=1)
            num = data.shape[0]
            return np.linspace(0, (num-1)*1e-6*downsample, num), data, rate
        else:
            return np.linspace(0, (num-1)*1e-6, num), data, rate

    def exit(self):
        """ Instruct the serial thread to exit."""
        with self.exitMutex:
            self.exitFlag = True


class adc_chart(QtGui.QWidget):
    def __init__(self):
        super(adc_chart, self).__init__()
        self.init_ui()
        self.qt_connections()

        self.plotcurve = pg.PlotCurveItem()
        self.plotwidget.addItem(self.plotcurve)

        self.updateplot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot) # updateplot on each timertick
        self.timer.start(0) # Timer tick. Set 0 to update as fast as possible

    def init_ui(self):
        self.setWindowTitle('Signal from Arduino\'s ADC')
        hbox = QtGui.QVBoxLayout()
        self.setLayout(hbox)

        self.plotwidget = pg.PlotWidget()
        self.plotwidget.getPlotItem().setLabels(left=('ADC Signal', 'V'), bottom=('Time', 's'))
        self.plotwidget.getPlotItem().setYRange(0.0, 3.3)
        hbox.addWidget(self.plotwidget)

        self.record_start_button = QtGui.QPushButton("Record")
        hbox.addWidget(self.record_start_button)

        self.spin = pg.SpinBox(value=1048576, int=True, bounds=[524288, None], suffix=' Values to record', step=524288, decimals=12)
        hbox.addWidget(self.spin)

        self.record_values_button = QtGui.QPushButton("Record Values")
        hbox.addWidget(self.record_values_button)

        self.setGeometry(10, 10, 1000, 600)
        self.show()

    def qt_connections(self):
        self.record_start_button.clicked.connect(self.on_record_start_button_clicked)
        self.record_values_button.clicked.connect(self.on_record_values_button)

    def updateplot(self):
        global thread, recording
        if not recording:
            t,v,r = thread.get(1000*1024, downsample=256)
            self.plotcurve.setData(t, v)
            self.plotwidget.getPlotItem().setTitle('Sample Rate: %0.2f'%r)

    def on_record_start_button_clicked(self):
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

    def on_record_values_button(self):
        global recording, values_to_record, time0, record_buffer
        values_to_record = self.spin.value()
        print(values_to_record)
        record_buffer = np.empty(values_to_record)
        recording = True
        time0 = time.time()

    def closeEvent(self, event):
        global thread
        thread.exit()


def send_to_cuda():
    global recording, record_buffer, record_time, rate, time0, time1

    # Convert array to float and rescale to voltage. Assume 3.3V / 12bits
    record_buffer = record_buffer.astype(np.float32) * (3.3 / 2**12)
    # print(record_buffer)
    # print(len(record_buffer))
    # print(record_buffer.dtype)

    record_time = np.float32(time1 - time0)
    rate = np.float32(len(record_buffer) / record_time)
    record_buffer = np.append(record_buffer, [record_time, rate])

    # record_buffer = np.append(record_buffer, [record_time, rate])
    # record_buffer = np.append(record_buffer, record_time)
    # record_buffer = np.append(record_buffer, rate)
    # print(len(record_buffer))


    # time_rate = np.array([record_time, rate])

    # print('record time:', record_time, 's', 'rate', rate)
    sys.stdout.write('record time: ' + str(record_time) + 's\t' + 'rate: ' + str(rate) + 'sps\n')


    # sys.stdout.write('start write to file ' + str(len(record_buffer) - 2) + ' values...') # - 2 cause last 2 values are not values of signal but record time and rate
    sys.stdout.write('start write to file ' + str(len(record_buffer)) + ' values...')
    sys.stdout.flush()
    with open('signal.dat', 'w') as f:
        record_buffer.tofile(f)

    # with open('time_rate.dat', 'w') as f:
        # time_rate.tofile(f)
    filesize = os.stat('signal.dat').st_size
    print(" done (", filesize, ' bytes)', sep='')

    # sys.stdout.write('data compression: ' + str(filesize / 1000000) + 'MB...')
    # sys.stdout.flush()

    # with open('signal.dat', 'rb') as f_in, gzip.open('signal.dat.gz', 'wb') as f_out:
    #     shutil.copyfileobj(f_in, f_out)
    # gzfilesize = os.stat('signal.dat.gz').st_size
    # print(' done. File reduced to ', gzfilesize / 1000000, 'MB (%0.0f' % (gzfilesize/filesize*100), '% of uncompressed)', sep='')

    # print('start sending data to CUDA server...')
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('192.168.1.37', 5005))  # (TCP_IP, TCP_PORT)
    # blocksize = 8192 # or some other size packet you want to transmit. Powers of 2 are good.
    # with open('signal.dat.gz', 'rb') as f:
    #     packet = f.read(blocksize)
    #     i = 0
    #     while packet:
    #         s.send(packet)
    #         packet = f.read(blocksize)
    #         i += 1
    #         if i % 100 == 0:
    #             # print('data send:', f.tell() / filesize, '%')
    #             print('data send: %0.0f' % (f.tell() / gzfilesize * 100), '%')

    # # with open('time_rate.dat', 'rb') as f:
    # #     packet = f.read(blocksize//512)
    # #     while packet:
    # #         s.send(packet)
    # #         packet = f.read(blocksize//512)
    # # print('data send: 100% - success')
    # s.close()
    
    # record_buffer = np.array([], dtype=np.uint16)
    print('session end\n')


def main():
    for i in range(21):
        try:
            ser = serial.Serial('/dev/cu.usbmodem1421')    # Left MacBook USB
            # ser = serial.Serial('/dev/cu.usbmodem1411') # Right MacBook USB
            print('device connected\n')
            break
        except Exception as e:
            if i == 20:
                print('Device not found. Check the connection.')
                sys.exit()
            # sys.stdout.write('\r')
            sys.stdout.write('\rsearching device' + '.'*i + ' ')
            sys.stdout.flush()
            time.sleep(0.1)

    # Create thread to read and buffer serial data.
    global thread
    thread = SerialReader(ser)
    thread.daemon = True # without this line UI freezes when close app window, maybe this is wrong and you can fix freeze at some other place
    thread.start()

    global recording, record_buffer, record_time, rate, values_to_record, time0, time1
    recording        = False
    values_to_record = 0
    record_time      = 0
    rate             = 0
    time0            = 0
    time1            = 0
    # record_buffer = np.array([], dtype=np.uint16)

    app = QtGui.QApplication(sys.argv)
    adc = adc_chart() # create class instance
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
