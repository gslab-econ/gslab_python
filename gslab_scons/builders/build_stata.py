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

    Note: the user can specify a flavour by typing `scons sf=StataMP` 
    (By default, SCons will try to find each flavour). 
    '''
    start_time =  misc.current_time()
    
    source       = misc.make_list_if_string(source)
    target       = misc.make_list_if_string(target)
    source_file  = str(source[0])
    target_file  = str(target[0])

    target_dir   = os.path.dirname(target_file)
    misc.check_code_extension(source_file, '.do')
    log_file     = target_dir + '/sconscript.log'
    loc_log      = os.path.basename(source_file).replace('.do','.log')

    executable   = misc.get_stata_executable(env)
    command      = misc.get_stata_command(executable)

    try:
        system_call = command % source_file
        subprocess.check_output(system_call, 
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError:
        message =  '''Could not find executable for Stata.
                      Command tried:   %s''' % (system_call)
        raise BadExecutableError(message)

    shutil.move(loc_log, log_file)
    end_time = misc.current_time()
    log_timestamp(start_time, end_time, log_file)

    # Append builder-log to SConstruct log
    scons_log   = open("SConstruct.log", "a")
    builder_log = open(log_file, "r") 
    scons_log.write(builder_log.read())
    
    return None

