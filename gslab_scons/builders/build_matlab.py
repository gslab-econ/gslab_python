import os
import subprocess
import shutil
from sys import platform
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import BadExecutableError


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
    env: SCons construction environment, see SCons user guide 7.2

	'''
    # Prelims
    source       = misc.make_list_if_string(source)
    target       = misc.make_list_if_string(target)
    start_time =  misc.current_time()

    # Set up source file and the original location of the log
    source_file  = str(source[0])
    misc.check_code_extension(source_file, '.m')

    # Set up log file destination
    target_dir   = os.path.dirname(str(target[0]))
    log_file     = target_dir + '/sconscript.log'

    # Set up command line arguments
    cl_arg       = misc.command_line_arg(env)
    os.environ['CL_ARG'] = cl_arg

    # Matlab options
    if misc.is_unix():
        options = '-nosplash -nodesktop'
    elif platform == 'win32':
        options = '-nosplash -minimize -wait'
    else:
        raise Exception("Unknown OS")

    # Run matlab on source file
    shutil.copy(source_file, 'source.m')
    try:
        command  = 'matlab %s -r source > %s' % (options, log_file)
        subprocess.check_output(command, 
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError:
        message = misc.command_error_msg("Matlab", command)
        raise BadExecutableError(message)    
    os.remove('source.m')

    end_time = misc.current_time()
    log_timestamp(start_time, end_time, log_file)

    return None
	