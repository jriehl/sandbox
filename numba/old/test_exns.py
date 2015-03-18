import logging; logging.getLogger().setLevel(0)
import numba

def init(): print("init")

def deinit(): print("deinit")

def do_something(): raise Exception('Life is pain')

def handle(exn): print("handled %r" % exn)

@numba.jit(numba.void())
def testfn0():
    init()
    deinit()

'''
This generates the following:

define void @__numba_specialized_0___main___2E_testfn0() {
entry:
  %tuple_result = tail call { i32, i32* }* (i32, ...)* @PyTuple_Pack(i32 0)
  %0 = icmp eq { i32, i32* }* %tuple_result, null
  br i1 %0, label %cleanup_label, label %"no_error_13:0"

cleanup_label:                                    ; preds = %"no_error_13:05", %entry, %"no_error_13:0", %"no_error_13:01"
  %1 = phi { i32, i32* }* [ %tuple_result4, %"no_error_13:05" ], [ null, %entry ], [ null, %"no_error_13:0" ], [ null, %"no_error_13:01" ]
  %2 = phi { i32, i32* }* [ %7, %"no_error_13:05" ], [ null, %entry ], [ null, %"no_error_13:0" ], [ null, %"no_error_13:01" ]
  %3 = phi { i32, i32* }* [ %4, %"no_error_13:05" ], [ null, %entry ], [ null, %"no_error_13:0" ], [ %4, %"no_error_13:01" ]
  tail call void @Py_XDECREF({ i32, i32* }* %tuple_result)
  tail call void @Py_XDECREF({ i32, i32* }* %3)
  tail call void @Py_XDECREF({ i32, i32* }* %1)
  tail call void @Py_XDECREF({ i32, i32* }* %2)
  ret void

"no_error_13:0":                                  ; preds = %entry
  %4 = tail call { i32, i32* }* @PyObject_Call({ i32, i32* }* inttoptr (i32 -1217161036 to { i32, i32* }*), { i32, i32* }* %tuple_result, { i32, i32* }* null)
  %5 = icmp eq { i32, i32* }* %4, null
  br i1 %5, label %cleanup_label, label %"no_error_13:01"

"no_error_13:01":                                 ; preds = %"no_error_13:0"
  %tuple_result4 = tail call { i32, i32* }* (i32, ...)* @PyTuple_Pack(i32 0)
  %6 = icmp eq { i32, i32* }* %tuple_result4, null
  br i1 %6, label %cleanup_label, label %"no_error_13:05"

"no_error_13:05":                                 ; preds = %"no_error_13:01"
  %7 = tail call { i32, i32* }* @PyObject_Call({ i32, i32* }* inttoptr (i32 163664140 to { i32, i32* }*), { i32, i32* }* %tuple_result4, { i32, i32* }* null)
  br label %cleanup_label
}

Would like it to be like this:

define void @__numba_specialized_0___main___2E_testfn0() {
entry:
  %YYY = alloca [164 x i8]*, align 4
  %.sub1 = getelementptr inbounds [164 x i8]* %YYY, i32 0, i32 0
  call void @numba_enter_handler(i8* %.sub1)
  %jmpres = call i32 @sigsetjmp(i8* %.sub1, i32 0)
  %firsttime = icmp eq i32 %jmpres, 0
  br i1 %firsttime, label %entry0, label %cleanup_label

entry0:
  %tuple_result = tail call { i32, i32* }* (i32, ...)* @NumbaPyTuple_Pack(i32 0)
  %4 = tail call { i32, i32* }* @NumbaPyObject_Call({ i32, i32* }* inttoptr (i32 -1217161036 to { i32, i32* }*), { i32, i32* }* %tuple_result, { i32, i32* }* null)
  %tuple_result4 = tail call { i32, i32* }* (i32, ...)* @NumbaPyTuple_Pack(i32 0)
  %7 = tail call { i32, i32* }* @NumbaPyObject_Call({ i32, i32* }* inttoptr (i32 163664140 to { i32, i32* }*), { i32, i32* }* %tuple_result4, { i32, i32* }* null)
  br label %cleanup_label

cleanup_label:                                    ; preds = %entry, %entry0
  %XXX = phi { i32, i32* }* [ %tuple_result, %entry0 ], [ null, %entry ]
  %1 = phi { i32, i32* }* [ %tuple_result4, %entry0 ], [ null, %entry ]
  %2 = phi { i32, i32* }* [ %7, %entry0 ], [ null, %entry ]
  %3 = phi { i32, i32* }* [ %4, %entry0 ], [ null, %entry ]
  tail call void @Py_XDECREF({ i32, i32* }* %tuple_result)
  tail call void @Py_XDECREF({ i32, i32* }* %3)
  tail call void @Py_XDECREF({ i32, i32* }* %1)
  tail call void @Py_XDECREF({ i32, i32* }* %2)
  call void @numba_pop_handler()
  br i1 %firsttime, label %no_reraise, label %reraise

reraise:
  call void @numba_reraise()
  unreachable

no_reraise:
  ret void
}

XXX This doesn't work!!! Going to have to use stack allocated
variables, not SSA variables, since the PHI nodes will set everything
to null if an exception is raised.
'''

print(testfn0.lfunc)

@numba.jit(numba.void())
def testfn():
    try:
        init()
    finally:
        deinit()

@numba.jit(numba.void())
def testfn2():
    try:
        init()
        do_something()
    except Exception as e:
        handle(e)
    finally:
        deinit()

