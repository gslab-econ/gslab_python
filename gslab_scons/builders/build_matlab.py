import os
import shutil
import hashlib

import gslab_scons.misc as misc
from gslab_builder import GSLabBuilder


def build_matlab(target, source, env):
    '''
    Build targets with a MATLAB command
 
    This function executes a MATLAB function to build objects 
    specified by target using the objects specified by source.
    It requires MATLAB to be callable from the command line 
    via `matlab`.

    Accessing command line arguments from within matlab is 
    possible via the `command_line_arg = getenv('CL_ARG')`. 
    '''
    builder_attributes = {
        'name': 'MATLAB',
        'valid_extensions': ['.m'],
    }
    builder = MatlabBuilder(source, target, env, **builder_attributes)
    builder.execute_system_call()    
    return None

class MatlabBuilder(GSLabBuilder):
    '''
    '''
    def __init__(self, source, target, env, name = '', valid_extensions = []):
        '''
        '''
        self.add_executable_options()
        super(MatlabBuilder, self).__init__(source, target, env, name = name,
                                            exec_opts = self.exec_opts,
                                            valid_extensions = valid_extensions)
        return None


    def add_executable_options(self):
        '''
        '''
        if misc.is_unix():
            platform_option = '-nodesktop '
        elif sys.platform == 'win32':
            platform_option = '-minimize -wait '
        else:
            message = 'Cannot find MATLAB command line syntax for platform.'
            raise PrerequisiteError(message)
        options = ' -nosplash %s -r' % platform_option
        self.exec_opts = options
        return None


    def add_call_args(self):
        '''
        '''
        source_hash = hashlib.sha1(self.source_file).hexdigest()
        source_exec = 'source_%s' % source_hash
        exec_file   = source_exec + '.m'
        shutil.copy(self.source_file, exec_file)
        args = '%s > %s' % (source_exec, self.log_file)
        self.call_args = args
        self.exec_file = exec_file
        return None


    def execute_system_call(self):
        '''
        '''
        os.environ['CL_ARG'] = self.cl_arg
        super(MatlabBuilder, self).execute_system_call()
        os.remove(self.exec_file)
        return None
