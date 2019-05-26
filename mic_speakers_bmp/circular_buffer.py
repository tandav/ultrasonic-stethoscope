import numpy as np

class CircularBuffer:
    '''
    works only if chunks of data aligns into buffer
    (the most right chunk should be able to put without breaks into 2 smallest)

    TODO:
        just a quick version, maybe there are better ones
        google.com/search?q=numpy+circular+buffer
        github.com/tandav/gists/blob/master/manual_circular_buffer_vs_np_roll_benchmark.ipynb

    TODO:
        maybe it is better to use collections.deque
        but store chunks of data (numpy objects) instead all elements

    '''
    def __init__(self, n, dtype):
        self.buffer = np.full(shape=n, fill_value=np.nan, dtype=dtype)
        self.cursor = 0 # pointer to most (recently collected buffer index) + 1

    def append(self, item):
        self.buffer[self.cursor: self.cursor + 1] = item


        self.cursor = (self.cursor + 1) % self.buffer.shape[0]

        # self.cursor += 1

        # if self.cursor == self.buffer.shape[0]:
        #     self.cursor = 0
        #     self.buffer[:] = np.nan


    def extend(self, array_like):
        # TODO: coment this assert for performance
        # assert len(self.buffer) % len(array_like) == 0, 'chunks of data not aligns into buffer'

        # print(sum(array_like == 0))
        array_like_length = array_like.shape[0]
        self.buffer[self.cursor : self.cursor + array_like_length] = array_like

        self.cursor += array_like_length

        if self.cursor == self.buffer.shape[0]:
            self.cursor = 0
            self.buffer[:] = np.nan
        # self.cursor = (self.cursor + array_like_length) % self.buffer.shape[0]

    def most_recent(self, n):
        assert n <= len(self.buffer), 'requested data is bigger than buffer size'

        if self.cursor - n < 0:
            data = np.empty(n, self.buffer.dtype)
            data[:n - self.cursor] = self.buffer[self.cursor - n:]
            data[n - self.cursor:] = self.buffer[:self.cursor]
        else:
            data = self.buffer[self.cursor - n:self.cursor].copy()
        return data

    def __repr__(self):
        return repr(self.buffer)
