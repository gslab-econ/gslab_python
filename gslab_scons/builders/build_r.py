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
    '''
    # Prelims
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)
    start_time  = misc.current_time()

    # Setup source file
    source_file = str(source[0])
    misc.check_code_extension(source_file, '.r')
 
    # Setup log file
    log_dir     = os.path.dirname(str(target[0]))
    log_file    = log_dir + '/sconscript.log'

    # Allow command line arguments 
    cl_arg      = misc.command_line_arg(env)
    if cl_arg != '':
        cl_arg = "'--args %s'" % cl_arg

    # System call
    try:
        command = 'R CMD BATCH --no-save %s %s %s' % (cl_arg, source_file, log_file)
        subprocess.check_output(command,
                                stderr = subprocess.STDOUT,
                                shell = True)
    except subprocess.CalledProcessError:
        message = system_call_error("R", command)
        raise BadExecutableError(message)

    # Close log
    end_time   =  misc.current_time()    
    log_timestamp(start_time, end_time, log_file)

    # Append builder-log to SConstruct log
    scons_log   = open("SConstruct.log", "a")
    builder_log = open(log_file, "r") 
    scons_log.write(builder_log.read())
    
    return None
