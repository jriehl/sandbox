import subprocess
import time
import pprint

def do_trial (front, n = 1):
    t0 = time.time()
    cmd = front + ['scipy2012.py', str(n)]
    print cmd
    subprocess.call(cmd)
    t1 = time.time()
    return t1 - t0

pprint.pprint([[[do_trial(front, 10 ** exp) for _ in xrange(10)]
                for exp in xrange(0, 9, 2)]
               for front in [['python'], ['python', '-O'], ['pypy']]])
