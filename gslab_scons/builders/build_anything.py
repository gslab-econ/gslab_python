import os
import subprocess
import gslab_scons.misc as misc
import warnings
import re
import SCons.Builder
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError
import SCons.Builder

def build_anything(target, source, action, env, **kw):

    def _build_anything(env, target, source):
        
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
            command = '%s > %s' % (action, log_file)
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
        except KeyError: pass

        log_timestamp(start_time, end_time, log_file)
        return None
    

    bkw = {
            'action': _build_anything,
            'target_factory' : env.fs.Entry,
            'source_factory':  env.fs.Entry,
          }
    bld = SCons.Builder.Builder(**bkw) 
    return bld(env, target, source, **kw)







