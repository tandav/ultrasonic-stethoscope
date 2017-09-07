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
