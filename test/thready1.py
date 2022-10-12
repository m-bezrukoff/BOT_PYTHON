import threading
import time


list = []

def gen(name):
    global x
    while True:
        x = time.time()
        print('поток ', name, 'сгенерировал: ', x)
        time.sleep(1)


def out(name):
    global x
    while True:
        print('поток ', name, 'получил: ', x)
        time.sleep(1)


# t = threading.Thread(target=gen,
#                      name='thread_gen')
# list.append(t)

t = threading.Thread(target=gen,
                         name='thread_gen',
                         args=('thread_gen',))
list.append(t)
t.daemon = True
t.start()


for i in range(1):
    t = threading.Thread(target=out,
                         name='thread_{}'.format(i),
                         args=('thread_{}'.format(i),))
    list.append(t)
    t.daemon = True
    t.start()

print(list)

for t in list:
    t.join()




print('финиш')
