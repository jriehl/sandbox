#! /usr/bin/env python
# ______________________________________________________________________

import ctypes

import llvm.core as lc

# ______________________________________________________________________

lvoid = lc.Type.void()
li1 = lc.Type.int(1)
li8 = lc.Type.int(8)
li16 = lc.Type.int(16)
li32 = lc.Type.int(32)
li64 = lc.Type.int(64)
lsize_t = lc.Type.int(
    ctypes.sizeof(getattr(ctypes, 'c_ssize_t',
                          getattr(ctypes, 'c_size_t'))) * 8 )
lfloat = lc.Type.float()
ldouble = lc.Type.double()
li8_ptr = lc.Type.pointer(li8)

strlen = lc.Type.function(lsize_t, (li8_ptr,))
strncpy = lc.Type.function(li8_ptr, (li8_ptr, li8_ptr, lsize_t))
strndup = lc.Type.function(li8_ptr, (li8_ptr, lsize_t))
malloc = lc.Type.function(li8_ptr, (lsize_t,))
free = lc.Type.function(lvoid, (li8_ptr,))

# ______________________________________________________________________
# End of bytetype.py
