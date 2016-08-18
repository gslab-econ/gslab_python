import os, sys, shutil, subprocess
from gslab_fill.tablefill import tablefill

def build_tables(target, source, env):
    tablefill(input    = ' '.join(env.GetBuildPath(env['INPUTS'])), 
              template = env.GetBuildPath(source[0]), 
              output   = env.GetBuildPath(target[0]))
    return None

def build_lyx(target, source, env):
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    newpdf      = source_file.replace('.lyx','.pdf')
    log_file    = target_dir + '/sconscript.log'
    os.system('lyx -e pdf2 %s >> %s' % (source_file, log_file))
    shutil.move(newpdf, target_file)
    return None

def build_r(target, source, env):
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    log_file    = target_dir + '/sconscript.log'
    os.system('Rscript %s >> %s' % (source_file, log_file) + " 2>&1")
    return None

def build_stata(target, source, env, executable = 'StataMP', version = "14"):
    source_file = str(source[0])
    target_file = str(target[0])
    target_dir  = os.path.dirname(target_file)
    
    if os.name == 'posix':
      log_file  = target_dir + '/sconscript.log'
      loc_log   = source_file.replace('.do','.log')
      if executable == 'StataSE':
        os.system('statase -e %s' % source_file)        
      else if executable == 'Stata':
        os.system('stata -e %s' % source_file)
      else if executable == 'StataMP': 
        try:
          subprocess.check_output(['statamp -e', source_file], shell=True)
        except subprocess.CalledProcessError:       
          subprocess.check_output(['statase -e', source_file], shell=True)      
      os.system('mv %s %s' % (source_file, log_file))
    
    else if os.name == 'nt':
      log_file  = target_dir + '\sconscript.log'
      loc_log   = source_file.replace('.do','.log')
      excut     = '"C:\Program Files\Stata'+ version + '\\' + executable +  '/e do  "' + source_file
      os.system('move %s %s' % (source_file, log_file))
    
    return None
