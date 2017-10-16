import numpy as np
from time import time
def signal(freq=440, rate=44100, seconds=10):
    # T = 1./rate; # sampling interval / period
    # t = np.arange(0, seconds, T) # time vector
    t = np.linspace(0, seconds, seconds*rate)  # time vector

    # num = data.shape[0]
    # return np.linspace(0, (num-1)*1e-6, num), data, rate

    # ff = 1400 * np.random.random()
    
    n = len(t)
    # y = np.sin(2*np.pi*ff*t)
    # y = t - np.floor(t)
    # y = np.sin(2*np.pi*freq*t - time()) - np.sin(2*np.pi*freq*t - time()) * 0.4 * np.random.random(n) 
    y = np.sin(2*np.pi*freq*t) + np.sin(3*np.pi*freq*t*np.random.random())

    return t, y, rate
