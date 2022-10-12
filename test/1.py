from random import randint
from time import time

t1 = time()
for i in range(3000000):
    a = randint(0, 1000)
    if a % 2 == 0:
        if a > 500:
            if a % 10 == 0:
                pass
t2 = time()
print(t2 - t1)
