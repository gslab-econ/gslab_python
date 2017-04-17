import subprocess
import os
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import BadExecutableError


def build_r(target, source, env):
    '''Build SCons targets using an R script

    This function executes an R script to build objects specified
    by target using the objects specified by source.

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the R script that the builder is intended to execute. 
    env: SCons construction environment, see SCons user guide 7.2
    '''
    # Prelims
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)

    start_time  = misc.current_time()

    misc.check_code_extension(source_file, 'r')
    log_file = target_dir + '/sconscript.log'
    
    cl_arg = misc.command_line_args(env)

    if cl_arg != '':
        cl_arg = "'--args %s'" % cl_arg

    # System call
    try:
        command = 'R CMD BATCH --no-save %s %s %s' % (cl_arg, source_file, log_file)
        subprocess.check_output(command,
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError:
        message = misc.command_error_msg("R", command)
        raise BadExecutableError(message)

    end_time = misc.current_time()    
    log_timestamp(start_time, end_time, log_file)
    
    return None
