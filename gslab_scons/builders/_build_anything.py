import os
import subprocess
import gslab_scons.misc as misc
import warnings
import re
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError

def _build_anything(target, source, action, env, warning = True, **kw):
    ''' 
    Anything builder-generator. The generator will create a custom builder 
    that runs `action` and add it as a SCons node, similar to the native env.Command.
    Using gslab_scons.build_anything will utilize our logging mechanism
    and error catching similar to our other builders.
    `    
    Parameters
    target: string or list 
        The target(s) of the SCons command. The log ends up in the 
        directory of the first specified target.
    source: string or list
        The source(s) of the SCons command. 
    action: string
        The code to be run by the generated builder.
    env: SCons construction environment, see SCons user guide 7.2.
        You ***MUST *** manually pass `env = env` when calling this in SConscript,
        since this is not a Scons.env method like env.Command.
        Special parameters that can be added when using the builder
        log_ext: string
            Instead of logging to `sconscript.log` in the target dir, 
            the builder will log to `sconscript_<log_ext>.log`.
        origin_log_file: string
            Sometimes, your command may produce a log file in an undesirable location.
            Specifying the that location in this argument leads the builder to append
            the content of origin_log_file to log_file and delete origin_log_file.            
            The builder will crash if this file doesn't exist at the end of the command.
        warning: Boolean
            Turns off warnings if warning = False. 
    '''

    # the logging mechanism relies on redirection operators
    if '>' in action:
        if warning == True:
            warning_message = '\nThere is a redirection operator > in your prescribed action key.\n' + \
                              'build_anything\'s logging mechanism may not work as intended.'
            warnings.warn(warning_message)

    # this point onward looks like our other builders
    def build_anything(env, target, source):
        import SCons.Builder
        
        # Prelims
        start_time  = misc.current_time()

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
            command = '%s > %s 2>&1' % (action, log_file)
            subprocess.check_output(command,
                                    stderr = subprocess.STDOUT,
                                    shell  = True)
        except subprocess.CalledProcessError as ex:
            message = misc.command_error_msg("build_anything", command)
            raise ExecCallError('%s\n%s' % (message, ex.output))

        # Check if target exists after build
        misc.check_targets(target)

        # Close log
        end_time = misc.current_time()
        # check if there's an origin_log_file to be appended
        try:
            origin_log_file = env['origin_log_file']
            with open(log_file, 'a') as sconscript_log:
                with open(origin_log_file, 'r') as origin_log:
                    sconscript_log.write(origin_log.read())
                os.remove(origin_log_file)
        except KeyError: pass

        log_timestamp(start_time, end_time, log_file)
        return None
    
    # generate SCons object based on the custom builder we made above
    bkw = {
            'action': build_anything,
            'target_factory' : env.fs.Entry,
            'source_factory':  env.fs.Entry,
          }
    bld = SCons.Builder.Builder(**bkw) 
    return bld(env, target, source, **kw)







