#! /usr/bin/env python
# ______________________________________________________________________
'''numpy_api_user.py

Demo of calling into the Numpy C-API from C extension code loaded via
LLVM (pay no mind to the inline c mechanism).
'''
# ______________________________________________________________________
# Module imports

import os.path
import inline_c as ic # At time of writing this is a test in my fork
                      # of llvm-py.  See .../test/inline_c.py in
                      # https://github.com/jriehl/llvm-py/
import numpy as np
import numpy.ctypeslib as npctl
import ctypes

# ______________________________________________________________________
# Module data

with open('numpyext.c') as cfile:
    NPY_SRC = cfile.read()

numpy_arr_to_int_wrap_func_ty = ctypes.CFUNCTYPE(ctypes.c_int,
                                                 ctypes.py_object)
numpy_arr_to_arr_wrap_func_ty = ctypes.CFUNCTYPE(ctypes.py_object,
                                                 ctypes.py_object)

# ______________________________________________________________________
# Main (demo) routine

def main (*args, **kws):
    global NPY_SRC
    numpyext = ic.py_module_from_c_source('numpyext', NPY_SRC, '-I',
        os.path.join(np.__path__[0], 'core', 'include', 'numpy'))
    test_array = np.array([1,2,3])
    assert numpyext.testfn(test_array) == None
    assert numpyext.getndim(test_array) == 1
    numpyext.c_getndim_wrap = numpy_arr_to_int_wrap_func_ty(
        numpyext.c_getndim_addr)
    assert numpyext.c_getndim_wrap(test_array) == 1
    numpyext.c_do_zeros_like_wrap = numpy_arr_to_arr_wrap_func_ty(
        numpyext.c_do_zeros_like_addr)
    zeros_like_result = numpyext.c_do_zeros_like_wrap(test_array)
    assert (zeros_like_result == 0.).all()
    assert zeros_like_result.shape == test_array.shape
    return numpyext

# ______________________________________________________________________

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of numpy_api_user.py
