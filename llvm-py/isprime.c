/* Another test file copied from the Bitey documentation.

   Example results:

   $ clang -O3 -emit-llvm -S isprime.c
   $ gcc -O3 -shared isprime.c -o isprime.so
   $ python
   Python 2.7.2+ (default, Oct  4 2011, 20:03:08) 
   [GCC 4.6.1] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import nobitey; nobitey.NoBiteyLoader.install()
   >>> from isprime import isprime as isprime1
   >>> import ctypes
   >>> ex = ctypes.cdll.LoadLibrary("./isprime.so")
   >>> isprime2 = ex.isprime
   >>> isprime2.argtypes=(ctypes.c_int,)
   >>> isprime2.restype=ctypes.c_int
   >>> from timeit import timeit
   >>> timeit("isprime1(3)","from __main__ import isprime1")
   0.35082483291625977
   >>> timeit("isprime2(3)", "from __main__ import isprime2")
   1.2938711643218994
   >>> timeit("isprime1(10143937)", "from __main__ import isprime1")
   21.533010005950928
   >>> timeit("isprime2(10143937)", "from __main__ import isprime2")
   21.168850898742676

 */

int isprime(int n) {
    int factor = 3;
    /* Special case for 2 */
    if (n == 2) {
        return 1;
    }
    /* Check for even numbers */
    if ((n % 2) == 0) {
       return 0;
    }
    /* Check for everything else */
    while (factor*factor < n) {
        if ((n % factor) == 0) {
            return 0;
        }
        factor += 2;
    }
    return 1;
}
