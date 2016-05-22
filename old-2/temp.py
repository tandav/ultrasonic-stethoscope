import numpy
from math import cos
import matplotlib.pyplot as plt
from random import random
def shrink(arr, n):
	chunk = len(arr) / n
	arr_out = []
	avg = 0
	for i in xrange(len(arr)):
		if (i % chunk == 0 and i != 0):
			arr_out.append(float(avg) / chunk)
			avg = 0
		avg += arr[i]
	arr_out.append(avg / chunk)
	return arr_out

def running_mean(x, N): 
    cumsum = numpy.cumsum(numpy.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N # len(running_mean(x, N)) = len(x) - (N - 1)


x = numpy.arange(1500)
print len(x[::30])
# for i in range(1, 10):
	# print i, len(x[::i]), 20 / i 
