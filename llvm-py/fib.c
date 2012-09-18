/* Fibonacci function from Bitey documentation.

   $ clang -emit-llvm -S fib.c
   $ python
   >>> import nobitey
   >>> nobitey.NoBiteyLoader.install()
   >>> import fib
   >>> fib.fib(38)
   39088169
   >>>
*/

int fib (int n) {
    if (n < 3) {
       return 1;
    } else {
       return fib(n-1) + fib(n-2);
    }
}
