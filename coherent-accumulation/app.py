from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
from scipy.fftpack import fft
from scipy.io.wavfile import write as write_wav
from scipy.io import wavfile
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('classic')
import pyqtgraph as pg
import numpy as np
import time
import threading
import sys
import serial # TODO: try del
import serial.tools.list_ports
import socket
import signal
import os
import gzip
import shutil


class SerialReader(threading.Thread):
    """ Defines a thread for reading and buffering serial data.
    By default, about 5MSamples are stored in the buffer.
    Data can be retrieved from the buffer by calling get(N)"""
    def __init__(self, data_collected_signal, chunkSize=1024, chunks=5000):
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
        self.data_collected_signal = data_collected_signal

        self.series_n = 10
        self.matrix = np.zeros((self.series_n, self.chunkSize * 64))
        self.tone_playing = False
        self.current_tone_i = 0
        self.out = np.zeros(self.chunkSize * 64)

    def find_device_and_return_port(self):
        for i in range(61):
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                if 'Arduino' in port.description or \
                   'Устройство с последовательным интерфейсом USB' in port.description or \
                   'USB Serial Device' in port.description: 
                # if ('Устройство с последовательным интерфейсом USB') in port.description: 
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
        ptr2 = 0

        global record_buffer, recording, values_to_record, t2, record_end_time, NFFT, gui, overlap

        while True:
            # see whether an exit was requested
            with exitMutex:
                if self.exitFlag:
                    port.close()
                    break

            # read one full chunk from the serial port
            data = port.read(self.chunkSize * 2) # *2 probably because of datatypes/bytes/things like that
            # convert data to 16bit int numpy array TODO: convert here to -1..+1 values, instead voltage 0..3.3




            # dirty hotfix
            if data[:4] == b'\xd2\x02\x96I':
                timings = np.frombuffer(data, dtype=np.uint32)
                print(f'tone_playing {timings[1]} current_tone_i {timings[2]} {timings[2] % self.series_n}')
                self.tone_playing = timings[1] == True
                if self.current_tone_i != timings[2]:
                    self.ptr2 = 0
                self.current_tone_i = timings[2] % self.series_n
            elif data[4:8] == b'\xd2\x02\x96I':
                timings = np.frombuffer(data, dtype=np.uint32)
                print(f'tone_playing {timings[2]} current_tone_i {timings[3]} {timings[3] % self.series_n}')
                self.tone_playing = timings[2] == True
                if self.current_tone_i != timings[3]:
                    self.ptr2 = 0
                self.current_tone_i = timings[3] % self.series_n
            elif self.tone_playing:
                data = np.frombuffer(data, dtype=np.uint16)

                # keep track of the acquisition rate in samples-per-second
                count += self.chunkSize
                # now = pg.ptime.time()
                now = time.time()

                dt = now - lastUpdate
                if dt > 1.0:
                    # sps is an exponential average of the running sample rate measurement
                    if sps is None:
                        sps = count / dt
                    else:
                        sps = sps * 0.9 + (count / dt) * 0.1
                    count = 0
                    lastUpdate = now
                # print('rate', sps)
                # write the new chunk into the circular buffer
                # and update the buffer pointer
                with dataMutex:
                    if self.current_tone_i == 0 and self.ptr2 == 0: # end of series (start of new series), need to update plot
                        print('fu')
                        self.out = np.mean(self.matrix, axis=0)
                        self.data_collected_signal.emit() # try pass array via signal?
                        self.matrix = np.zeros((self.series_n, self.chunkSize * 64))


                    self.matrix[self.current_tone_i, self.ptr2 : self.ptr2 + self.chunkSize] = data
                    self.ptr2 += self.chunkSize


                    # buffer[self.ptr:self.ptr + self.chunkSize] = data
                    # self.ptr = (self.ptr + self.chunkSize) % buffer.shape[0]
                    # ptr2 += self.chunkSize

                    if sps is not None:
                        self.sps = sps

                    # if ptr2 >= NFFT - overlap:
                        # ptr2 = 0
                        # self.data_collected_signal.emit()

    def get(self):
        """ Return a tuple (time_values, voltage_values, rate)
          - voltage_values will contain the *num* most recently-collected samples
            as a 32bit float array.
          - time_values assumes samples are collected at 1MS/s
          - rate is the running average sample rate.
        """
        # with self.dataMutex:  # lock the buffer and copy the requested data out
        #     ptr = self.ptr
        #     if ptr-num < 0:
        #         data = np.empty(num, dtype=np.uint16)
        #         data[:num-ptr] = self.buffer[ptr-num:] # last N=ptr values of the buffer
        #         data[num-ptr:] = self.buffer[:ptr]
        #     else:
        #         data = self.buffer[self.ptr-num:self.ptr].copy()
        #     rate = self.sps

        # Convert array to float and rescale to voltage.
        # Assume 3.3V / 12bits
        # (we need calibration data to do a better job on this)
        # data = data.astype(np.float32) * (3.3 / 2**12) * 2 / 3.3 - 1

        with self.dataMutex:
            # rate = self.sps
            out = self.out
        return out

    def exit(self):
        """ Instruct the serial thread to exit."""
        with self.exitMutex:
            self.exitFlag = True



class AppGUI(QtGui.QWidget):
    data_collected = QtCore.pyqtSignal()

    def __init__(self):
        super(AppGUI, self).__init__()
        # global NFFT
        
        self.rate = 1


        self.init_ui()
        self.qt_connections()
        
        # self.t = np.linspace(0, (NFFT - 1) * 1e-6, NFFT)
        # self.y = np.zeros(NFFT)
        # self.f = np.zeros(NFFT // 2)
        # self.a = np.zeros(NFFT // 2)
        # self.win = np.hanning(NFFT)

        # self.avg_sum = 0
        # self.avg_iters = 0

    def init_ui(self):
        global record_name, NFFT, chunkSize, overlap
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.setWindowTitle('Signal from stethoscope')
        self.layout = QtGui.QVBoxLayout()


        self.signal_widget = pg.PlotWidget()
        self.signal_widget.showGrid(x=True, y=True, alpha=0.1)
        self.signal_widget.setYRange(-1, 1)
        self.signal_curve = self.signal_widget.plot(pen='b')

        self.fft_widget = pg.PlotWidget(title='FFT')
        self.fft_widget.showGrid(x=True, y=True, alpha=0.1)
        self.fft_widget.setLogMode(x=True, y=False)
        # self.fft_widget.setLogMode(x=False, y=False)
        # self.fft_widget.setYRange(0, 0.1) # w\o np.log(a)
        # self.fft_widget.setYRange(-15, 0) # w/ np.log(a)
        self.fft_curve = self.fft_widget.plot(pen='r')

        self.layout.addWidget(self.signal_widget)
        self.layout.addWidget(self.fft_widget)


        self.setLayout(self.layout)
        self.setGeometry(10, 10, 600, 1000)
        self.show()

    def qt_connections(self):
        self.data_collected.connect(self.updateplot)

    @QtCore.pyqtSlot()
    def updateplot(self):
        print('updateplot')
        y = ser_reader_thread.get()
        n = len(y)
        t = np.arange(n) # temp solution
        # t0 = time.time()
        # global ser_reader_thread, recording, values_to_record, record_start_time, NFFT, big_dt

        # self.t, self.y, self.rate = ser_reader_thread.get(num=NFFT) # MAX num=chunks*chunkSize (in SerialReader class)

        a = (fft(y * np.hanning(n)) / n)[:n//2] # fft + chose only real part

        # # в 2 строчки быстрее чем в одну! я замерял!
        a = np.abs(a) # magnitude
        a = 20 * np.log10(a) # часто ошибка - сделать try, else

        
        f = np.arange(len(a))

        # print('fuck you')
        # pp = 4096*2 # number of points to plot
        # t_for_plot = self.t.reshape(pp, NFFT // pp).mean(axis=1)
        # y_for_plot = self.y.reshape(pp, NFFT // pp).mean(axis=1)

        self.signal_curve.setData(t, y)
        self.fft_curve.setData(f, a)

        # self.signal_widget.getPlotItem().setTitle('Sample Rate: %0.2f'%self.rate)
        # if self.rate > 0:
        #     self.f = np.fft.rfftfreq(NFFT - 1, d = 1. / self.rate)
        #     f_for_plot = self.f.reshape(pp, NFFT // pp // 2).mean(axis=1)
        #     a_for_plot = self.a.reshape(pp, NFFT // pp // 2).mean(axis=1)
        #     self.fft_curve.setData(f_for_plot, a_for_plot)



        # t1 = time.time()
        # self.avg_sum += t1 - t0
        # self.avg_iters += 1
        # # print('avg_dt=', self.avg_sum / self.avg_iters, 'iters=', self.avg_iters)
        # if self.avg_iters % 10 == 0:
        #     # print('avg_dt=', self.avg_sum * 1000 / self.avg_iters, 'iters=', self.avg_iters)
        #     # print('big_dt =', (time.time() - big_dt) * 1000, '\tupdateplot_dt =', (t1 - t0) * 1000)

        #     print('big_dt: {:.3f}ms | updateplot_dt: {:.3f}ms | avg_dt: {:.3f} | iters: {}'.format((time.time() - big_dt) * 1000,
        #                                                               (t1 - t0) * 1000,
        #                                                                self.avg_sum * 1000 / self.avg_iters,
        #                                                                self.avg_iters))
        #     if abs((time.time() - big_dt) - (t1 - t0)) < 0.010:
        #         print('WARNING: too big overlap: {:.3f}ms'.format(abs((time.time() - big_dt) - (t1 - t0)) * 1000))
        # big_dt = time.time()

    # def closeEvent(self, event):
    def closeEvent(self, event):
        global ser_reader_thread
        ser_reader_thread.exit()



def main():
    # globals
    global gui, ser_reader_thread, chunkSize, big_dt
    chunkSize = 256
    chunks    = 2000
    big_dt    = 0

    # init gui
    app = QtGui.QApplication(sys.argv)
    gui = AppGUI() # create class instance

    # init and run serial arduino reader
    ser_reader_thread = SerialReader(data_collected_signal=gui.data_collected, 
                                     chunkSize=chunkSize,
                                     chunks=chunks)
    ser_reader_thread.start()

    # app exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
