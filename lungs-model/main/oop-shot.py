class A(object):
    """docstring for A"""
    def __init__(self):
        self.x = 12

class B(object):
    """docstring for B"""
    def __init__(self):
        self.a = A()

    def change(self, num):
        self.a.x = num


b = B()

print(b.a.x)

b.change(0)
print(b.a.x)
print(a.x)

                
