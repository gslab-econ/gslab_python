import os
import subprocess
import shutil
import sys 
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import (ExecCallError,
                                           PrerequisiteError)


def build_matlab(target, source, env):
    '''Build targets with a MATLAB command
 
    This function executes a MATLAB function to build objects 
    specified by target using the objects specified by source.
    It requires MATLAB to be callable from the command line 
    via `matlab`.

    Accessing command line arguments from within matlab is 
    possible via the `command_line_arg = getenv('CL_ARG')`. 

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the MATLAB .M script that the builder is intended to execute. 
    env: SCons construction environment, see SCons user guide 7.2
    '''

    if misc.is_unix():
        options = '-nosplash -nodesktop'
    elif sys.platform == 'win32':
        options = '-nosplash -minimize -wait'
    else:
        raise PrerequisiteError("Unsupported OS")
    
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)

    start_time = misc.current_time()

    misc.check_code_extension(source_file, '.m')
    try:
        log_ext = '_%s' % env['log_ext']
    except KeyError:
        log_ext = ''
    log_file = os.path.join(target_dir, ('sconscript%s.log' % log_ext))

    # Set up command line arguments
    cl_arg = misc.command_line_args(env)
    os.environ['CL_ARG'] = cl_arg

    # Run MATLAB on source file
    shutil.copy(source_file, 'source.m')
    try:
        command  = 'matlab %s -r source > %s' % (options, log_file)
        subprocess.check_output(command, 
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError:
        message = misc.command_error_msg("Matlab", command)
        raise ExecCallError(message)    
    os.remove('source.m')

    end_time = misc.current_time()
    log_timestamp(start_time, end_time, log_file)

    return None
    