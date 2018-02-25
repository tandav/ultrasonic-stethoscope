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


---
