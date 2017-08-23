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
    if '>' in do:
        warning = 'There is a redirection operator > in your "do" argument,' + \
                  'build_anything may not work as intended.'
        warnings.warn(warning)

    # log maker
    ## the log_file key must exist in env
    try: 
        log_file = env['log_file']
    except KeyError:
        message = 'We did not find a log_file key in the env passed to build_anything' + \
                  'Please specify the log_file argument when calling build_anything.'
        raise ExecCallError(message)
    ## the log must be named sconscript*.log 
    log_tail = log_file.split('/')[-1]
    log_pattern = re.compile('^sconscript(.)*log')
    if not re.search(log_pattern, log_tail):
        message = 'The log file passed to build_anything needs to be named' + \
                  ' sconscript*.log'
        raise ExecCallError(message)

    # System call
    command = '%s > %s' % (do, log_file)
    print command

    try:
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












