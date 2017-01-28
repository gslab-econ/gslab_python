import os
import subprocess
import shutil
import gslab_scons.misc as misc
from gslab_scons import log_timestamp

def build_matlab(target, source, env):
    '''Build targets with a Matlab command
 
    This function executes a Matlab function to build objects specified by target using the objects specified by source.
    It requires Matlab to be callable from the command line via `matlab`.

    Accessing command line arguments from within matlab is possible via the `command_line_arg = getenv('CL_ARG')`. 

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the Matlab .M script that the builder is intended to execute. 

	'''
    start_time =  misc.current_time()

    if misc.is_unix():
        options = '-nosplash -nodesktop'
    elif misc.is_64_windows():
        options = '-nosplash -minimize -wait'
    else:
        raise Exception("Unknown OS")
    
    source       = misc.make_list_if_string(source)
    target       = misc.make_list_if_string(target)
    
    source_file  = str(source[0])
    misc.check_code_extension(source_file, 'matlab')

    target_dir   = os.path.dirname(str(target[0]))
    log_file     = target_dir + '/sconscript.log'
    cl_arg       = misc.command_line_arg(env)

    os.environ['CL_ARG'] = cl_arg

    shutil.copy(source_file, 'source.m')
    command  = 'matlab %s -r source -logfile %s'
    os.system(command % (options, log_file))
    os.remove('source.m')

    end_time = misc.current_time()
    log_timestamp(start_time, end_time, log_file)
    return None
	