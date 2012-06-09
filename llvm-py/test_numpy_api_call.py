#! /usr/bin/env python
# ______________________________________________________________________
'''Proof of concept test for LLVM code generation of calls into the
Numpy C API.
'''
# ______________________________________________________________________

import types
import ctypes

import llvm.core as lc
import llvm.ee as le

from numpy.core.multiarray import _ARRAY_API

from numba.translate import _int32, _intp, _intp_star, _void_star, \
    _numpy_struct, _numpy_array, _head_len

# ______________________________________________________________________

_void = lc.Type.void()
_void_star_star = lc.Type.pointer(_void_star)
_void_star_to_void_star_fn = lc.Type.function(_void_star, [_void_star])
_void_star_to_void_fn = lc.Type.function(_void, [_void_star])
_arr_to_arr_fn = lc.Type.function(_numpy_array, [_numpy_array])

_obj_to_obj_cty = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object)
_pa_zeros_fn_ty = lc.Type.function(_numpy_array, [_int32, _intp_star,
                                                  _void_star, _int32])
_pa_zeros_fn_ptr = lc.Type.pointer(_pa_zeros_fn_ty)

# ______________________________________________________________________

def build_llvm_module ():
    ret_val = m = lc.Module.new(b'numpy_caller_module')
    api = m.add_global_variable(_void_star_star, 'PyArray_API')
    api.initializer = lc.Constant.inttoptr(lc.Constant.int(_intp, 0),
                                           _void_star_star)
    api.linkage = lc.LINKAGE_INTERNAL
    # ____________________________________________________________
    pycobj_avp = m.add_function(_void_star_to_void_star_fn,
                                'PyCObject_AsVoidPtr')
    init_api_fn = m.add_function(_void_star_to_void_star_fn,
                                 'init_api_fn')
    bb = init_api_fn.append_basic_block('entry')
    builder = lc.Builder.new(bb)
    arg = init_api_fn.args[0]
    api_val = builder.bitcast(builder.call(pycobj_avp, [arg]), _void_star_star)
    builder.store(api_val, api)
    builder.ret(api_val)
    # ____________________________________________________________
    pyobj_incref = m.add_function(_void_star_to_void_fn, 'Py_IncRef')
    test_fn0 = m.add_function(_arr_to_arr_fn, b'test_fn0')
    bb = test_fn0.append_basic_block(b'entry')
    builder = lc.Builder.new(bb)
    arg = test_fn0.args[0]
    builder.call(pyobj_incref, [builder.bitcast(arg, _void_star)])
    builder.ret(arg)
    # ____________________________________________________________
    test_fn1 = m.add_function(_arr_to_arr_fn, b'test_fn1')
    bb = test_fn1.append_basic_block('entry')
    builder = lc.Builder.new(bb)
    arg = test_fn1.args[0]
    pa_zeros_ptr = (
        builder.load(
            builder.gep(
                builder.load(api),
                [lc.Constant.int(_int32, 183)])))
    pa_zeros = builder.bitcast(pa_zeros_ptr, _pa_zeros_fn_ptr)
    largs = [
        builder.load(
            builder.gep(arg,
                        [lc.Constant.int(_int32, 0),
                         lc.Constant.int(_int32, _head_len + ofs)]))
        for ofs in (1, 2, 5)]
    largs.append(lc.Constant.int(_int32, 0))
    builder.ret(builder.call(pa_zeros, largs))
    return ret_val

# ______________________________________________________________________

def build_py_module ():
    ret_val = types.ModuleType('py_numpy_caller_module')
    m = build_llvm_module()
    ee = le.ExecutionEngine.new(m)
    api_pycobj_lval = le.GenericValue.pointer(_void_star, id(_ARRAY_API))
    ee.run_static_ctors()
    ee.run_function(m.get_function_named('init_api_fn'), [api_pycobj_lval])
    test_fn0, test_fn1 = (m.get_function_named(fnname)
                          for fnname in ('test_fn0', 'test_fn1'))
    test_fn0_addr = ee.get_pointer_to_function(test_fn0)
    ret_val.test_fn0_addr = test_fn0_addr
    ret_val.test_fn0 = _obj_to_obj_cty(test_fn0_addr)
    test_fn1_addr = ee.get_pointer_to_function(test_fn1)
    ret_val.test_fn1_addr = test_fn1_addr
    ret_val.test_fn1 = _obj_to_obj_cty(test_fn1_addr)
    ret_val._llvm_module = m
    ret_val._ee = ee
    return ret_val

# ______________________________________________________________________

def main (*args, **kws):
    import numpy
    extmod = build_py_module()
    test_arr = numpy.array([1.,2.,3.])
    assert (extmod.test_fn0(test_arr) == test_arr).all()
    result1 = extmod.test_fn1(test_arr)
    assert result1.shape == test_arr.shape
    assert (result1 == 0.).all()
    print extmod._llvm_module

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of test_numpy_api_call.py
