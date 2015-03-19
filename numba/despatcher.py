#! /bin/env python
# ______________________________________________________________________
'''Module containing the Despatcher class, intended to be a sane,
generic, and low-level entry into the Numba compiler, developed with
the primary intention to make rapid prototyping easier.
'''
# ______________________________________________________________________
# Module imports

from numba import *
from numba import compiler, sigutils
from numba.targets import registry

# ______________________________________________________________________

class Despatcher(object):
    '''This class is responsible for collecting all the information
    necessary to use the Numba compiler, but without using the
    now-preferred entry point through the dispatcher subclasses (hence
    Despatcher).
    '''
    def __init__(self, locals={}, targetoptions={}, target='cpu',
                 library=None, **kws):
        targetoptions.update(kws)
        self.dispatcher_ty = registry.target_registry[target]
        self.targetdescr = self.dispatcher_ty.targetdescr
        self.typingctx = self.targetdescr.typing_context
        self.targetctx = self.targetdescr.target_context
        self.locals = locals
        self.targetoptions = targetoptions
        self.flags = compiler.Flags()
        self.targetdescr.options.parse_as_flags(self.flags, self.targetoptions)
        self.library = library

    def get_pipeline(self, sig, library=None):
        if library is None:
            library = self.library
        args, return_type = sigutils.normalize_signature(sig)
        return compiler.Pipeline(self.typingctx, self.targetctx,
                                 self.library, args, return_type,
                                 self.flags, self.locals)

    def compile(self, py_func, sig, library=None):
        if library is None:
            library = self.library
        args, return_type = sigutils.normalize_signature(sig)
        return compiler.compile_extra(self.typingctx, self.targetctx,
                                      py_func, args=args,
                                      return_type=return_type,
                                      flags=self.flags, locals=self.locals,
                                      library=library)

    def get_and_prime_pipeline(self, py_func, sig, library=None, lifted=(),
                               func_attr=compiler.DEFAULT_FUNCTION_ATTRIBUTES):
        pipeline = self.get_pipeline(sig, library)
        bc = pipeline.extract_bytecode(py_func)
        pipeline.bc = bc
        pipeline.func = py_func
        pipeline.lifted = lifted
        return pipeline

    def get_pipeline_manager(self, py_func, sig, library=None, lifted=(),
                             func_attr=compiler.DEFAULT_FUNCTION_ATTRIBUTES):
        '''Returns a non-finalized PipelineManager, populated as if set up by
        Pipeline._compile_bytecode().
        '''
        pipeline = self.get_and_prime_pipeline(py_func, sig, library, lifted,
                                               func_attr)
        pm = compiler._PipelineManager()
        if not pipeline.flags.force_pyobject:
            pm.create_pipeline("nopython")
            pm.add_stage(pipeline.stage_analyze_bytecode, "analyzing bytecode")
            pm.add_stage(pipeline.stage_nopython_frontend, "nopython frontend")
            pm.add_stage(pipeline.stage_annotate_type, "annotate type")
            pm.add_stage(pipeline.stage_nopython_backend,
                         "nopython mode backend")

        if pipeline.status.can_fallback or pipeline.flags.force_pyobject:
            pm.create_pipeline("object")
            pm.add_stage(pipeline.stage_analyze_bytecode, "analyzing bytecode")
            pm.add_stage(pipeline.stage_objectmode_frontend,
                         "object mode frontend")
            pm.add_stage(pipeline.stage_annotate_type, "annotate type")
            pm.add_stage(pipeline.stage_objectmode_backend,
                         "object mode backend")

        if pipeline.status.can_giveup:
            pm.create_pipeline("interp")
            pm.add_stage(pipeline.stage_compile_interp_mode,
                         "compiling with interpreter mode")

        return pm

# ______________________________________________________________________
# End of despatcher.py
