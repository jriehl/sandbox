import llvm.core as lc
import ctypes

class _stm(ctypes.Structure):
    pass

stm_ty = ctypes.POINTER(_stm)

class _exp(ctypes.Structure):
    _fields_ = [('foo', ctypes.c_void_p)]

exp_ty = ctypes.POINTER(_exp)

class _union_0_0(ctypes.Structure):
    _fields_ = [('stm1', stm_ty), ('stm2', stm_ty)]

class _union_0_1(ctypes.Structure):
    _fields_ = [('id', ctypes.c_char_p), ('exp', exp_ty)]

class _union_0_2(ctypes.Structure):
    _fields_ = [('exps', ctypes.POINTER(exp_ty))]

class _union_0(ctypes.Union):
    _fields_ = [('Compound', _union_0_0), ('Assign', _union_0_1),
                ('Print', _union_0_2)]

_stm._fields_ = [('kind', ctypes.c_int), ('value', _union_0)]

DEFAULT_TY_MAP={
    ctypes.c_int: lc.Type.int(8 * ctypes.sizeof(ctypes.c_int)),
    ctypes.c_long: lc.Type.int(8 * ctypes.sizeof(ctypes.c_long)),
    ctypes.c_longlong: lc.Type.int(8 * ctypes.sizeof(ctypes.c_longlong)),
    ctypes.c_void_p: lc.Type.pointer(lc.Type.int(8)),
    ctypes.c_char_p: lc.Type.pointer(lc.Type.int(8)),
}

class CTypesToLLVM(object):
    def __init__(self, ty_map=None):
        if ty_map is None:
            ty_map = DEFAULT_TY_MAP.copy()
        self.ty_map = ty_map

    def ctypes_to_llvm(self, ctype):
        ty_map = self.ty_map
        if ctype in ty_map:
            rv = ty_map[ctype]
        else:
            ctypetype = type(ctype)
            # ______________________________
            if ctypetype == type(ctypes.Structure):
                rv = lc.Type.opaque(ctype.__name__)
                ty_map[ctype] = rv
                rv.set_body(tuple(self.ctypes_to_llvm(field_ty)
                                  for _, field_ty in ctype._fields_))
            # ______________________________
            elif ctypetype == type(ctypes.Union):
                rv = lc.Type.opaque(ctype.__name__)
                ty_map[ctype] = rv
                fields = [(ctypes.sizeof(field_ty),
                           self.ctypes_to_llvm(field_ty))
                          for _, field_ty in ctype._fields_]
                max_field = max(fields)
                rv.set_body((max_field[1],))
            # ______________________________
            elif ctypetype == type(ctypes._Pointer):
                rv = lc.Type.pointer(self.ctypes_to_llvm(ctype._type_))
                ty_map[ctype] = rv
            # ______________________________
            else:
                raise ValueError(ctype)
        return rv

def main():
    import pprint
    converter = CTypesToLLVM()
    print(converter.ctypes_to_llvm(stm_ty))
    pprint.pprint(dict((k, str(v)) for k, v in converter.ty_map.items()))

if __name__ == "__main__":
    main()
