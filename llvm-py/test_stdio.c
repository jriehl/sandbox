/* ______________________________________________________________________
   test_stdio.c

   Check to see what clang outputs for the standard I/O FILE *'s.
   ______________________________________________________________________ */

#include "Python.h"

PyObject *
get_libc_file_addrs(PyObject *self, PyObject *args)
{
  PyObject *result = NULL, *in = NULL, *out = NULL, *err = NULL;
  in = PyLong_FromVoidPtr(&stdin);
  out = PyLong_FromVoidPtr(&stdout);
  err = PyLong_FromVoidPtr(&stderr);
  if (!(in && out && err))
    goto error;

  result = PyTuple_Pack(3, in, out, err);

 error:
  Py_XDECREF(in);
  Py_XDECREF(out);
  Py_XDECREF(err);
  return result;
}

/* ______________________________________________________________________
   End of test_stdio.c
   ______________________________________________________________________ */
