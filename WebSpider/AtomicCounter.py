from multiprocessing import Process, Value, Lock
import time

'''
Atomic counter to keep track of number of pages crawled by multiple threads
'''


class Counter(object):
    def __init__(self, value=0):
        # RawValue because we don't need it to create a Lock:
        self.val = Value('i', value)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value
