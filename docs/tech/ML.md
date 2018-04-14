# ML / DL
начинать уже думать варики ML/DL моделей для записей больных

- на янексе лекции чекать, не обяз про сердце/легкцие - любые звуковые сигналы или ЭЭГ - ну короче сигналы
- fft machine learning
- fft feature extraction
- machine learning for audio
- machine learning signal processing
- чекаю ml-algorithms for time signals
  -  time-series data (e.g. audio, video, sensors) : RNN, LSTM
- MVP-суть
  - по сути нужна задача классификации.
    - типа есть размеченные врачом данные. И для нового человека нужно по fft-спектру определить к какому класу относится данный чувак.
      - не обязательно ффт, возможно тут нужны какие-то другие методы, фурье - оно типа сжимает, а вдруг нужно чтобы оно всю совокупность воспринимало.
      - https://en.wikipedia.org/wiki/Spectrogram
        - + youtube
        - + google images
        - + google search
    - Для начала попробывать просто типа разные частоты сгенерировать / записать. - и типа чтобы программа их различала.
    - Потом можно чтобы она отличала запись вдоха от сердца
  - machine learning classification algorithms
    - svm/knn/k-means???
    - ну именно deep-learning наверное юзать - с весами, с обучением, с нейронками, а не просто старые алгоритмы
- Сигнал с сердца, всякие аритмии 
- [Student Ambassador Program Details | Intel® Software](https://software.intel.com/en-us/ai-academy/ambassadors/details)
- Прослушать и спросить у врачей что именно они там по звуку определяют. На что обращать внимание. Сможет ли врач по моей аудиозаписи в наушниках определить что то ( если нет то тогда можно даже не стараться - хуевые записи.)
- [Time Series Analysis In Python - YouTube](https://www.youtube.com/watch?v=0NkKq7AGYaQ)
- [Архитектура и алгоритмы индексации аудиозаписей ВКонтакте / Блог компании ВКонтакте / Хабрахабр](https://habrahabr.ru/company/vkontakte/blog/330988/)
- https://pdfs.semanticscholar.org/94e3/eed1b0a772f7156cddac66490792e2e0ff29.pdf
