# Building with:
# cython exceptionlib.pyx; gcc -I /usr/include/python2.7 -c exceptionlib.c; gcc -shared exceptionlib.o -o exceptionlib.so

cimport libc.setjmp
cimport libc.stdlib

cpdef get_sizeof_jmp_buf():
     return sizeof(libc.setjmp.jmp_buf)

cdef void * crnt_ec = NULL

cdef class ExceptionContext:
     cdef libc.setjmp.jmp_buf * buf_p
     cdef void * prev_p

     def __cinit__(self):
         self.buf_p = <libc.setjmp.jmp_buf *>libc.stdlib.malloc(
             sizeof(libc.setjmp.jmp_buf))
         self.prev_p = NULL
         if self.buf_p is NULL:
             raise MemoryError()

     def __dealloc__(self):
         if self.buf_p is not NULL:
             libc.stdlib.free(<void *>self.buf_p)

     cpdef register(self):
         global crnt_ec
         self.prev_p = crnt_ec
         crnt_ec = <void *>self

     cpdef deregister(self):
         global crnt_ec
         if crnt_ec is not <void *>self:
              raise ValueError()
         crnt_ec = self.prev_p
