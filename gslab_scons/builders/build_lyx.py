import os
import subprocess
import shutil
import gslab_scons.misc as misc
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import BadExecutableError


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

    '''
    # Prelims
    source      = misc.make_list_if_string(source)
    target      = misc.make_list_if_string(target)
    start_time  = misc.current_time()
    
    # Setup source file
    source_file = str(source[0])
    misc.check_code_extension(source_file, '.lyx')

    # Setup target file and log file
    newpdf      = source_file.replace('.lyx','.pdf')
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    log_file    = target_dir + '/sconscript.log'
    
    # System call
    try:
        system_call = 'lyx -e pdf2 %s > %s' % (source_file, log_file)
        subprocess.check_output(system_call,
                               stderr = subprocess.STDOUT,
                               shell = True)
        # Move rendered pdf to the target
        shutil.move(newpdf, target_file)
    except subprocess.CalledProcessError:
        message = '''Could not find executable for Lyx.  
                     \nCommand tried: %s''' % (system_call)
        raise BadExecutableError(message)

    # Close log
    end_time    = misc.current_time()
    log_timestamp(start_time, end_time, log_file)

    # Append builder-log to SConstruct log
    scons_log   = open("SConstruct.log", "a")
    builder_log = open(log_file, "r") 
    scons_log.write(builder_log.read())
    
    
    return None
