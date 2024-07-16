import math
import threading
import time
import sys
import warnings

module = sys.modules[__name__]

from multiprocessing.dummy import Pool

# Adjust NTHREADS and WORK_SCALE as needed to get a reasonable runtime
NTHREADS = 20
WORK_SCALE = 100

def double(x):
    return x + x

def benchmark(func):
    t0 = time.time()
    func(0)
    t1 = time.time()
    pool.map(func, range(NTHREADS))
    t2 = time.time()

    delta_st = t1 - t0
    delta_mt = t2 - t1
    speed = delta_st * NTHREADS / delta_mt
    if speed >= NTHREADS/2:
        print(f"{func.__name__} PASSED: {round(speed, 1)}x faster")
    elif speed >= 1:
        print(f"{func.__name__} FAILED: {round(speed, 1)}x faster")
    else:
        print(f"{func.__name__} MEGA FAILED: {round(1/speed, 1)}x slower")


def object_cfunction(idx):
    accu = 0
    tab = [idx] * 100
    for i in range(10000 * WORK_SCALE):
        tab.pop(0)
        tab.append(i)
        accu += tab[50]
    return accu

def cmodule_function(i0):
    for i in range(1000 * WORK_SCALE):
        math.floor(i * i)

def mult_constant(i0):
    x = 1.0
    for i in range(1000 * WORK_SCALE):
        x *= 1.01

def simple_gen():
    for i in range(10):
        yield i

def generator(i0):
    accu = 0
    for i in range(100 * WORK_SCALE):
        for v in simple_gen():
            accu += v
    return accu

class Counter:
    def __init__(self):
        self.i = 0

    def next_number(self):
        self.i += 1
        return self.i

def pymethod(i0):
    c = Counter()
    for i in range(1000 * WORK_SCALE):
        c.next_number()
    return c.i

def next_number(i):
    return i + 1

def pyfunction(i0):
    accu = 0
    for i in range(1000 * WORK_SCALE):
        accu = next_number(i)
    return accu

def module_function(i0):
    total = 0
    for i in range(1000 * WORK_SCALE):
        total += module.double(i)
    return total

class MyObject:
    pass

def create_pyobject(i0):
    """ do some expensive operation that involves a thread-local python list """
    for i in range(1000 * WORK_SCALE):
        o = MyObject()

def load_string_const(i0):
    accu = 0
    for i in range(1000 * WORK_SCALE):
        if i == 'a string':
            accu += 7
        else:
            accu += 1
    return accu

def load_tuple_const(i0):
    accu = 0
    for i in range(1000 * WORK_SCALE):
        if i == (1, 2):
            accu += 7
        else:
            accu += 1
    return accu

def create_closure(i0):
    for i in range(1000 * WORK_SCALE):
        def foo(x):
            return x
        foo(i)

def create_dict(i0):
    for i in range(1000 * WORK_SCALE):
        d = {
            "key": "value",
        }

tl = threading.local()

def thread_local_read(i0):
    tmp = tl
    tmp.x = 10
    for i in range(1000 * WORK_SCALE):
        _ = tmp.x
        _ = tmp.x
        _ = tmp.x
        _ = tmp.x
        _ = tmp.x


def main():
    global pool
    if not hasattr(sys, "_is_gil_enabled") or sys._is_gil_enabled():
        warnings.warn("expected GIL to be disabled")

    if len(sys.argv) > 1:
        with Pool(NTHREADS) as pool:
            for func_name in sys.argv[1:]:
                benchmark(globals()[func_name])
        return

    with Pool(NTHREADS) as pool:
        benchmark(object_cfunction)
        benchmark(cmodule_function)
        benchmark(generator)
        benchmark(pymethod)
        benchmark(pyfunction)
        benchmark(module_function)
        benchmark(load_string_const)
        benchmark(load_tuple_const)
        benchmark(mult_constant)

        benchmark(create_closure)
        benchmark(create_pyobject)
        benchmark(create_dict)

        benchmark(thread_local_read)

main()
