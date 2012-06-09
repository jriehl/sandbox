/* ______________________________________________________________________
   numpyext.c

   Simple C extension module that demonstrates using the Numpy C API.
   Used as clang input to assist with identifying target LLVM code for
   Numba.

   LLVM test driver: numpy_api_user.py

   Command line:
   % clang -I </path/to/Python.h> -I </path/to/ndarrayobject.h> -emit-llvm \
     numpyext.c

   To build standalone Python extension module (on Linux, anyway):
   % gcc -shared -fPIC -I </path/to/Python.h> -I </path/to/ndarrayobject.h> \
     numpyext.c -o numpyext.so

   Standalone/ctypes test driver: test_numpyext.py
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

int _getndim(PyArrayObject * arr)
{
  if (!PyArray_Check(arr)) return -1;
  return arr->nd;
}

PyObject * _do_zeros_like(PyArrayObject * arr)
{
  if (!PyArray_Check(arr)) return NULL;
  return PyArray_Zeros(arr->nd, arr->dimensions, arr->descr, 0);
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
  PyObject * mod = (PyObject *)NULL;
  import_array();
  mod = Py_InitModule("numpyext", numpyext_methods);
  if (mod)
    {
      PyModule_AddObject(mod, "c_getndim_addr",
                         Py_BuildValue("l", (long)_getndim));
      PyModule_AddObject(mod, "c_do_zeros_like_addr",
                         Py_BuildValue("l", (long)_do_zeros_like));
    }
}

/* ______________________________________________________________________
   End of numpyext.c
   ______________________________________________________________________ */
