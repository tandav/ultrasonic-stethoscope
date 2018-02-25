# Someday
- move back to pip (anaconda del, too big)
- https://stackoverflow.com/questions/47510617/saving-data-to-image-in-batch-need-speedup
- http://amyboyle.ninja/blog_list.html - deep shit
- Add LPC envelope?
- class SerialReader - в отдельный файл
- Удалить ненужные буффер в run()??? // уже забыл что это, check it out
- нужен варик не только с генератора но и со встроенного микро добавить(pyaudio)
- мб сделать чтобы не постоянно график ехал, а заполнялся типа. слува направа, потом по старому новое пошло Как на осцилографе
- какие-то артефакты вверху (2 полоски)

---

keyboardevent latency - check
- https://www.saltycrane.com/blog/2008/01/how-to-capture-tab-key-press-event-with/ better shit with signals
- try del fft plot

---

- [Qt Crash Course — pyqtgraph 0.10.0 documentation](http://www.pyqtgraph.org/documentation/qtcrashcourse.html)
- [PyQT4 Tutorials – Python Tutorial](https://pythonspot.com/en/pyqt4/)
- [Coding With Ninjas](http://amyboyle.ninja/blog_list.html)
- https://github.com/mherrmann/pyqt-resources/wiki

---

- У меня только один instance класса PyQt - сделать чисто на функциях, без ООП. Там можно в PyQt, когда без классов. Чисто ради readability
  - сделать transition в отдельном файле, где меньше функционал (аля рандомный квадрат просто обновляется)
  - а мб и не надо, а то вдруг потом придется в будущем много окон делать и всякие сложные UI
- try как матплотлиб переводит в лог координаты - и попробовать также для картинки. Также черкнуть, есть ли specgram log scale. Если ест. - то черкнуть исходный код. 
  - https://gist.github.com/ganwell/3772157
- должен указываться не downsampling а количество точек на каждом графике
  - (по идее должен быть регулятор в GUI)
  - вообще там есть native downsampling - юзать его
  - и оси тоже - там по правой кнопке норм
- send_to_cuda - переименовать в типа handle record и перенести в класс AppGUI
  - write to file тоже
- нормальное время на signal_plot
  - бля там написано time_values assumes samples are collected at 1MS/s
    - check it out
- https://docs.scipy.org/doc/scipy/reference/signal.html
- добавить секунды на лейбл fft типа сколько секунд окно

---
