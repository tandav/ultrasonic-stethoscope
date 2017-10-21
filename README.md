# Ultrasonic Stethoscope
Ultrasonic stethoscope is a device build on top of Arduino Due, PyQtgraph and NVidia CUDA. Device allows to get HQ sound (about 666 samples per second) and record ultrasonic range up to 333 kHz. Device is supposed to use for medical diagnostics of heart and lungs deseases.

This repo contains software for ultrasonic stethoscope and academic [paper](Paper) describing this project.

## Installation
1. Download and install [Anaconda](https://www.anaconda.com/download)
2. Install pyFFT and last version of pyserial (install it from conda forge channel)

## Running
Activate Anaconda environment and run app: `python app.py`(on windows just double-click `Stethoscope.bat`)

## Overview:
1. Input Signal
2. Ultrasonic mic
3. Amplifier
4. ADC (Arduino Due)
5. App: gets data from ADC,  plots hi-fps soundwawe in realtime, record data to file
6. App: send data to NVidia CUDA Server
7. CUDA Server: calculates fft very fast and sends fft.png (plot of signal's spectrum) back to client's app 
