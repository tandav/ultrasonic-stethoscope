# Fast FFT
FAST FFT

- короче на текущий момент pyFFT работает медленнее numpy.fft и scipy.fftpack
  - avg fft time measurements
    - numpy: 0.0165650823623
    - scipy: 0.0160278922544
    - pyfft: 0.0196073707378
  - короче видимо нужно сильнее оптимизировать. А пока не парюсь и юзаю scipy (чуть быстрее numpy потому что фортран, иногда значительно быстрее)
    - юзаю fftpack.fft, а не fftpack.rfft, потому что он там странный
      - ну нужно сильнее прошариваться, пока так
  - бля вообще заметил что pyFFTW в отличии от numpy и scipy еще домножалось на  np.hanning(self.NFFT).
    - так что для чистоты эксперимента нужно еще раз все замерить
    - ну пока время нет - на scipy посижу
    - ну и потом добавить fft windowing (hanning) в scipy/numpy
- mutex - долгая операция, мб как-то оптимизировать можно
- [Using pyfftw properly for speed up over numpy - Stack Overflow](https://stackoverflow.com/questions/28227314/using-pyfftw-properly-for-speed-up-over-numpy)
[the fastest fft python - Google Search](https://www.google.ru/search?newwindow=1&q=the+fastest+fft+python&spell=1&sa=X&ved=0ahUKEwjeu4i6x4bWAhWIa5oKHdazAlsQvwUIJSgA&biw=1440&bih=799)
