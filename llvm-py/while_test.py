#! /usr/bin/env python
# ______________________________________________________________________
'''while_test.py

This corresponds to some LLVM code similar to what I'd want Numba to
generate for a simple while loop.

I've cheated somewhat and used clang to translate the following:
______________________________________________________________________
double foo (int max_index, double * indexable)
{
  int index = 0;
  double acc = 0.;

  while(index<max_index)
  {
    acc += indexable[index];
  }

  return acc;
}
______________________________________________________________________
The result was:
______________________________________________________________________
define double @foo(i32 %max_index, double* %indexable) nounwind uwtable {
entry:
  %max_index.addr = alloca i32, align 4
  %indexable.addr = alloca double*, align 8
  %index = alloca i32, align 4
  %acc = alloca double, align 8
  store i32 %max_index, i32* %max_index.addr, align 4
  store double* %indexable, double** %indexable.addr, align 8
  store i32 0, i32* %index, align 4
  store double 0.000000e+00, double* %acc, align 8
  br label %while.cond

while.cond:                                       ; preds = %while.body, %entry
  %0 = load i32* %index, align 4
  %1 = load i32* %max_index.addr, align 4
  %cmp = icmp slt i32 %0, %1
  br i1 %cmp, label %while.body, label %while.end

while.body:                                       ; preds = %while.cond
  %2 = load i32* %index, align 4
  %idxprom = sext i32 %2 to i64
  %3 = load double** %indexable.addr, align 8
  %arrayidx = getelementptr inbounds double* %3, i64 %idxprom
  %4 = load double* %arrayidx, align 8
  %5 = load double* %acc, align 8
  %add = fadd double %5, %4
  store double %add, double* %acc, align 8
  br label %while.cond

while.end:                                        ; preds = %while.cond
  %6 = load double* %acc, align 8
  ret double %6
}
______________________________________________________________________

Interested parties may compare what I've done to the above.
'''
# ______________________________________________________________________
# Module imports

import array
import llvm.core as lc
import llvm.ee as le

# ______________________________________________________________________
# Main (test/demo) routine

def main (*args, **kws):
    m = lc.Module.new('whiletestmod')
    i64 = lc.Type.int(64)
    f64 = lc.Type.double()
    f64p = lc.Type.pointer(f64)
    tf_ty = lc.Type.function(f64, (i64, f64p))
    tf = lc.Function.new(m, tf_ty, 'whiletestfn')
    arg0 = tf.args[0]; arg0.name = 'max_index'
    arg1 = tf.args[1]; arg1.name = 'indexable'
    entry = tf.append_basic_block('entry')
    loopin = tf.append_basic_block('loopin')
    loopbody = tf.append_basic_block('loopbody')
    ret = tf.append_basic_block('return')

    b = lc.Builder.new(entry)
    index = b.alloca(i64, 'index')
    acc = b.alloca(f64, 'acc')
    b.store(lc.Constant.int(i64,0), index)
    b.store(lc.Constant.real(f64, 0.), acc)
    b.branch(loopin)

    b.position_at_end(loopin)
    ival = b.load(index, 'tmp')
    index_cmp = b.icmp(lc.IPRED_SLT, ival, arg0, 'tmp')
    b.cbranch(index_cmp, loopbody, ret)

    b.position_at_end(loopbody)
    ival = b.load(index, 'tmp')
    accval = b.load(acc, 'tmp')
    addr_at_index = b.gep(arg1, (ival,), 'tmp')
    val_at_index = b.load(addr_at_index, 'tmp')
    accup = b.fadd(accval, val_at_index, 'tmp')
    b.store(accup, acc)
    iup = b.add(ival, lc.Constant.int(i64, 1), 'tmp')
    b.store(iup, index)
    b.branch(loopin)

    b.position_at_end(ret)
    rval = b.load(acc, 'tmp')
    b.ret(rval)

    print "_" * 70
    print m
    print "_" * 70

    myarr = array.array('d', [1,2,3])
    max_index = le.GenericValue.int(i64, 3)
    indexable = le.GenericValue.pointer(f64p, myarr.buffer_info()[0])
    ee = le.ExecutionEngine.new(m)
    result = ee.run_function(tf, [max_index, indexable]).as_real(f64)
    assert result == 6.
    print result

    return m

# ______________________________________________________________________

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of while_test.py
