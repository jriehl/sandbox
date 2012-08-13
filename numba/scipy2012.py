'''Demoware from SciPy 2012 sprint.
'''
import sys

if 'PyPy' in sys.version:
    def jit_on_opt (fn):
        return fn
else:
    from numba.decorators import numba_compile as jit

    def jit_on_opt (fn, *args, **kws):
        if not __debug__:
            fn = jit(*args, **kws)(fn)
        return fn

@jit_on_opt
def series_sum (n):
    acc = 0.
    for val in xrange(n):
        acc += val
    return acc

if __name__ == "__main__":
    ntimes = 1
    if len(sys.argv) > 1:
        ntimes = int(sys.argv[1])
    print series_sum(ntimes)
