import os
import subprocess
import shutil
import sys
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError


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
    '''

    # Prelims
    source     = misc.make_list_if_string(source)
    target     = misc.make_list_if_string(target)
    start_time =  misc.current_time()

    # Set up source file and the original location of the log
    source_file = str(source[0])
    misc.check_code_extension(source_file, '.do')
    loc_log  = os.path.basename(source_file).replace('.do','.log')

    # Set up log file destination
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)
    try:
        log_ext = '_%s' % env['log_ext']
    except KeyError:
        log_ext = ''
    log_file = os.path.join(target_dir, ('sconscript%s.log' % log_ext))
    
    # Set up command line arguments
    cl_arg = misc.command_line_args(env)
    executable = misc.get_stata_executable(env)
    command_skeleton = misc.get_stata_command(executable)
    
    try:
        command = command_skeleton % (source_file, cl_arg)
        subprocess.check_output(command, 
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError:
        message = misc.command_error_msg("Stata", command)
        if  env['stata_executable'] in [None, 'None', '']:
            message = message + '\n Maybe try specifying the Stata executable in config_user.yaml?'
        raise ExecCallError(message)

    shutil.move(loc_log, log_file)

    # Check if targets exist after build
    misc.check_targets(target)

    end_time = misc.current_time()
    log_timestamp(start_time, end_time, log_file)
    
    return None

