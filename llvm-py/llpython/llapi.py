#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ______________________________________________________________________
# Module imports

from llpython.bytetype import lc, lvoid, l_pyobj_p, l_pyobj_pp, lc_int, \
    lc_long, li1, li32, li8_ptr
from llpython.byte_translator import llpython

# ______________________________________________________________________
# Module data

llapi_module = lc.Module.new('llapi')

lfn = lc.Type.function

_UNARY_FN_ty = lfn(l_pyobj_p, [l_pyobj_p])

_BINARY_FN_ty = lfn(l_pyobj_p, [l_pyobj_p, l_pyobj_p])

# ______________________________________________________________________
# Module functions

_REFCNT_FN_ty = lfn(lvoid, [l_pyobj_p])

@llpython(_REFCNT_FN_ty, llapi_module)
def __INCREF(obj):
    refcnt_p = gep(obj, (0, li32(0)))
    refcnt_p[0] += 1

@llpython(_REFCNT_FN_ty, llapi_module)
def _INCREF(obj):
    if obj != l_pyobj_p(0):
        __INCREF(obj)

@llpython(_REFCNT_FN_ty, llapi_module)
def _DECREF(obj):
    if obj != l_pyobj_p(0):
        refcnt_p = gep(obj, (0, li32(0)))
        refcnt = load(refcnt_p)
        if refcnt > 1:
            refcnt_p[0] -= 1
        else:
            Py_DecRef(obj)

# declare void @_STORE_FAST({ i32, i32* }*, { i32, i32* }**)

_STORE_FAST_ty = lfn(lvoid, (l_pyobj_p, l_pyobj_pp))
@llpython(_STORE_FAST_ty, llapi_module)
def _STORE_FAST(src, dest):
    if dest != l_pyobj_pp(0):
        tmp = load(dest)
        dest[0] = src
        _DECREF(tmp)

# declare { i32, i32* }* @_LOAD_FAST({ i32, i32* }**)

_LOAD_FAST_ty = lfn(l_pyobj_p, [l_pyobj_pp])
@llpython(_LOAD_FAST_ty, llapi_module)
def _LOAD_FAST(src):
    rv = l_pyobj_p(0)
    if src != l_pyobj_pp(0):
        rv = load(src)
        if rv != l_pyobj_p(0):
            __INCREF(rv)
        # XXX else: raise unbound local error
    return rv

# declare { i32, i32* }* @_BINARY_MODULO({ i32, i32* }*, { i32, i32* }*)

_BINARY_MODULO_ty = _BINARY_FN_ty
@llpython(_BINARY_MODULO_ty, llapi_module)
def _BINARY_MODULO(arg0, arg1):
    if PyString_CheckExact(arg0) != 0:
        rv = PyString_Format(arg0, arg1)
    else:
        rv = PyNumber_Remainder(arg0, arg1)
    _DECREF(arg0)
    _DECREF(arg1)
    return rv

# declare { i32, i32* }* @_LOAD_CONST_INT(i32)

_LOAD_CONST_INT_ty = lfn(l_pyobj_p, [lc_long])
@llpython(_LOAD_CONST_INT_ty, llapi_module)
def _LOAD_CONST_INT(ival):
    return PyInt_FromLong(ival)

# declare { i32, i32* }* @_COMPARE_OP(i32, { i32, i32* }*, { i32, i32* }*)

@llpython(lfn(li8_ptr, [l_pyobj_p]), llapi_module)
def _Py_GetType(arg):
    return load(gep(arg, (0, li32(1))))

@llpython(lfn(li1, [l_pyobj_p]), llapi_module)
def _PyInt_CheckExact(arg):
    return _Py_GetType(arg) == `PyInt_Type`

_COMPARE_OP_ty = lfn(l_pyobj_p, [lc_int, l_pyobj_p, l_pyobj_p])
@llpython(_COMPARE_OP_ty, llapi_module)
def _COMPARE_OP(op, arg0, arg1):
    if _PyInt_CheckExact(arg0) and _PyInt_CheckExact(arg1):
        rv = PyBool_FromLong(lc_long(0))
    else:
        rv = PyBool_FromLong(lc_long(1))
    return rv

# declare i1 @_POP_JUMP_IF_FALSE({ i32, i32* }*)
# declare { i32, i32* }* @_INPLACE_ADD({ i32, i32* }*, { i32, i32* }*)
# declare void @_DELETE_FAST(i1, { i32, i32* }**)
# declare i1 @_SETUP_LOOP()
# declare { i32, i32* }* @_BINARY_AND({ i32, i32* }*, { i32, i32* }*)
# declare { i32, i32* }* @_INPLACE_MULTIPLY({ i32, i32* }*, { i32, i32* }*)
# declare { i32, i32* }* @_INPLACE_RSHIFT({ i32, i32* }*, { i32, i32* }*)
# declare { i32, i32* }* @_BREAK_LOOP(i32)
# declare { i32, i32* }* @_POP_BLOCK()
# declare { i32, i32* }* @_LOAD_GLOBAL({ i32, i32* }*, [7 x i8]*)
# declare { i32, i32* }* @_CALL_FUNCTION(i32, { i32, i32* }*, { i32, i32* }*)
# declare { i32, i32* }* @_BINARY_SUBTRACT({ i32, i32* }*, { i32, i32* }*)
# declare { i32, i32* }* @_BINARY_ADD({ i32, i32* }*, { i32, i32* }*)
# declare void @_POP_TOP({ i32, i32* }*)
# declare { i32, i32* }* @_STORE_SUBSCR({ i32, i32* }*, { i32, i32* }*, { i32, i32* }*)

# ______________________________________________________________________

if __name__ == "__main__":
    print(llapi_module)

# ______________________________________________________________________
# End of llapi.py
