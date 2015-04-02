# Another incremental improvement: Calling user ufuncs from njit...

from numba import *
import numpy as np

# It all starts so simply...

@vectorize([float64(float64, float64)])
def myuadd(a0, a1):
    return a0 + a1

# And then we start hacking the ufunc into the type system...

from numba import types, typing
from numba.targets import npyimpl
from numba.typing.npydecl import builtin_global, Numpy_rules_ufunc
_any = types.Any

def _numba_ufunc(ufunc):
    class typing_class(Numpy_rules_ufunc):
        key = ufunc
    typing_class.__name__ = "resolve_{0}".format(ufunc.__name__)
    return types.Function(typing_class)

myuadd_ty = _numba_ufunc(myuadd)

# Using the following decorator on a njit function gets us to the
# lower phase, where it doesn't know how to lower the ufunc...

def _patch_typingctx(nb_fn):
    nb_fn.typingctx._insert_global(myuadd, myuadd_ty)
    return nb_fn

# ...so we can do that too, except that ufunc_db doesn't know how to
# implement the element-wise function... so we fake it.  Here we
# basically get into the crux of why calling into existing ufunc's is
# hard: once you translate from Python to a UFunc, you can't get the
# Python code back out for dynamic compilation.  Here we just
# implement the function a second time, but decorate it differently:

@njit
def _myuadd_impl(a0, a1):
    return a0 + a1

class _MyUAdd_Kernel(npyimpl._Kernel):
    "Mostly borrowed from numba.targets.npyimpl._KernelImpl."
    def __init__(self, context, builder, outer_sig):
        super(_MyUAdd_Kernel, self).__init__(context, builder, outer_sig)
        # Note ufunc_find_matching_loop() is actually in numba.numpy_support
        loop = npyimpl.ufunc_find_matching_loop(
            myuadd, outer_sig.args + (outer_sig.return_type,))
        self.inner_sig = typing.signature(*(loop.outputs + loop.inputs))
        _myuadd_impl_closure = _myuadd_impl.compile(self.inner_sig)
        self.fn = context.get_function(_myuadd_impl_closure, self.inner_sig)

    def generate(self, *args):
        isig = self.inner_sig
        osig = self.outer_sig
        cast_args = [self.cast(val, inty, outty)
                     for val, inty, outty in zip(args, osig.args, isig.args)]
        res = self.fn(self.builder, cast_args)
        return self.cast(res, isig.return_type, osig.return_type)

def _myuadd_lower(context, builder, sig, args):
    return npyimpl.numpy_ufunc_kernel(context, builder, sig, args,
                                      _MyUAdd_Kernel)

def _patch_targetctx(nb_fn):
    nb_fn.targetctx.insert_func_defn([(_myuadd_lower, [
        (myuadd, _any(_any, _any, types.Kind(types.Array)))])])
    return nb_fn

def _patch_contexts(nb_fn):
    return _patch_targetctx(_patch_typingctx(nb_fn))

# Great, so let's try it out...

@_patch_contexts
@njit
def myadd(a0, a1, o0):
    myuadd(a0, a1, o0)

X = np.linspace(0,1.9,20)

X0 = X[:10]
X1 = X[10:]
out0 = np.zeros(10)
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
