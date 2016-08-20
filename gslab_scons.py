import os, sys, shutil, subprocess
from gslab_fill.tablefill import tablefill
from gslab_make.make_log import *
from gslab_make.run_program import *


def build_tables(target, source, env):
    tablefill(input    = ' '.join(env.GetBuildPath(env['INPUTS'])), 
              template = env.GetBuildPath(source[0]), 
              output   = env.GetBuildPath(target[0]))
    return None

def build_lyx(target, source, env):
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    if os.name == 'posix':
        log_file    = target_dir + '/sconscript.log'
    else:
        log_file    = target_dir + '\sconscript.log'
    set_option(makelog = log_file, output = target_file)
    start_make_logging(log_file)
    run_lyx(program = source_file)
    start_make_logging(log_file)
    return None

def build_r(target, source, env):
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    if os.name == 'posix':
        log_file    = target_dir + '/sconscript.log'
    else:
        log_file    = target_dir + '\sconscript.log'
    log_file    = target_dir + '/sconscript.log'
    os.system('Rscript %s >> %s' % (source_file, log_file))
    return None

def build_stata(target, source, env, executable = 'StataMP'):
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    if os.name == 'posix':
        log_file    = target_dir + '/sconscript.log'
    else:
        log_file    = target_dir + '\sconscript.log'
    set_option(makelog = log_file, output = target_file)
    start_make_logging(log_file)
    run_stata(program = source_file)
    start_make_logging(log_file)
    return None