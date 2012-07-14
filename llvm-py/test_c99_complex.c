#include <stdio.h>
#include <complex.h>

typedef struct { double real; double imag; } test_complex_t;

double complex cidentity (double complex in_val)
{
    return in_val;
}

test_complex_t cidentity2 (test_complex_t in_val)
{
    return in_val;
}

void test_fn (void)
{
    double complex v = cidentity(4.+3.j);

    printf("test_fn(): %lg%+lgj\n\n", creal(v), cimag(v));
}
