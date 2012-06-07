/* ______________________________________________________________________
   numpy_api_user.c

   Simple C extension module that demonstrates using the Numpy C API.
   Used as clang input to assist with identifying target LLVM code for
   Numba.

   Test driver: numpy_api_user.py

   Command line:
   % clang -I </path/to/Python.h> -I </path/to/ndarrayobject.h> -emit-llvm \
     numpy_api_user.c
   ______________________________________________________________________ */

#include <Python.h>
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

static PyObject *
numpyext_getndim(PyObject * self, PyObject * args)
{
  PyArrayObject * arr = (PyArrayObject *)NULL;
  if (!PyArg_ParseTuple(args, "O", &arr)) return NULL;
  if (!PyArray_Check(arr))
    {
      PyErr_SetString(PyExc_ValueError, "Exepected ndarray input.");
      return NULL;
    }
  return Py_BuildValue("i", arr->nd);
}

static PyMethodDef numpyext_methods[] = {
  {"testfn", numpyext_testfn, METH_VARARGS, NULL},
  {"getndim", numpyext_getndim, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initnumpyext(void)
{
  import_array();
  Py_InitModule("numpyext", numpyext_methods);
}

/* ______________________________________________________________________
   End of numpy_api_user.c
   ______________________________________________________________________ */
