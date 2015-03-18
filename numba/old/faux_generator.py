#! /usr/bin/env python
# ______________________________________________________________________

import threading
try:
    import queue
except ImportError:
    import Queue as queue

# ______________________________________________________________________

class Channel(object):
    def __init__(self):
        self.data = None
        self.cv = threading.Condition()

    def get(self):
        self.cv.acquire()
        try:
            while self.data is None:
                self.cv.wait()
            rv = self.data
            self.data = None
        finally:
            self.cv.release()
        return rv

    def put(self, *args):
        self.cv.acquire()
        try:
            assert self.data is None and args is not None
            self.data = args
            self.cv.notify()
        finally:
            self.cv.release()

# ______________________________________________________________________

class FauxGenerator(object):
    def __init__(self, *args, **kws):
        self.args = args
        self.kws = kws
        self.closed = False
        self.thread = threading.Thread(target=self.threadtarget)
        self.in_channel = Channel()
        self.out_channel = Channel()
        self.sending = queue.Queue(1)
        self.receiving = queue.Queue(1)
        self.thread.daemon = True

    def run(self, *args, **kws):
        raise NotImplementedError

    def threadtarget(self):
        try:
            self.receiving.get() # Throw out first value.
            self.run(*self.args, **self.kws)
        finally:
            self.dostop()

    def dostop(self):
        self.closed = True
        self.sending.put((1, StopIteration))
        self.in_channel = None
        self.out_channel = None

    def doyield(self, value):
        #self.out_channel.put(0, value)
        #exn, value = self.in_channel.get()
        self.sending.put((0, value))
        exn, value = self.receiving.get()
        if exn:
           raise value
        return value

    def send_ex(self, s_exn, s_value):
        if not self.thread.is_alive():
           if self.closed:
               raise StopIteration
           else:
               assert s_value is None and not s_exn
               self.thread.start()
        #exn, value = self.out_channel.get()
        #self.in_channel.put(s_exn, s_value)
        self.receiving.put((exn, value))
        exn, value = self.sending.get()
        if exn:
           raise value
        return value

    def __iter__(self):
        return self

    def send(self, value):
        return self.send_ex(0, value)

    def next(self):
        return self.send_ex(0, None)

    def throw(self, exn):
        return self.send_ex(1, exn)

    def close(self):
        rv = self.send_ex(1, GeneratorExit)
        return rv



# ______________________________________________________________________

class EchoGenerator(FauxGenerator):
    def run(self, value, *args, **kws):
        print("Execution starts when 'next()' is called for the first time.")
        try:
            while True:
                try:
                    value = self.doyield(value)
                except Exception as e:
                    value = e
        finally:
            print("Don't forget to clean up when 'close()' is called.")

# ______________________________________________________________________
# The following is present for comparison against an example in the
# Python documentation.  See:
# http://docs.python.org/2/reference/expressions.html#yieldexpr

def echo(value=None):
     print "Execution starts when 'next()' is called for the first time."
     try:
         while True:
             try:
                 value = (yield value)
             except Exception, e:
                 value = e
     finally:
         print "Don't forget to clean up when 'close()' is called."

# ______________________________________________________________________
# End of faux_generator.py
