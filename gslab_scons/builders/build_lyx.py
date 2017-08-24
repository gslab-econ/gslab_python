import os
import subprocess
import shutil
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError

def build_lyx(target, source, env):
    '''Compile a pdf from a LyX file

    This function is a SCons builder that compiles a .lyx file
    as a pdf and places it at the path specified by target.

    Parameters
    ----------
    target: string or list 
        The target of the SCons command. This should be the path
        of the pdf that the builder is instructed to compile. 
    source: string or list
        The source of the SCons command. This should
        be the .lyx file that the function will compile as a PDF.
    env: SCons construction environment, see SCons user guide 7.2
    '''

    # Prelims
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)

    source_file = str(source[0])
    misc.check_code_extension(source_file, '.lyx')

    # Set up target file and log file
    newpdf      = source_file[:-4] + '.pdf'
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)

    start_time  = misc.current_time()

    try:
        log_ext = '_%s' % env['log_ext']
    except KeyError:
        log_ext = ''
    log_file = os.path.join(target_dir, ('sconscript%s.log' % log_ext))

    # System call
    try:
        command = 'lyx -e pdf2 %s > %s' % (source_file, log_file)
        subprocess.check_output(command,
                                stderr = subprocess.STDOUT,
                                shell  = True)
        # Move rendered pdf to the target
        shutil.move(newpdf, target_file)
    except subprocess.CalledProcessError:
        message = misc.command_error_msg('lyx', command)
        raise ExecCallError(message)

    # Check if targets exist after build
    misc.check_targets(target)
    
    # Close log
    end_time    = misc.current_time()
    log_timestamp(start_time, end_time, log_file)

    return None
