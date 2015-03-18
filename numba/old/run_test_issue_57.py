#! /usr/bin/env python
import logging; logging.getLogger().setLevel(0)
from numba import *
import numba.tests.issues.test_issue_57 as ti57
c_ra_numba = jit(f4[:,:](i2,f4[:,:]))(ti57.ra_numba)
c_ra_numpy = jit(f4[:,:](i2,f4[:,:]))(ti57.ra_numpy)
print c_ra_numpy.lfunc.module
ti57.benchmark(test_fn = c_ra_numba)
ti57.benchmark(test_fn = c_ra_numba, control_fn = c_ra_numpy)
