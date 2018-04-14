# Port to Windows
- попробывать бинарники скопировать чтобы прям без установки (ну только конду установить)
  - скорее всего рип

- [I'm an indie dev and have been developing a cross-platform (Py)Qt app for the pa... | Hacker News](https://news.ycombinator.com/item?id=15870010)

- try run pyqt on windows
  - pyfft fails, pyqt+pyqtgraph вроде норм (просто через пип, возможно через конду)
    - юзать мою прогу , только заменить pyfftw на np,fft.rfft
  - pyqtgraph freezes on small  self.timer.start(0) 
    - set about 10-20ms

- собрать все в один .exe / .app
  - pyqt deploy
  - мб Electron юзать?


---

- короче `cx_Freeze`, `py2exe` - нафиг. Полная дичь. Только `anaconda` и никак иначе.
- пробую offline установку без инета - типа как-то можно в `conda`

--- 
