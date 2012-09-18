/* ______________________________________________________________________
   Tests of using Py_BuildValue() and seeing what clang generates...
   ______________________________________________________________________ */

#include "Python.h"


PyObject * mk_42 (PyObject * self, PyObject * args)
{
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("d", 42.);
}

float f_id (float in_val)
{
  return in_val;
}

PyObject * mk_42_f (PyObject * self, PyObject * args)
{
  /* This is an interesting case because it exposes a C
     ABI compatibility issue, where the float val is upcasted to a
     double when Py_BuildValue is called...*/
  float val = 42.;
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("f", f_id(val));
}

/* ______________________________________________________________________
   End of build_vals.c
   ______________________________________________________________________ */
