#! /usr/bin/env python
import logging; logging.getLogger().setLevel(0)
from numba import *
import numba.tests.issues.test_issue_57 as ti57
jit(f4[:,:](i2,f4[:,:]))(ti57.ra_numba)
