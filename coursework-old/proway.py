from pylab import*
from scipy.io import wavfile
import time

start = time.time()


sampFreq, snd = wavfile.read('saw3harm.wav')
snd = snd / (2.**15)
s1 = snd[:,0]  # taking 1st channel
n = len(s1) 
p = fft(s1) # take the fourier transform

nUniquePts = ceil((n+1)/2.0)
p = p[0:nUniquePts]
p = abs(p)

p = p / float(n) # scale by the number of points so that
                 # the magnitude does not depend on the length 
                 # of the signal or on its sampling frequency  
p = p**2  # square it to get the power 

# multiply by two (see technical document for details)
# odd nfft excludes Nyquist point
if n % 2 > 0: # we've got odd number of points fft
    p[1:len(p)] = p[1:len(p)] * 2
else:
    p[1:len(p) -1] = p[1:len(p) - 1] * 2 # we've got even number of points fft

end = time.time()
print 'Finishe',end - start, 'seconds'
freqArray = arange(0, nUniquePts, 1.0) * (sampFreq / n);
# plot(freqArray/1000, 10*log10(p), 'k.-')
# xlabel('Frequency (kHz)')
plot(freqArray, 10*log10(p), 'k.-')
xlabel('Frequency (Hz)')
ylabel('Power (dB)')
show()