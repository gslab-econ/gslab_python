import os
import subprocess

from gslab_builder import GSLabBuilder


def build_mathematica(target, source, env):
    '''
    Build targets with a Mathematica command
 
    This function executes a Mathematica function to build objects 
    specified by target using the objects specified by source.
    It requires Mathematica to be callable from the command line 
    via `math`.
    
    If on OS X, you'll need to change line 180 in gslab_scons\misc.py
    to 'mathematica': 'MathKernel'.
 
    '''
    builder_attributes = {
        'name': 'Mathematica',
        'valid_extensions': ['.m'],
        'exec_opts': '-script'
    }
    builder = MathematicaBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()    
    return None

class MathematicaBuilder(GSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        args = '%s %s > %s' % (os.path.normpath(self.source_file),
                               self.cl_arg,
                               os.path.normpath(self.log_file))
        self.call_args = args
        return None

