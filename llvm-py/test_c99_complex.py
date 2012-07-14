#! /usr/bin/env python
# ______________________________________________________________________
'''test_c99_complex.py

Quick check to see if clang supports C99 complex numbers, and how it
handles them.
'''
# ______________________________________________________________________

import inline_c as ic
import llvm.core as lc
import llvm.ee as le

# ______________________________________________________________________

with open('test_c99_complex.c') as cfile:
    TEST_C_SRC = cfile.read()

# ______________________________________________________________________

def main (*args):
    SKIP_CLANG = False
    args = list(args)
    if '-a' in args:
        args.remove('-a')
        SKIP_CLANG = True
    if not SKIP_CLANG:
        lmod = ic.llvm_module_from_c_source(TEST_C_SRC, *args)
        print lmod
        ee = le.ExecutionEngine.new(lmod)
        ee.run_static_ctors()
        ee.run_function(lmod.get_function_named('test_fn'), [])
    with open('test_c99_complex.ll') as llfile:
        lmod2 = lc.Module.from_assembly(llfile)
    ee2 = le.ExecutionEngine.new(lmod2)
    ee2.run_static_ctors()
    ee2.run_function(lmod2.get_function_named('test_fn'), [])

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of test_c99_complex.py
