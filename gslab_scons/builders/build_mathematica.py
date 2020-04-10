import os
import shutil
import hashlib
import sys

import gslab_scons.misc as misc
from gslab_builder import GSLabBuilder


def build_mathematica(target, source, env):
    '''
    Build targets with a Mathematica command
 
    This function executes a Mathematica function to build objects 
    specified by target using the objects specified by source.
    It requires Mathematica to be callable from the command line 
    via `MathKernel`.
 
    '''
    builder_attributes = {
        'name': 'Mathematica',
        'valid_extensions': ['.m'],
    }
    builder = MathematicaBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()    
    return None

class MathematicaBuilder(GSLabBuilder):
    '''
    '''
    def __init__(self, target, source, env, name = '', valid_extensions = []):
        '''
        '''
        exec_opts = self.add_executable_options()
        super(MathematicaBuilder, self).__init__(target, source, env, name = name,
                                            exec_opts = exec_opts,
                                            valid_extensions = valid_extensions)


    def add_executable_options(self):
        '''
        '''
        options = ' -script '
        return options

    def add_call_args(self):
        '''
        '''
        args = '%s > %s' % (os.path.normpath(self.source_file), os.path.normpath(self.log_file))
        self.call_args = args
        self.exec_file = os.path.normpath(self.source_file)
        return None


    def execute_system_call(self):
        '''
        '''
        super(MathematicaBuilder, self).execute_system_call()
        return None
