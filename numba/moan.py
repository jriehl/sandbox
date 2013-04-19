# Mother of all Numba inputs?
import math

def kernel(invec):
    return invec * 2 + 1

def gen_test(it):
    for other in it:
        yield kernel(other)

def closure_test(foo):
    def bar(baz):
        return foo + baz - global_z
    return bar

global_z = 98.6

def global_test(adj):
    global global_z
    global_z += adj

class ClassTest0:
    def __init__ (self, x, y):
        self.x = x
        self.y = y
        self.z = global_z

class ClassTest1(object):
    def __init__ (self, x, y):
        self.x = x
        self.y = y
        self.z = global_z

def len(self):
    return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

def main():
    t0 = ClassTest0(2, 3)
    t1 = ClassTest1(2, 3)
    assert len(t0) == len(t1)
    print("Passed.")

if __name__ == "__main__":
    main()
