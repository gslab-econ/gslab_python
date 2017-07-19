import os
import subprocess
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError

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
    env: SCons construction environment, see SCons user guide 7.2
    '''

    # Prelims
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)    

    start_time  = misc.current_time()

    misc.check_code_extension(source_file, '.py')
    log_file = target_dir + '/sconscript.log'
    
    cl_arg = misc.command_line_args(env)

    # System call
    try:
        command = 'python %s %s > %s' % (source_file, cl_arg, log_file)
        subprocess.check_output(command,
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError as ex:
        message = misc.command_error_msg("Python", command)
        raise ExecCallError('%s\n\n%s' % (message, ex.output))

    # Close log
    end_time   =  misc.current_time()    
    log_timestamp(start_time, end_time, log_file)
    
    return None
