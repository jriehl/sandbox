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

# ______________________________________________________________________
# Module data

with open('numpy_api_user.c') as cfile:
    NPY_SRC = cfile.read()

# ______________________________________________________________________
# Main (demo) routine

def main (*args, **kws):
    global NPY_SRC
    numpyext = ic.py_module_from_c_source('numpyext', NPY_SRC, '-I',
        os.path.join(np.__path__[0], 'core', 'include', 'numpy'))
    test_array = np.array([1,2,3])
    assert numpyext.testfn(test_array) == None
    assert numpyext.getndim(test_array) == 1

# ______________________________________________________________________

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of numpy_api_user.py
