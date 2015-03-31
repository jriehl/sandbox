# Another incremental improvement: Calling ufuncs from njit...

from numba import *
import numpy as np

@vectorize([float64(float64, float64)])
def myuadd(a0, a1):
    return a0 + a1

from numba import types
from numba.typing.npydecl import builtin_global, Numpy_rules_ufunc

def _numba_ufunc(ufunc):
    class typing_class(Numpy_rules_ufunc):
        key = ufunc
    typing_class.__name__ = "resolve_{0}".format(ufunc.__name__)
    ty = types.Function(typing_class)
    builtin_global(ufunc, ty)
    return ty

myuadd_ty = _numba_ufunc(myuadd)

@njit
def myadd(a0, a1, o0):
    myuadd(a0, a1, o0)

# The following gets us to the lower phase where it doesn't know how
# to lower the ufunc...
myadd.typingctx._insert_global(myuadd, myuadd_ty)

X = np.linspace(0,1.9,20)

X0 = X[:10]
X1 = X[10:]
out0 = np.zeros(10)
import pdb; pdb.set_trace()
myadd(X0,X1,out0)
assert np.all(X0 + X1 == out0)

Y0 = X0.reshape((2,5))
Y1 = X1.reshape((2,5))
out1 = np.zeros((2,5))
myadd(Y0,Y1,out1)
assert np.all(Y0 + Y1 == out1)

Y2 = X1[:5]
out2 = np.zeros((2,5))
myadd(Y0,Y2,out2)
assert np.all(Y0 + Y2 == out2)

