#include <stdio.h>
#include <complex.h>

double complex cidentity(double complex in_val)
{
    return in_val;
}

void test_fn (void)
{
    double complex v = cidentity(4.+3.j);

    printf("test_fn(): %lg%+lgj\n\n", creal(v), cimag(v));
}
