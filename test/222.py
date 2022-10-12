class A:
    def __init__(self):
        self.count = 0

    @staticmethod
    def decorator(func):
        def func_wrap(cls, *args, **kwargs):
            # print(cls.ser.__dict__)
            cls.ser.count += 1
            print(cls.ser.count)
            return func(cls, *args, **kwargs)
        return func_wrap


class B:
    def __init__(self):
        self.a = 'a'
        self.ser = A()

    @A.decorator
    def qqq(self):
        print(self.a)


h = B()
for i in range(5):
    print(h.qqq())
    # print()