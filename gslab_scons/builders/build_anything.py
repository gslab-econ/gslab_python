import os
import subprocess
import gslab_scons.misc as misc
import warnings
import re
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError

def build_anything(target, source, env):
    ''' 
    Anything builder. A wrapper that will run any code in the terminal
    using gslab_scons builder logging mechanism.
    
    The user must specify a "do" and a log_file" arguments when 
    calling the builder.
    
    The command called in the user's terminal will be
        [do] > [log_file]
    
    Parameters
    target: string or list 
        The target(s) of the SCons command. The log ends up in the 
        directory of the first specified target.
    source: string or list
        The source(s) of the SCons command. 
    env: SCons construction environment, see SCons user guide 7.2
        env must contain the following arguments:
        do: string
            The command to be run in terminal. Must not contain a redirection 
            operator i.e. > or >>
        log_file: string
            The log file where output will be redirected. Must be a full path
            from the directory's root, ending with `sconscript*.log` where *
            can be anything. 
        [OPTIONAL]
        origin_log_file: string
            Sometimes, your command may produce a log file in an undesirable location.
            Specifying the that location in this argument leads the builder to append
            the content of origin_log_file to log_file and delete origin_log_file.            
            The builder will crash if this file doesn't exist at the end of the command.
    '''

    # Prelims
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)
    start_time  = misc.current_time()

    # check for redirection in `do`
    try: 
        do = env['do']
    except:
        raise ExecCallError('build_anything did not find a "do" key in env.')
    if '>' in do:
        warning = 'There is a redirection operator > in your "do" key,' + \
                  'build_anything may not work as intended.'
        warnings.warn(warning)

    # Set up log file destination
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)
    try:
        log_ext = '_%s' % env['log_ext']
    except KeyError:
        log_ext = ''
    log_file = os.path.join(target_dir, ('sconscript%s.log' % log_ext))

    # System call
    try:
        command = '%s > %s' % (do, log_file)
        subprocess.check_output(command,
                                stderr = subprocess.STDOUT,
                                shell  = True)
    except subprocess.CalledProcessError as ex:
        message = misc.command_error_msg("build_anything", command)
        raise ExecCallError('%s\n%s' % (message, ex.output))

    # Close log
    end_time = misc.current_time()
    # check if there's an origin_log_file to be appended
    try:
        origin_log_file = env['origin_log_file']
        with open(log_file, 'a') as sconscript_log:
            with open(origin_log_file, 'r') as origin_log:
                sconscript_log.write(origin_log.read())
            os.remove(origin_log_file)
    except KeyError:
        pass
    log_timestamp(start_time, end_time, log_file)

    return None












