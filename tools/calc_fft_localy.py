import matplotlib.pyplot as plt

def calc_fft_localy(record_buffer, n, record_time, rate):
    '''
    OLD: need switch to scipy.fftpack or pyFFTW
    This method calculates fft with np.fft.fft and saves result to plot.png
    '''
    sys.stdout.write('calculate FFT locally...')
    sys.stdout.flush()
    t = np.linspace(0, record_time, n) # time vector
    frq = np.arange(n) / n * rate # two sides frequency range
    frq = frq[range(n // 2)] # one side frequency range
    Y = np.fft.fft(record_buffer) / n # fft computing and normalization
    Y = Y[range(n // 2)]
    Y = abs(Y)
    
    fig, ax = plt.subplots(2, 1)
    fig.suptitle('Signal from Arduino\'s ADC, rate = ' + str(rate)[:3] + 'sps' , fontsize=12)
    
    ax[1].plot(t, record_buffer)
    ax[1].set_xlabel('Time, ' + str(record_time)[:5] + ' seconds')
    ax[1].set_ylabel('Voltage, V')
    ax[1].grid(True)
    ax[0].loglog(frq, Y,'r') # plotting the spectrum
    # ax[0].set_xlim([1, 1e6])
    # ax[0].set_ylim([1e-6,1e-2])
    ax[0].set_xlabel('Freq, Hz')
    ax[0].set_ylabel('Amplitude, dB')
    ax[0].grid()
    ax[0].xaxis.grid(which='minor', color='k', linestyle=':')

    plt.tight_layout()
    plt.savefig('plot.png', dpi=100)
    sys.stdout.write(' done\n')
    os.system('open plot.png')
