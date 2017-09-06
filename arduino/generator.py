import numpy as np
from time import time
def signal(rate=44100, seconds=10):
    # T = 1./rate; # sampling interval / period
    # t = np.arange(0, seconds, T) # time vector
    t = np.linspace(0, seconds, rate)  # time vector

    # num = data.shape[0]
    # return np.linspace(0, (num-1)*1e-6, num), data, rate

    # ff = 1400 * np.random.random()
    ff = 440
    n = len(t)
    # y = np.sin(2*np.pi*ff*t)
    # y = t - np.floor(t)
    y = np.sin(2*np.pi*ff*t - time()) - np.sin(2*np.pi*ff*t - time()) * 0.4 * np.random.random(n) 
    # y = np.sin(2*np.pi*ff*t) + np.sin(3*np.pi*ff*t)

    return t, y, rate, seconds, n
