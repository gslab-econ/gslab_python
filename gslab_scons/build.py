import os, sys, shutil, subprocess
from datetime import datetime
from sys import platform
from misc import *
from log import log_timestamp
from gslab_fill.tablefill import tablefill
from exceptions import *

def build_tables(target, source, env):
    tablefill(input    = ' '.join(env.GetBuildPath(env['INPUTS'])), 
              template = env.GetBuildPath(source[0]), 
              output   = env.GetBuildPath(target[0]))
    return None

def build_lyx(target, source, env):
    source      = make_list_if_string(source)
    target      = make_list_if_string(target)
    start_time  = current_time()
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    check_source_code_extension(source_file, 'lyx')
    newpdf      = source_file.replace('.lyx','.pdf')
    log_file    = target_dir + '/sconscript.log'
    
    os.system('lyx -e pdf2 %s > %s' % (source_file, log_file))
    
    shutil.move(newpdf, target_file)
    end_time    = current_time()
    log_timestamp(start_time, end_time, log_file)
    return None

def build_r(target, source, env):
    source      = make_list_if_string(source)
    target      = make_list_if_string(target)
    start_time  = current_time()
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    check_source_code_extension(source_file, 'r')
    log_file    = target_dir + '/sconscript.log'

    os.system('R CMD BATCH --no-save %s %s' % (source_file, log_file))

    end_time   =  current_time()    
    log_timestamp(start_time, end_time, log_file)
    return None

def build_python(target, source, env):
    source      = make_list_if_string(source)
    target      = make_list_if_string(target)
    start_time  = current_time()
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    check_source_code_extension(source_file, 'python')
    log_file    = target_dir + '/sconscript.log'

    os.system('python %s > %s' % (source_file, log_file))

    end_time   =  current_time()    
    log_timestamp(start_time, end_time, log_file)
    return None


def build_stata(target, source, env):
    ''' User can specify flavour by typing `scons sf=StataMP` 
       (default: Scons will try to find each flavour). 
    '''
    start_time =  current_time()
    
    source       = make_list_if_string(source)
    target       = make_list_if_string(target)
    source_file  = str(source[0])
    target_file  = str(target[0])

    target_dir   = os.path.dirname(target_file)
    check_source_code_extension(source_file, 'stata')
    log_file = target_dir + '/sconscript.log'
    loc_log  = os.path.basename(source_file).replace('.do','.log')

    user_flavor  = env['user_flavor']  
    if user_flavor is not None:
        if is_unix():
            command = stata_command_unix(user_flavor)
        elif platform == 'win32':
            command = stata_command_win(user_flavor)
    else:
        flavors = ['stata-mp', 'stata-se', 'stata']
        if is_unix():
            for flavor in flavors:
                if is_in_path(flavor):
                    command = stata_command_unix(flavor)
                    break
        elif platform == 'win32':
            try:
                key_exist = os.environ['STATAEXE'] is not None
                command   = stata_command_win("%%STATAEXE%%")
            except KeyError:
                flavors = [(f.replace('-', '') + '.exe') for f in flavors]
                if is_64_windows():
                    flavors = [f.replace('.exe', '-64.exe') for f in flavors]
                for flavor in flavors:
                    if is_in_path(flavor):
                        command = stata_command_win(flavor)
                        break
    try:
        subprocess.check_output(command % source_file, shell = True)
    except subprocess.CalledProcessError:
        print('*** Error: Stata executable not found.')
        raise BadExecutableError()

    shutil.move(loc_log, log_file)
    end_time = current_time()
    log_timestamp(start_time, end_time, log_file)
    return None


