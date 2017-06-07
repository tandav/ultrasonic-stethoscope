# Ultrasonic Stethoscope
Ultrasonic stethoscope is a device build on top of Arduino Due, PyQtgraph and NVidia CUDA. Device allows to get HQ sound (about 666 samples per second) and record ultrasonic range up to 333 kHz. Device is supposed to use for medical diagnostics of heart and lungs deseases.

This repo contains software for ultrasonic stethoscope and academic [paper](Paper) describing this project.

## Overview:
1. Input Signal
2. Ultrasonic mic
3. Amplifier
4. ADC (Arduino Due)
5. App: gets data from ADC,  plots hi-fps soundwawe in realtime, record data to file
6. App: send data to NVidia CUDA Server
7. CUDA Server: calculates fft very fast and sends fft.png (plot of signal's spectrum) back to client's app 

## TODO
- [ ] insert picture of device here

![plot](https://user-images.githubusercontent.com/5549677/26873219-b79b1884-4b81-11e7-9449-4979e5596dbe.png)
![plot-example](Server/fft-0.png)
