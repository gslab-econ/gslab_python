import os
import subprocess
import gslab_scons.misc as misc
from gslab_scons import log_timestamp

def build_python(target, source, env):
    '''Build SCons targets using a Python script

    This function executes a Python script to build objects specified
    by target using the objects specified by source.

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the Python script that the builder is intended to execute. 
    '''

    # Prelims
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)
    start_time  = misc.current_time()

    # Setup source file
    source_file = str(source[0])
    misc.check_code_extension(source_file, '.py')

    # Setup log file
    log_dir     = os.path.dirname(str(target[0]))
    log_file    = log_dir + '/sconscript.log'

    # System call
    try:
        system_call = 'python %s > %s' % (source_file, log_file)
        subprocess.check_output(system_call,
                               stderr = subprocess.STDOUT,
                               shell = True)
    except subprocess.CalledProcessError:
        message = '''Could not find executable for Python. 
                     \nCommand tried: %s''' % (system_call)
        raise BadExecutableError(message)

    # Close log
    end_time   =  misc.current_time()    
    log_timestamp(start_time, end_time, log_file)
    
    return None
