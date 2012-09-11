#! /usr/bin/env python
# ______________________________________________________________________

import dl
import sys
import os
import signal
import StringIO

import llvm.core as lc
import llvm.ee as le

import addfunc

import ctypes

# ______________________________________________________________________

with open('add42.ll') as src_file:
    add42_module = lc.Module.from_assembly(src_file)

ee = le.ExecutionEngine.new(add42_module)

add42_dl_ptr = dl.open('./addfunc.so').sym('addfunc_add42')

if __debug__:
    print("add42_dl_ptr = %s" % hex(add42_dl_ptr))

add42_dl = addfunc.addfunc("add42_dl", add42_dl_ptr)
add42_llvm_fn = add42_module.get_function_named('add42')

if __debug__:
    print add42_llvm_fn
    print add42_module.to_native_assembly()

add42_llvm_ptr = ee.get_pointer_to_function(add42_llvm_fn)

if __debug__:
    print("add42_llvm_ptr = %s" % hex(add42_llvm_ptr))

add42_llvm = addfunc.addfunc("add42_llvm", add42_llvm_ptr)

# ______________________________________________________________________

class PyMethodDef (ctypes.Structure):
    _fields_ = [
        ('ml_name', ctypes.c_char_p),
        ('ml_meth', ctypes.c_uint),
        ('ml_flags', ctypes.c_int),
        ('ml_doc', ctypes.c_char_p),
        ]

PyCFunction_NewEx = ctypes.pythonapi.PyCFunction_NewEx
PyCFunction_NewEx.argtypes = (ctypes.POINTER(PyMethodDef),
                              ctypes.c_void_p,
                              ctypes.c_void_p)
PyCFunction_NewEx.restype = ctypes.py_object

cache = {} # Unsure if this is necessary to keep the PyMethodDef
           # structures from being garbage collected.  Assuming so...

def pyaddfunc (func_name, func_ptr, func_doc = None):
    global cache
    key = (func_name, func_ptr)
    if key in cache:
        _, ret_val = cache[key]
    else:
        mdef = PyMethodDef(func_name,
                           func_ptr,
                           1, # == METH_VARARGS (hopefully remains so...)
                           func_doc)
        ret_val = PyCFunction_NewEx(ctypes.byref(mdef), 0, 0)
        cache[key] = (mdef, ret_val)
    return ret_val

py_add42_dl = pyaddfunc('py_add42_dl', add42_dl_ptr)
py_add42_llvm = pyaddfunc('py_add42_llvm', add42_llvm_ptr)

# ______________________________________________________________________

def test_funcs ():
    print add42_dl, add42_llvm, py_add42_dl, py_add42_llvm
    for i in xrange(42):
        expected = i + 42
        assert add42_dl(i) == expected
        assert add42_llvm(i) == expected
        assert py_add42_dl(i) == expected
        assert py_add42_llvm(i) == expected

# ______________________________________________________________________

if __name__ == "__main__":
    if '--break' in sys.argv:
        sys.argv.remove('--break')
        os.kill(os.getpid(), signal.SIGTRAP)
    test_funcs()

# ______________________________________________________________________
# End of test_addfunc.py
