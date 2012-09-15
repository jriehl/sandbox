#! /usr/bin/env python
# ______________________________________________________________________

try:
    import dl
except ImportError:
    dl = None
import sys
import os
import signal
import StringIO
import platform

import llvm.core as lc
import llvm.ee as le

try:
    import addfunc
except ImportError:
    addfunc = None

import pyaddfunc

import ctypes

# ______________________________________________________________________

with open('add42_%s.ll' % platform.architecture()[0]) as src_file:
    add42_module = lc.Module.from_assembly(src_file)

ee = le.ExecutionEngine.new(add42_module)

if dl and addfunc:
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

if addfunc:
    add42_llvm = addfunc.addfunc("add42_llvm", add42_llvm_ptr)

if dl:
    py_add42_dl = pyaddfunc.pyaddfunc('py_add42_dl', add42_dl_ptr)
py_add42_llvm = pyaddfunc.pyaddfunc('py_add42_llvm', add42_llvm_ptr)

# ______________________________________________________________________

def test_funcs ():
    if dl and addfunc:
        funcs = add42_dl, add42_llvm, py_add42_dl, py_add42_llvm
    elif addfunc:
        funcs = add42_llvm, py_add42_llvm
    else:
        funcs = (py_add42_llvm,)
    print funcs
    for i in xrange(42):
        expected = i + 42
        for func in funcs:
            assert func(i) == expected, '%r is a bad func!' % (func,)

# ______________________________________________________________________

if __name__ == "__main__":
    if '--break' in sys.argv:
        sys.argv.remove('--break')
        os.kill(os.getpid(), signal.SIGTRAP)
    test_funcs()

# ______________________________________________________________________
# End of test_addfunc.py
