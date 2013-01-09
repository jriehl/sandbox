import logging; logging.getLogger().setLevel(0)
from numba import *

def bar(x): return x.real

c_bar = jit(f8(c16))(bar)

def foo(x, y):
    return pow(x, y)

c_foo = jit(c16(c16,c16))(foo)
testargs = 2+3j, 1.1-0.9j
assert c_foo(*testargs) == pow(*testargs)
