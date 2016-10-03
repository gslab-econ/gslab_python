import os, sys, shutil, subprocess
from datetime import datetime
from sys import platform

def check_lfs():
    try:
        output = subprocess.check_output("git-lfs install", shell = True)
    except:
        try:
            output = subprocess.check_output("git-lfs init", shell = True) # init is deprecated version of install
        except:
            sys.exit('''ERROR: Either Git LFS is not installed or your Git LFS settings need to be updated. 
                  Please install Git LFS or run 'git lfs install --force' if prompted above.''')

def stata_command_unix(flavor):
    options = {'darwin': '-e',
               'linux' : '-b',
               'linux2': '-b'}
    option  = options[platform]
    command = flavor + ' ' + option + ' %s '
    return command

def stata_command_win(flavor):
    command  = flavor + ' /e do' + ' %s '
    return command

def is_unix():
    unix = ['darwin', 'linux', 'linux2']
    return platform in unix

def is_64_windows():
    return 'PROGRAMFILES(X86)' in os.environ

def is_in_path(program):
    # General helper function to check if `program` exist in the path env
    if is_exe(program):
        return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip("'")
            exe = os.path.join(path, program)
            if is_exe(exe):
                return exe
    return None

def is_exe(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

def make_list_if_string(source):
    if isinstance(source, str):
        source = [source]
    return source

def check_source_code_extension(source_file, software):
    extensions = {'stata'  : '.do',
                  'r'      : '.r', 
                  'lyx'    : '.lyx',
                  'python' : '.py'}
    ext = extensions[software]
    source_file = str.lower(source_file)
    if not source_file.endswith(ext):
        try:
            raise ValueError()
        except ValueError:
            sys.exit('*** Error: ' + 'First argument in `source`, ' + source_file + ', must be a ' + ext + ' file')    
    return None

def current_time():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')    