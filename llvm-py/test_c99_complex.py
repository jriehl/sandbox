#! /usr/bin/env python
# ______________________________________________________________________
'''test_c99_complex.py

Quick check to see if clang supports C99 complex numbers, and how it
handles them.
'''
# ______________________________________________________________________

import inline_c as ic

# ______________________________________________________________________

TEST_SRC = '''#include <stdio.h>
#include <complex.h>

double complex cidentity(double complex in_val)
{
    return in_val;
}

void test_fn (void)
{
    double complex v = cidentity(4.+3.j);

    printf("%lg %lg", creal(v), cimag(v));
}
'''

# ______________________________________________________________________

def main (*args):
    lmod = ic.llvm_module_from_c_source(TEST_SRC, *args)
    print lmod

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of test_c99_complex.py
