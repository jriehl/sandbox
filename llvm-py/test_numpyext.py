#! /usr/bin/env python
# ______________________________________________________________________
'''test_numpyext

Perform tests on a standalone shared object built from the Numpy C API
test module, numpyext.c.
'''
# ______________________________________________________________________

import numpyext
import ctypes
import numpy as np
import numpy.ctypeslib as npctl

numpy_arr_ty = npctl.ndpointer(flags = 'C_CONTIGUOUS')
numpy_arr_to_int_wrap_func_ty = ctypes.CFUNCTYPE(ctypes.c_int, numpy_arr_ty)

# ______________________________________________________________________

def test_standalone_wrap ():
    c_getndim_wrap = numpy_arr_to_int_wrap_func_ty(numpyext.c_getndim_addr)
    arr = np.array([1.,2,3])
    assert c_getndim_wrap(arr) == numpyext.getndim(arr)

def test_dll_wrap ():
    numpyext2 = ctypes.CDLL('./numpyext.so')
    numpyext2._getndim.argtypes = [numpy_arr_ty]
    numpyext2._getndim.restype = ctypes.c_int
    assert numpyext2._getndim(np.array([1.,2,3])) == 1

# ______________________________________________________________________
# Main routine

def main (*args, **kws):
    if len(args):
        for arg in args:
            if arg == 'standalone':
                test_standalone_wrap()
            elif arg == 'dll':
                test_dll_wrap()
    else:
        test_standalone_wrap()
        test_dll_wrap()

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of test_numpyext.py
