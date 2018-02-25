# Spectrogram
- [Audio Fingerprinting with Python and Numpy (2013) | Hacker News](https://news.ycombinator.com/item?id=12614794)
- [Классификация звуков с помощью TensorFlow / Блог компании DataArt / Хабрахабр](https://habrahabr.ru/company/dataart/blog/343464/)
- [Show HN: Shazam-like acoustic fingerprinting of continuous audio streams | Hacker News](https://news.ycombinator.com/item?id=15809291)
- https://gist.github.com/boylea/1a0b5442171f9afbf372


- matplotlib specgram - google - там есть готовые (но это когда потом записи, для реалтайма - pyqtgraph)
  - Но все равно попробывать, вдруг не очень будет тормозить


- https://www.youtube.com/watch?v=P9Kozlt0tTg
- https://www.youtube.com/watch?v=_FatxGN3vAM&feature=youtu.be
- [Short Time Fourier Transform 1/2 - YouTube](https://www.youtube.com/watch?v=RvKyTCx04u4)
- [The Short Time Fourier Transform | Digital Signal Processing - YouTube](https://www.youtube.com/watch?v=g1_wcbGUcDY)
- [Spectrum analyzer - Wikipedia](https://en.wikipedia.org/wiki/Spectrum_analyzer)
- [18- The Short Time Fourier Transform - YouTube](https://www.youtube.com/watch?v=awWlcFNkiEE)
- [The Short Time Fourier Transform | Digital Signal Processing - YouTube](https://www.youtube.com/watch?v=g1_wcbGUcDY)
- [SignalSpy - Audio Oscilloscope, Frequency Spectrum Analyzer, and more on the Mac App Store](https://itunes.apple.com/be/app/signalspy-audio-oscilloscope-frequency-spectrum-analyzer/id912509512?mt=12)


- Short-time Fourier Transform - youtube and google search 
  - python short time discrete transform
  - https://ru.wikipedia.org/wiki/Оконное_преобразование_Фурье
  - https://en.wikipedia.org/wiki/Spectrogram
  - https://stackoverflow.com/questions/2459295/invertible-stft-and-istft-in-python
  - [scipy.signal.stft — SciPy v1.1.0.dev0+6bb5af0 Reference Guide](http://scipy.github.io/devdocs/generated/scipy.signal.stft.html)
  - бля downsampling все таки должен помоч. потому что так окно можно меньше брать.


- hanning window usage (типок юзает - узнать зачем)
- http://zetcode.com/gui/pyqt4/eventsandsignals/


- Короче ебаш сначала без logscale - просто показывать там до 2-3 кгЦ графике. Как это mvp сделаю - уже пытаться logscale
  - fft overlap?
  - numpy transform image to logscale
  - numpy image transformation
  - numpy image interpolation
- np.roll юзать !!!
- realtime spectrogram - google
  - https://duckduckgo.com/?q=realtime+spectrogram&atb=v83-1__&iax=1&ia=videos


- how to make fast spectrogram - гуглить, мб там какие-то фишки есть
  - есть вар что нужно отбросить жесткий ультрозвук, чтобы низы лучше считались. Понизить частоту дискретизации до 44100 попробовать (щас 666kHz)
  - в идеале нужен слайдер для rate - чтобы в реальном времени двигать
  - есть вар что t нужно не в serialReader расчитывать а в updateplot, чтобы тот thread время не терял, а чисто данные собирал
    - - time_values assumes samples are collected at 1MS/s - ВОТ ЭТО ЕЩЕ ВАЖНО, тут наверное нужно поменять на rate
      - np.linspace(0, (num-1)*1e-6, num) ==>np.linspace(0, (num-1)*(1/rate), num) ?????
  - походу я часто обновляю и щитаю уже посчитанный ффт и у меня полоски жесткие получаются дольше чем реальные звуки. Типы нахлест большой из-за того что часто обновляю график.
    - короче там жестко окна fft перекрываются, нужно меньше. Я типа слишком часто fft считаю. нужно максимум чтобы они до половины перекрывались. 
    - Нужно как-то так сделать чтобы get() не вызывался  по 100 раз, а только когда новые данные уже пришли. До необходимого уровня.
    - EXPERIMNT W/ serial thread chunkSize
    - https://en.wikipedia.org/wiki/Praat
  - походу blackman тащит 
  - тут норм инфа http://coding-geek.com/how-shazam-works/
  - короче походу у меня все норм уже работает. Просто в реалтайме и не получится еще четче картинку получить походу. 
  - change colormap to virdis
    - https://github.com/BIDS/colormap/blob/master/colormaps.py
    - [How to set ImageItem colormaps in code - Google Groups](https://groups.google.com/forum/#!topic/pyqtgraph/gEjC08Vb8NQ)
  - fix record
  - вообще мб забить на downsampling - у меня вроде ффт быстро считается - просто ффт обойтись одним
  - верхний график должен больше показывать - там нужно делать get(num=chunks*chunkSize)
  - capability to select fft window from gui (hanning, blackman, etc)
  - короче 
  - Bruce Land fft
  - Как сделаю норм - сделать видео работы и как отдельную либу для pyaudio выложить на github, чтобы чуваки видели. И на hackday. Типа Very Hi Quality specram типа такого
  - fix overlap / NFFT//2  NFFT//4 + slider 
  - tryna decimate in run, write decimated values to buffer
  - https://news.ycombinator.com/item?id=15447706
  - music pitch detection software
  - [Understanding the Spectrogram/Waveform display - Help Documentation](http://downloads.izotope.com/docs/rx6/07-spectrogram-waveform-display/index.html)
  - REASSIGNMENT for spectrogram
    - The method has been independently introduced by several parties under various names, including method of reassignment, remapping, time-frequency reassignment, and modified moving-window method.
    - [bzamecnik/tfr: Spectral audio feature extraction using time-frequency reassignment](https://github.com/bzamecnik/tfr)
    - http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.5.9579&rep=rep1&type=pdf
    - https://quod.lib.umich.edu/cgi/p/pod/dod-idx/time-frequency-reassignment-for-music-analysis.pdf?c=icmc;idno=bbp2372.2001.041;format=pdf
    - https://www.izotope.com/en/support/knowledge-base/what-do-spectrogram-settings-do-in-RX.html
    - auto adjustable STFT (в изотопе прям заметна разница жестко, обычное - говно по сравнению с auto-adjustable)
    - [Practical Introduction to Time-Frequency Analysis - MATLAB & Simulink Example](https://www.mathworks.com/help/signal/examples/practical-introduction-to-time-frequency-analysis.html#d119e6162)
    - spectrogram reassignment method tutorial
    - - [More frequency resolution from a spectrogram. | Details | Hackaday.io](https://hackaday.io/project/514-more-frequency-resolution-from-a-spectrogram/details)
  - decimate - наверное все-таки придется делать, это быстрее чем ффт
  - [Hey Siri: An On-Device DNN-Powered Voice Trigger for Apple’s Personal Assistant | Hacker News](https://news.ycombinator.com/item?id=15499136)
  - [realtime spectrogram at DuckDuckGo](https://duckduckgo.com/?q=realtime+spectrogram&atb=v83-1__&iax=videos&ia=videos)


- короче запись на spectrogram не работает, поэтому пока откатываюсь на redesign branch и работаю с записями в оффлайне
  - делаю wavelet

- [The promise of AI in audio processing – Towards Data Science](https://towardsdatascience.com/the-promise-of-ai-in-audio-processing-a7e4996eb2ca)
- Mel Spectrogram
- [Continuous low-power music recognition | Hacker News](https://news.ycombinator.com/item?id=16120103)

- [What Do Spectrogram Settings Do in RX | iZotope Knowledge Base](https://www.izotope.com/en/support/knowledge-base/what-do-spectrogram-settings-do-in-RX.html)
- [Speech Spectrogram - File Exchange - MATLAB Central](https://www.mathworks.com/matlabcentral/fileexchange/29596-speech-spectrogram)
- [Understanding the Spectrogram/Waveform display - Help Documentation](http://downloads.izotope.com/docs/rx6/07-spectrogram-waveform-display/index.html)
- [Realtime python spectrograph test - YouTube](https://www.youtube.com/watch?v=9Ti1pjuBic0)
- [Intuitive Understanding of the Fourier Transform and FFTs - YouTube](https://www.youtube.com/watch?v=FjmwwDHT98c)
- [Fourier Transform, Fourier Series, and frequency spectrum - YouTube](https://www.youtube.com/watch?v=r18Gi8lSkfM)
- [izotope rx at DuckDuckGo](https://duckduckgo.com/?q=izotope+rx&atb=v83-1__&iax=videos&ia=videos&iai=XKNYYR-uUEo)
- [rfftn not included from numpy, scipy's rfft different from numpy's rfft · Issue #2487 · scipy/scipy](https://github.com/scipy/scipy/issues/2487)
- [03_mfcc.pdf](http://www.speech.cs.cmu.edu/15-492/slides/03_mfcc.pdf)
