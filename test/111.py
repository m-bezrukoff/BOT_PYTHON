import json
import os
import pickle
from inc.inc_log import log_pair_history


class Person:
    def __init__(self, name, age, **kwargs):
        self.name = name
        self.age = age
        self.attribute = kwargs or None


class ComplexEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, complex):
            return (z.real, z.imag)
        else:
            super().default(self, z)


def sessions_save(obj):
    print(json.dumps(obj, cls=PersonEncoder))


class PersonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Person):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

a = {}

a['BTH'] = Person('Bob', 30, height=180, width=70)
a['RVN'] = Person('Fred', 40, height=170, width=740)

log_pair_history('BTH', a['BTH'])

# print(pickle.dumps(a))
# print(a['BTH'].__dict__)
# print(json.dumps(a, cls=ComplexEncoder))
#
# with open('data.pickle', 'wb') as f:
#     pickle.dump(a, f)
#
# with open('data.pickle', 'rb') as f:
#     data_new = pickle.load(f)
# print(data_new['BTH'].age)

# p = Person('Bob', 30, height=180, width=70)
# print(json.dumps(a, cls=PersonEncoder))
# # {"name": "Bob", "age": 30, "attricbute": {"height": 180, "width": 70}}
#
# p = Person('Bob', 30)
# print(json.dumps(p, cls=PersonEncoder))
# # {"name": "Bob", "age": 30, "attribute": null}

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# print(ROOT_DIR)
# # Десериализация пример
# print(json.dumps(a, cls=PersonEncoder))
# with open(ROOT_DIR + '/save/1.txt', 'w') as f:
#     json.dump(a, f, cls=PersonEncoder)
#
# print((json.load(open(ROOT_DIR + '/save/1.txt'))))
