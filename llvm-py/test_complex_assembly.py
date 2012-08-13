#! /usr/bin/env python
# ______________________________________________________________________

import ctypes
import StringIO

import llvm.core as lc
import llvm.ee as le

import numba.translate as nt

SRC = '''
define { double, double } @prod_sum_fn_({ double, double } %coeff, { double, double } %inval, { double, double } %ofs) {
Entry:
  %0 = extractvalue { double, double } %coeff, 0
  %1 = extractvalue { double, double } %coeff, 1
  %2 = extractvalue { double, double } %inval, 0
  %3 = extractvalue { double, double } %inval, 1
  %4 = fmul double %0, %2
  %5 = fmul double %1, %3
  %6 = fsub double %4, %5
  %7 = fmul double %1, %2
  %8 = fmul double %0, %3
  %9 = fadd double %7, %8
  %10 = insertvalue { double, double } undef, double %6, 0
  %11 = insertvalue { double, double } %10, double %9, 1
  %12 = extractvalue { double, double } %11, 0
  %13 = extractvalue { double, double } %11, 1
  %14 = extractvalue { double, double } %ofs, 0
  %15 = extractvalue { double, double } %ofs, 1
  %16 = fadd double %12, %14
  %17 = fadd double %13, %15
  %18 = insertvalue { double, double } undef, double %16, 0
  %19 = insertvalue { double, double } %18, double %17, 1
  ret { double, double } %19
}
@__STR_0 = internal global [11 x i8] c"debugout: \\00"
@__STR_1 = internal global [24 x i8] c"prod_sum_fn(): coeff = \\00"
@__STR_2 = internal global [11 x i8] c"(%lf%+lfj)\\00"
@__STR_3 = internal global [11 x i8] c", inval = \\00"
@__STR_4 = internal global [9 x i8] c", ofs = \\00"
@__STR_5 = internal global [2 x i8] c"\\0A\\00"
@__STR_6 = internal global [19 x i8] c"prod_sum_fn() ==> \\00"

define { double, double } @prod_sum_fn({ double, double } %coeff, { double, double } %inval, { double, double } %ofs) {
Entry:
  %0 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_0, i32 0, i32 0))
  %1 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([24 x i8]* @__STR_1, i32 0, i32 0))
  %2 = extractvalue { double, double } %coeff, 0
  %3 = extractvalue { double, double } %coeff, 1
  %4 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_2, i32 0, i32 0), double %2, double %3)
  %5 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_3, i32 0, i32 0))
  %6 = extractvalue { double, double } %inval, 0
  %7 = extractvalue { double, double } %inval, 1
  %8 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_2, i32 0, i32 0), double %6, double %7)
  %9 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([9 x i8]* @__STR_4, i32 0, i32 0))
  %10 = extractvalue { double, double } %ofs, 0
  %11 = extractvalue { double, double } %ofs, 1
  %12 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_2, i32 0, i32 0), double %10, double %11)
  %13 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([2 x i8]* @__STR_5, i32 0, i32 0))
  %14 = extractvalue { double, double } %coeff, 0
  %15 = extractvalue { double, double } %coeff, 1
  %16 = extractvalue { double, double } %inval, 0
  %17 = extractvalue { double, double } %inval, 1
  %18 = fmul double %14, %16
  %19 = fmul double %15, %17
  %20 = fsub double %18, %19
  %21 = fmul double %15, %16
  %22 = fmul double %14, %17
  %23 = fadd double %21, %22
  %24 = insertvalue { double, double } undef, double %20, 0
  %25 = insertvalue { double, double } %24, double %23, 1
  %26 = extractvalue { double, double } %25, 0
  %27 = extractvalue { double, double } %25, 1
  %28 = extractvalue { double, double } %ofs, 0
  %29 = extractvalue { double, double } %ofs, 1
  %30 = fadd double %26, %28
  %31 = fadd double %27, %29
  %32 = insertvalue { double, double } undef, double %30, 0
  %33 = insertvalue { double, double } %32, double %31, 1
  %34 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_0, i32 0, i32 0))
  %35 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([19 x i8]* @__STR_6, i32 0, i32 0))
  %36 = extractvalue { double, double } %33, 0
  %37 = extractvalue { double, double } %33, 1
  %38 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([11 x i8]* @__STR_2, i32 0, i32 0), double %36, double %37)
  %39 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([2 x i8]* @__STR_5, i32 0, i32 0))
  ret { double, double } %33
}

declare i32 @printf(i8*, ...)

define void @prod_sum_fn_wrap( { double, double }* sret %out, { double, double } %coeff, { double, double } %inval, { double, double } %ofs ) {
entry:
  %0 = call { double, double } @prod_sum_fn_( { double, double } %coeff, { double, double } %inval, { double, double } %ofs )
  %1 = extractvalue { double, double } %0, 0
  %2 = extractvalue { double, double } %0, 1
  %3 = getelementptr inbounds { double, double }* %out, i32 0, i32 0
  %4 = getelementptr inbounds { double, double }* %out, i32 0, i32 1
  store double %1, double* %3
  store double %2, double* %4
  ret void
}
'''

m = lc.Module.from_assembly(StringIO.StringIO(SRC))
print m
ee = le.ExecutionEngine.new(m)
prod_sum_fn_ptr = ee.get_pointer_to_function(m.get_function_named('prod_sum_fn_'))
prod_sum_fn_wrap_ptr = ee.get_pointer_to_function(m.get_function_named('prod_sum_fn_wrap'))

cplx = nt.convert_to_ctypes('D')
prototype = cplx.make_ctypes_prototype_wrapper(ctypes.CFUNCTYPE(cplx, cplx, cplx, cplx))
prod_sum_fn = prototype(prod_sum_fn_ptr)
prod_sum_fn_wrap = prototype(prod_sum_fn_wrap_ptr)

import numpy, itertools

def test32 ():
    rrng = numpy.arange(-1., 1.0000001, 0.5)
    irng = rrng * 1.j
    ri, ii = numpy.mgrid[:len(rrng),:len(irng)]
    rng = (rrng[ri] + irng[ii]).flatten()
    for a, x, b in itertools.product(rng, repeat = 3):
        print a, x, b, a * x + b, prod_sum_fn_wrap(a, x, b)

def test32_1 ():
    rng = numpy.arange(-1., 1.0000001, 0.5)
    for ar, ai, xr, xi, br, bi in itertools.product(rng, repeat = 6):
        # So the call to prod_sum_fn() will corrupt the stack on a
        # 32-bit system, causing the next expression to generate an
        # invalid multiply.  I assume calling prod_sum_fn_wrap() on a
        # 64-bit system will also corrupt the stack?!
        ai * 1j
        a = numpy.complex128(ar + ai * 1j)
        x = numpy.complex128(xr + xi * 1j)
        b = numpy.complex128(br + bi * 1j)
        print "a = %r, x = %r, b = %r, a * x + b = %r, => %r" % (
            a, x, b, a * x + b, prod_sum_fn_wrap(a, x, b))
        print prod_sum_fn_wrap(a, x, b)

if __name__ == "__main__":
    test32()

# ______________________________________________________________________
# End of test_complex_assembly.py
