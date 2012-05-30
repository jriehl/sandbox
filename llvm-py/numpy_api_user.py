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

NPY_SRC = '''#include <Python.h>
#include "ndarrayobject.h"

static PyObject *
numpyext_testfn(PyObject * self, PyObject * args)
{
  PyArrayObject * arr = (PyArrayObject *)NULL;
  if (!PyArg_ParseTuple(args, "O", &arr)) return NULL;
  if (!PyArray_Check(arr))
    {
      PyErr_SetString(PyExc_ValueError, "Exepected ndarray input.");
      return NULL;
    }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef numpyext_methods[] = {
  {"testfn", numpyext_testfn, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initnumpyext(void)
{
  import_array();
  Py_InitModule("numpyext", numpyext_methods);
}
'''

# ______________________________________________________________________
# Main (demo) routine

def main (*args, **kws):
    numpyext = ic.py_module_from_c_source('numpyext', NPY_SRC, '-I',
        os.path.join(np.__path__[0], 'core', 'include', 'numpy'))
    assert numpyext.testfn(np.array([1,2,3])) == None

# ______________________________________________________________________

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of numpy_api_user.py
