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
    def __init__(self, record_ready_signal, chunkSize=1024, chunks=5000):
        threading.Thread.__init__(self)
        # circular buffer for storing serial data until it is
        # fetched by the GUI
        self.buffer = np.zeros(chunks*chunkSize, dtype=np.uint16)
        self.chunks = chunks        # number of chunks to store in the buffer
        self.chunkSize = chunkSize  # size of a single chunk (items, not bytes)
        self.ptr = 0                # pointer to most (recently collected buffer index) + 1
        # self.port = port            # serial port handle
        self.port = self.find_device_and_return_port()           # serial port handle

        self.exitFlag = False
        self.exitMutex = threading.Lock()
        self.dataMutex = threading.Lock()
        self.values_recorded = 0
        self.record_ready_signal = record_ready_signal

        self.series_n = 50
        # self.series_n = 20
        # self.series_n = 4
        self.matrix = np.full((self.series_n, self.chunkSize * 170), 4095/2) # if map -1..1 to 0..4095, then 0 maps to 4095/
        # self.matrix = np.zeros((self.series_n, self.chunkSize * 170))
        # self.matrix = np.zeros((self.series_n, self.chunkSize * 300))
        self.tone_playing = 0 # 0/1 here instead of False/True
        self.current_tone_i = 0
        self.mean = np.zeros(self.matrix.shape[1])
        # self.matrix_out = np.zeros_like(self.matrix)
        
        self.matrix_record = self.matrix.copy()
        
        self.ptr = 0

        self.rate_record = 0
        self.count = 0
        self.record_start_t = 0

        self.record_requested = False
        self.recording = False
        self.recording_start_tone_i = 0

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


        global record_buffer, values_to_record, t2, record_end_time, NFFT, gui, overlap

        while True:
            # see whether an exit was requested
            with exitMutex:
                if self.exitFlag:
                    port.close()
                    break

            # read one full chunk from the serial port
            # (chunkSize) uint16 samples == (chunkSize * 2) bytes
            data = port.read(self.chunkSize * 2) 
            # convert data to 16bit int numpy array TODO, [KINDA DONE]: convert here to -1..+1 values, instead voltage 0..3.3

            # dirty hotfix
            if data[:4] == b'\xd2\x02\x96I' or data[4:8] == b'\xd2\x02\x96I':
                timings = np.frombuffer(data, dtype=np.uint32)
                
                current_tone_i_old = self.current_tone_i
                if data[:4] == b'\xd2\x02\x96I':
                    self.tone_playing   = timings[1]
                    self.current_tone_i = timings[2]
                elif data[4:8] == b'\xd2\x02\x96I':
                    self.tone_playing   = timings[2]
                    self.current_tone_i = timings[3]
                if self.current_tone_i != current_tone_i_old:
                    if self.record_requested:
                        self.recording = True
                        self.recording_start_tone_i = self.current_tone_i
                        self.count = 0
                        self.record_requested = False
                        self.record_start_t = time.time()
                    if self.recording:
                        print(self.current_tone_i - self.recording_start_tone_i)


                    # self.matrix_updated_signal.emit()
                    # print(self.current_tone_i, self.series_n)
                    self.ptr = 0
            else:
                if self.recording and self.tone_playing:
                    if self.current_tone_i - self.recording_start_tone_i < self.series_n:
                        # keep recording
                        data = np.frombuffer(data, dtype=np.uint16)
                        self.matrix[self.current_tone_i - self.recording_start_tone_i, self.ptr : self.ptr + self.chunkSize] = data
                        self.ptr += self.chunkSize
                    else:
                        # save record to file somehow
                        self.matrix_record = self.matrix.copy() * 2 / 4095 - 1
                        self.rate_record = self.count / (time.time() - self.record_start_t)
                        self.record_ready_signal.emit()
                        self.recording = False
                        self.matrix[:, :] = 4095/2 # if map -1..1 to 0..4095, then 0 maps to 4095/2

                    # with dataMutex:
                        # if self.current_tone_i == 0 and self.ptr == 0: # end of series (start of new series), need to update plot
                            # self.mean = np.mean(self.matrix, axis=0) * 2 / 4095 - 1
                            # self.matrix_updated_signal.emit()

                self.count += self.chunkSize

                # collect samples for computing rate 
                #   - even when tone_playing == False
                #       - because the whole series dt is measured (with silences between tones))

    def request_record(self):
        with self.dataMutex:
            self.record_requested = True

    def get_record(self):
        with self.dataMutex:
            return self.matrix_record, self.rate_record

    def get_matrix(self):
        with self.dataMutex:
            return self.matrix_out 

    def get_mean(self):
        with self.dataMutex:
            return self.mean, self.rate

    def exit(self):
        """ Instruct the serial thread to exit."""
        with self.exitMutex:
            self.exitFlag = True



class AppGUI(QtGui.QWidget):
    record_ready = QtCore.pyqtSignal()

    def __init__(self):
        super(AppGUI, self).__init__()
        
        self.file_counter = 0
        self.mm = 0

        self.init_ui()
        self.qt_connections()

    def init_ui(self):
        global record_name, NFFT, chunkSize, overlap

        self.setWindowTitle('Accumulation')
        self.layout = QtGui.QVBoxLayout()

        self.new_accumulation_button = QtGui.QPushButton('New Accumulation')
        self.layout.addWidget(self.new_accumulation_button)



        self.spin = pg.SpinBox(
            value=0,
            int=True,
            bounds=[0, 10000],
            suffix=' mm',
            step=1
        )
        self.layout.addWidget(self.spin)



        self.setLayout(self.layout)
        self.setGeometry(10, 10, 200, 200)
        self.show()

    def qt_connections(self):
        self.new_accumulation_button.clicked.connect(self.request_record)
        self.record_ready.connect(self.save_record)

    def request_record(self):
        ser_reader_thread.request_record()

    def save_record(self):
        matrix, rate = ser_reader_thread.get_record()
        np.save(f'cancellation_accs/{self.mm}-{int(rate)}', matrix)


    def update_matrix(self):
        self.matrix = ser_reader_thread.get_matrix()
        print(f'saving accs/a-{str(self.file_counter)}............................................')
        np.save('accs/a-' + str(self.file_counter), self.matrix)
        self.file_counter += 1
        # print('update_matrix')
        # self.z_slice_img.setImage(self.matrix.T)



    def closeEvent(self, event):
        global ser_reader_thread
        ser_reader_thread.exit()



def main():
    # globals
    global gui, ser_reader_thread, chunkSize
    chunkSize = 256
    chunks    = 2000

    # init gui
    app = QtGui.QApplication(sys.argv)
    gui = AppGUI() # create class instance

    # init and run serial arduino reader
    ser_reader_thread = SerialReader(
        record_ready_signal=gui.record_ready, 
        chunkSize=chunkSize,
        chunks=chunks
    )
    ser_reader_thread.start()

    # app exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
