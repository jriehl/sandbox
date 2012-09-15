#include <Python.h>

static PyObject * addfunc (PyObject * self, PyObject * args)
{
  const char * func_name = NULL;
  unsigned long func_ptr_uint = 0;
  PyObject * result = NULL;
  PyMethodDef * method = NULL;

  if (!PyArg_ParseTuple(args, "sk", &func_name, &func_ptr_uint))
    return NULL;

  method = malloc(sizeof(PyMethodDef));
  if (method == NULL)
    {
      return NULL;
    }

  method->ml_name = strdup(func_name);
  if (method->ml_name == NULL)
    {
      free(method);
      return NULL;
    }

  method->ml_meth = (PyCFunction)func_ptr_uint;
  method->ml_flags = METH_VARARGS;
  method->ml_doc = NULL;

  result = PyCFunction_NewEx(method, NULL, NULL);

  if (result == NULL)
    {
      free((char *)method->ml_name);
      free(method);
    }

  return result;
}

PyObject * addfunc_add42 (PyObject * self, PyObject * args)
{
  long value = 0;
  if (!PyArg_ParseTuple(args, "l", &value)) return NULL;
  value += 42;
  return PyInt_FromLong(value);
}

static PyMethodDef AddFuncMethods [] = {
  {"addfunc", addfunc, METH_VARARGS,
   "Given a function name as a string, function pointer as an integer, create and return a PyCFunction wrapper object." },
  {"add42", addfunc_add42, METH_VARARGS, NULL},
  { NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initaddfunc (void)
{
  Py_InitModule("addfunc", AddFuncMethods);
}

