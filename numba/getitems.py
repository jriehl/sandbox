#!/bin/env python
# ______________________________________________________________________
'''Harness used to help develop getitem(buffer, intp) for buffers with
more than one dimension.

We need to use a rudimentary code generator to specialize the indexing
function at various types.
'''
# ______________________________________________________________________
import numba as nb
from numba import typeinfer as nb_tyinf
import numpy as np
import despatcher as de
import pdb

# ______________________________________________________________________

def index_i(X, i):
    '''This was the original test function.  It doesn't type check because
    the compiler isn't smart enough to realize that the loop protects
    against the case where X is the return value.
    '''
    while X.ndim >= 1:
        X = X[i]
    return X

# Having realized our mistake...

def format_stmt(stmt, indent=0, indent_str=' '):
    '''...how many different kinds of this function are in the wild?
    '''
    if isinstance(stmt, tuple):
        return '{}{}\n{}'.format(indent_str * indent, stmt[0],
                                 ''.join(format_stmt(sub_stmt, indent+1,
                                                     indent_str)
                                         for sub_stmt in stmt[1]))
    return '{}{}\n'.format(indent_str * indent, stmt)

def gen_index_i_at_dim(ndim):
    return ('def index_{}i(X, i):'.format(ndim),
            ['X = X[i]' for _ in range(ndim)] +
            ['return X'])

# ______________________________________________________________________
# Our goal?

def test(*args):
    exec format_stmt(gen_index_i_at_dim(2))
    nb_index_2i = nb.njit(index_2i)
    Y = np.arange(4).reshape(2,2)
    assert nb_index_2i(Y, 0) == 0
    assert nb_index_2i(Y, 1) == 3
    assert nb_index_2i(Y, -1) == 3
    return nb_index_2i

# ______________________________________________________________________
# Main routine...

def main(*args):
    if len(args):
        test(*args)
    else:
        test_X = np.ones((5,5,5))
        index_i_test_sig = nb.typeof(test_X), nb.intp
        dobj = de.Despatcher()
        exec format_stmt(gen_index_i_at_dim(test_X.ndim))
        pipeline = dobj.get_and_prime_pipeline(index_3i, index_i_test_sig)
        pipeline.stage_analyze_bytecode()
         # Originally had to get this to type here:
        pipeline.stage_nopython_frontend()
        pipeline.stage_annotate_type()
        # Then had to write code generation here:
        pipeline.stage_nopython_backend()

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of getitems.py
