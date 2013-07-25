#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ______________________________________________________________________
# Module imports

import opcode

from llpython.bytetype import lc, lvoid, l_pyobj_p, l_pyobj_pp, lc_int, \
    lc_long, li1, li32, li8_ptr
from llpython.byte_translator import llpython

# ______________________________________________________________________
# Module data

llapi_module = lc.Module.new('llapi')

lfn = lc.Type.function

_UNARY_FN_ty = lfn(l_pyobj_p, [l_pyobj_p])

_BINARY_FN_ty = lfn(l_pyobj_p, [l_pyobj_p, l_pyobj_p])

llpy_null = lc.Constant.null(l_pyobj_p)

lltrue = lc.Constant.int(li1, 1)

llfalse = lc.Constant.int(li1, 0)

# ______________________________________________________________________
# Module functions

_REFCNT_FN_ty = lfn(lvoid, [l_pyobj_p])

@llpython(_REFCNT_FN_ty, llapi_module)
def __INCREF(obj):
    refcnt_p = gep(obj, (0, li32(0)))
    refcnt_p[0] += 1

@llpython(_REFCNT_FN_ty, llapi_module)
def _INCREF(obj):
    if obj != llpy_null:
        __INCREF(obj)

@llpython(_REFCNT_FN_ty, llapi_module)
def _DECREF(obj):
    if obj != llpy_null:
        refcnt_p = gep(obj, (0, li32(0)))
        refcnt = load(refcnt_p)
        if refcnt > 1:
            refcnt_p[0] -= 1
        else:
            Py_DecRef(obj)

# declare void @_DELETE_FAST(i1, { i32, i32* }**)

_DELETE_FAST_ty = lfn(lvoid, [l_pyobj_pp])
@llpython(_DELETE_FAST_ty, llapi_module)
def _DELETE_FAST(dest):
    if dest != l_pyobj_pp(0):
        tmp = load(dest)
        dest[0] = llpy_null
        _DECREF(tmp)

# declare { i32, i32* }* @_LOAD_FAST({ i32, i32* }**)

_LOAD_FAST_ty = lfn(l_pyobj_p, [l_pyobj_pp])
@llpython(_LOAD_FAST_ty, llapi_module)
def _LOAD_FAST(src):
    rv = llpy_null
    if src != l_pyobj_pp(0):
        rv = load(src)
        if rv != llpy_null:
            __INCREF(rv)
        # XXX else: raise unbound local error
    return rv

# declare void @_STORE_FAST({ i32, i32* }*, { i32, i32* }**)

_STORE_FAST_ty = lfn(lvoid, (l_pyobj_p, l_pyobj_pp))
@llpython(_STORE_FAST_ty, llapi_module)
def _STORE_FAST(src, dest):
    if dest != l_pyobj_pp(0):
        tmp = load(dest)
        dest[0] = src
        _DECREF(tmp)

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

def _mk_lc_int(val): return lc.Constant.int(lc_int, val)

PyCmp_LT = _mk_lc_int(opcode.cmp_op.index('<'))
PyCmp_LE = _mk_lc_int(opcode.cmp_op.index('<='))
PyCmp_EQ = _mk_lc_int(opcode.cmp_op.index('=='))
PyCmp_NE = _mk_lc_int(opcode.cmp_op.index('!='))
PyCmp_GT = _mk_lc_int(opcode.cmp_op.index('>'))
PyCmp_GE = _mk_lc_int(opcode.cmp_op.index('>='))
PyCmp_IN = _mk_lc_int(opcode.cmp_op.index('in'))
PyCmp_NOT_IN = _mk_lc_int(opcode.cmp_op.index('not in'))
PyCmp_IS = _mk_lc_int(opcode.cmp_op.index('is'))
PyCmp_IS_NOT = _mk_lc_int(opcode.cmp_op.index('is not'))
PyCmp_EXC_MATCH = _mk_lc_int(opcode.cmp_op.index('exception match'))

@llpython(lfn(l_pyobj_p, [lc_int, l_pyobj_p, l_pyobj_p]), llapi_module)
def _cmp_outcome(op, arg0, arg1):
    result = llfalse
    result_i = lc_int(0)
    if op == PyCmp_IS:
        result = arg0 == arg1
    elif op == PyCmp_IS_NOT:
        result = arg0 != arg1
    elif op == PyCmp_IN:
        result_i = PySequence_Contains(arg1, arg0)
        if result_i < 0:
            return llpy_null
        result = li1(result_i)
    elif op == PyCmp_NOT_IN:
        result_i = PySequence_Contains(arg1, arg0)
        if result_i < 0:
            return llpy_null
        result = ~li1(result_i)
    elif op == PyCmp_EXC_MATCH:
        # XXX: Generate warnings
        result = li1(PyErr_GivenExceptionMatches(arg0, arg1))
    else:
        return PyObject_RichCompare(arg0, arg1, op)
    return PyBool_FromLong(lc_long(result))

_COMPARE_OP_ty = lfn(l_pyobj_p, [lc_int, l_pyobj_p, l_pyobj_p])
@llpython(_COMPARE_OP_ty, llapi_module)
def _COMPARE_OP(op, arg0, arg1):
    result = llfalse
    slow = 0
    ret_val = llpy_null
    if (arg0 != llpy_null) and (arg1 != llpy_null):
        if _PyInt_CheckExact(arg0) and _PyInt_CheckExact(arg1):
            arg0_l = PyInt_AsLong(arg0)
            arg1_l = PyInt_AsLong(arg1)
            if op == PyCmp_LT:
                result = arg0 < arg1
            elif op == PyCmp_LE:
                result = arg0 <= arg1
            elif op == PyCmp_EQ:
                result = arg0 == arg1
            elif op == PyCmp_NE:
                result = arg0 != arg1
            elif op == PyCmp_GT:
                result = arg0 > arg1
            elif op == PyCmp_GE:
                result = arg0 >= arg1
            elif op == PyCmp_IS:
                result = arg0 == arg1
            elif op == PyCmp_IS_NOT:
                result = arg0 != arg1
            else:
                slow = 1
        else:
            slow = 1
        if slow != 0:
            ret_val = _cmp_outcome(op, arg0, arg1)
        else:
            ret_val = PyBool_FromLong(lc_long(result))
    _DECREF(arg0)
    _DECREF(arg1)
    return ret_val

# declare i1 @_POP_JUMP_IF_FALSE({ i32, i32* }*)

_POP_JUMP_IF_FALSE_ty = lfn(li1, [l_pyobj_p])
@llpython(_POP_JUMP_IF_FALSE_ty, llapi_module)
def _POP_JUMP_IF_FALSE(arg0):
    err = PyObject_IsTrue(arg0)
    _DECREF(arg0)
    return llfalse if err != 0 else lltrue

# declare { i32, i32* }* @_INPLACE_ADD({ i32, i32* }*, { i32, i32* }*)

_INPLACE_ADD_ty = _BINARY_FN_ty
@llpython(_INPLACE_ADD_ty, llapi_module)
def _INPLACE_ADD(arg0, arg1):
    ret_val = llpy_null
    if (arg0 != llpy_null) and (arg1 != llpy_null):
        if _PyInt_CheckExact(arg0) and _PyInt_CheckExact(arg1):
            arg0_i = PyInt_AsLong(arg0)
            arg1_i = PyInt_AsLong(arg1)
            result_i = arg0_i + arg1_i
            if ((result_i ^ arg0_i) < 0) and ((result_i ^ arg1_i) < 0):
                ret_val = PyNumber_InPlaceAdd(arg0, arg1)
            else:
                ret_val = PyInt_FromLong(result_i)
        elif li1(PyString_CheckExact(arg0)) and li1(PyString_CheckExact(arg1)):
            # XXX FIXME: implement string_concatenate
            ret_val = llpy_null
        else:
            ret_val = PyNumber_InPlaceAdd(arg0, arg1)
    _DECREF(arg0)
    _DECREF(arg1)
    return ret_val

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
