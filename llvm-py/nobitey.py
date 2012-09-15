#! /usr/bin/env python
# ______________________________________________________________________

import llvm.core as lc
import llvm.ee as le

from numba import llvm_types
from numba.translate import _LLVMModuleUtils as LLVMModuleUtils

LLVM_TO_INT_PARSE_STR_MAP = {
    8 : 'b',
    16 : 'h', 
    32 : 'i', # Note that on 32-bit systems sizeof(int) == sizeof(long)
    64 : 'L', # Seeing sizeof(long long) == 8 on both 32 and 64-bit platforms
}

LLVM_TO_PARSE_STR_MAP = {
    lc.TYPE_FLOAT : 'f',
    lc.TYPE_DOUBLE : 'd',
}

# ______________________________________________________________________

class NoBitey (object):
    def __init__ (self, target_module = None, type_aliases = None):
        if target_module is None:
            target_module = lc.Module.new('NoBitey_%d' % id(self))
        if type_aliases is None:
            type_aliases = {}
        self.target_module = target_module
        self.type_aliases = type_aliases

    def _build_parse_string (self, llvm_type, type_annotations = None):
        kind = llvm_type.kind
        if kind == lc.TYPE_INTEGER:
            ret_val = LLVM_TO_INT_PARSE_STR_MAP[llvm_type.width]
        elif kind in LLVM_TO_PARSE_STR_MAP:
            ret_val = LLVM_TO_PARSE_STR_MAP[kind]
        else:
            raise TypeError('Unsupported LLVM type: %s' % str(llvm_type))
        return ret_val

    def build_parse_string (self, llvm_types, type_annotations = None):
        """Given a set of LLVM types, return a string for parsing
        them via PyArg_ParseTuple."""
        return ''.join((self._build_parse_string(ty, type_annotations)
                        for ty in llvm_types))

    def build_wrapper_function (self, llvm_function, type_annotations = None):
        _pyobj_p = llvm_types._pyobject_head_struct_p
        _char_p = lc.Type.pointer(llvm_types._int8)
        self.crnt_function = self.target_module.add_function(
            lc.Type.function(_pyobj_p, (_pyobj_p, _pyobj_p)),
            llvm_function.name + "_wrapper")
        entry_block = self.crnt_function.append_basic_block('entry')
        args_ok_block = self.crnt_function.append_basic_block('args_ok')
        exit_block = self.crnt_function.append_basic_block('exit')
        _int32_zero = lc.Constant.int(llvm_types._int32, 0)
        _Py_BuildValue = self.target_module.get_or_insert_function(
            lc.Type.function(_pyobj_p, [_char_p], True), 'Py_BuildValue')
        _PyArg_ParseTuple = self.target_module.get_or_insert_function(
            lc.Type.function(llvm_types._int32, [_char_p], True),
            'PyArg_ParseTuple')
        # __________________________________________________
        # entry:
        builder = lc.Builder.new(entry_block)
        arg_types = llvm_function.type.pointee.args
        parse_str = builder.gep(
            LLVMModuleUtils.get_string_constant(
                self.target_module,
                self.build_parse_string(arg_types, type_annotations)),
            [_int32_zero, _int32_zero])
        parse_args = [builder.alloca(arg_ty) for arg_ty in arg_types]
        parse_args.insert(0, parse_str)
        parse_result = builder.call(_PyArg_ParseTuple, parse_args)
        builder.cbranch(builder.icmp(lc.ICMP_NE, parse_result, _int32_zero),
                        args_ok_block, exit_block)
        # __________________________________________________
        # args_ok:
        builder = lc.Builder.new(args_ok_block)
        target_args = [builder.load(parse_arg) for parse_arg in parse_args[1:]]
        result = builder.call(llvm_function, target_args)
        build_str = builder.gep(
            LLVMModuleUtils.get_string_constant(
                self.target_module,
                self._build_parse_string(result.type, type_annotations)),
            [_int32_zero, _int32_zero])
        py_result = builder.call(_Py_BuildValue, [build_str, result])
        builder.branch(exit_block)
        # __________________________________________________
        # exit:
        builder = lc.Builder.new(exit_block)
        rval = builder.phi(llvm_types._pyobject_head_struct_p)
        rval.add_incoming(lc.Constant.null(llvm_types._pyobject_head_struct_p),
                          entry_block)
        rval.add_incoming(py_result, args_ok_block)
        builder.ret(rval)
        return self.crnt_function

# ______________________________________________________________________

def mk_add_42 (llvm_module, at_type = llvm_types._intp):
    f = llvm_module.add_function(
        lc.Type.function(at_type, [at_type]), 'add_42_%s' % str(at_type))
    block = f.append_basic_block('entry')
    builder = lc.Builder.new(block)
    if at_type.kind == lc.TYPE_INTEGER:
        const_42 = lc.Constant.int(at_type, 42)
        add = builder.add
    elif at_type.kind in (lc.TYPE_FLOAT, lc.TYPE_DOUBLE):
        const_42 = lc.Constant.real(at_type, 42.)
        add = builder.fadd
    else:
        raise TypeError('Unsupported type: %s' % str(at_type))
    builder.ret(add(f.args[0], const_42))
    return f

# ______________________________________________________________________

if __name__ == "__main__":
    # Build up a module.
    m = lc.Module.new('test')
    nobiter = NoBitey()
    wfs = []
    for ty in (llvm_types._int32, llvm_types._int64,
               llvm_types._float, llvm_types._double):
        f = mk_add_42(m, ty)
        wf = nobiter.build_wrapper_function(f)
        wfs.append(wf)

    print m
    print nobiter.target_module
    print nobiter.target_module.to_native_assembly()

    # Now try running the generated wrappers.
    from pyaddfunc import pyaddfunc
    import llvm.ee as le
    ee = le.ExecutionEngine.new(nobiter.target_module)
    for wf in wfs:
        py_wf = pyaddfunc(f.name, ee.get_pointer_to_function(wf))
        for i in xrange(42):
            assert py_wf(i) == (i + 42)

# ______________________________________________________________________
# End of nobitey.py
