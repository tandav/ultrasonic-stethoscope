# Tips
```
buffer
len(buffer) = chunkSize * chunks

buffer fills this way:

[                ]
[....            ]
[........        ]
[............    ]
[................]
[                ]
[....            ]
[........        ]
[............    ]
[................]
[                ]
[....            ]
[........        ]
[............    ]
[................]
        ...
```
- `serial.get(num)` - `num` не должно быть больше len(buffer) = chunkSize * chunks
    - наверн добавить в метод типа `if num > len(self.buffer): print(too many values to get)`
- do not use downsampling in serial.get (пусть будет 1 по умолчанию, в будущем ваще дел, делать downsample - в update plot method самому, иначе там ффт сбивается потому что мало точек в `t` прилетает

# TODO
- BUG: if change initial spinbox value then it will be changing wrong, see `spinbox.step`
- add FFT window slider + Label
- how many points to draw on signal_plot - slider / spinbox
    - how many chunks to fetch (1 - 5000)
    - downsample
    - use native pyqtgraph downsample???
    - http://www.pyqtgraph.org/documentation/graphicsItems/plotitem.html#pyqtgraph.PlotItem.setClipToView - типа чтобы не рисовать точки которые не в окне, ну наверное мне это не надо, хотя мб можно
- widget - to window
