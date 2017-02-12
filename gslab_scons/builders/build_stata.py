import os
import subprocess
import shutil
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import BadExecutableError
from sys import platform

def build_stata(target, source, env):
    '''Build targets with a Stata command
 
    This function executes a Stata script to build objects specified
    by target using the objects specified by source.

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the Stata .do script that the builder is intended to execute. 
    env: SCons construction environment, see SCons user guide 7.2

    Note: the user can specify a flavour by typing `scons sf=StataMP` 
    (By default, SCons will try to find each flavour). 
    '''

    #Prelims
    source       = misc.make_list_if_string(source)
    target       = misc.make_list_if_string(target)
    start_time =  misc.current_time()

    # Set up source file and the original location of the log
    source_file = str(source[0])
    misc.check_code_extension(source_file, '.do')
    loc_log  = os.path.basename(source_file).replace('.do','.log')

    # Set up log file destination
    log_dir     = os.path.dirname(str(target[0]))
    log_file    = log_dir + '/sconscript.log'
    
    # Set up command line arguments
    cl_arg      = misc.command_line_arg(env)

    executable       = misc.get_stata_executable(env)
    command_skeleton = misc.get_stata_command(executable)

    try:
        command = command_skeleton % (source_file, cl_arg)
        subprocess.check_output(command, 
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError:
        message = misc.command_error_msg("Stata", command)
        raise BadExecutableError(message)

    shutil.move(loc_log, log_file)
    end_time = misc.current_time()
    log_timestamp(start_time, end_time, log_file)
    
    return None

