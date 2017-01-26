import os
import re
import sys
import time
import shutil
import subprocess
import re

from datetime import datetime
from sys import platform
from _exception_classes import BadExtensionError


def state_of_repo(target, source, env):
    maxit = int(command_line_arg(env))
    outfile = 'state_of_repo.log'
    with open(outfile, 'wb') as f:
        f.write("WARNING: Information about .sconsign.dblite may be misleading \n" +
                "as it can be edited after state_of_repo.log finishes running\n\n" +
                "===================================\n\n GIT STATUS \n\n===================================\n")
        f.write("Last commit:\n\n")
    os.system("git log -n 1 >> state_of_repo.log")
    with open(outfile, 'ab') as f:
        f.write("\n\nFiles changed since last commit:\n\n")
    os.system("git diff --name-only >> state_of_repo.log")
    with open(outfile, 'ab') as f:
        f.write("\n===================================\n\n FILE STATUS \n\n===================================\n")
        for root, dirs, files in os.walk(".", followlinks = True):
            i = 1
            for name in files:
                if i <= maxit and not re.search('\./\.', os.path.join(root, name)) \
                                and not re.search('.DS_Store', name):
                    stat_info = os.stat(os.path.join(root, name))
                    f.write(os.path.join(root, name) + ':\n')
                    f.write('   modified on: %s\n' % time.strftime('%d %b %Y %H:%M:%S', time.localtime(stat_info.st_mtime)))
                    f.write('   size of file: %s\n' % stat_info.st_size)
                    i = i + 1
                elif i > maxit:
                    f.write('MAX ITERATIONS (%s) HIT IN DIRECTORY: %s\n' % (maxit, root))
                    break
    return None


def check_lfs():
    '''Check that Git LFS is installed'''
    try:
        output = subprocess.check_output("git-lfs install", shell = True)
    except:
        try:
            # init is a deprecated version of install
            output = subprocess.check_output("git-lfs init", shell = True) 
        except:
            raise LFSError('''Either Git LFS is not installed or your Git LFS settings need to be updated. 
                  Please install Git LFS or run 'git lfs install --force' if prompted above.''')

def command_line_arg(env):
    try:
        cl_arg = env['CL_ARG']
    except KeyError:
        cl_arg = ''
    return cl_arg

def stata_command_unix(flavor, cl_arg = ''):
    '''
    This function returns the appropriate Stata command for a user's 
    Unix platform.
    '''
    options = {'darwin': '-e',
               'linux' : '-b',
               'linux2': '-b'}
    option  = options[platform]
    command = flavor + ' ' + option + ' %s ' + cl_arg # %s will take filename later
    return command


def stata_command_win(flavor, cl_arg = ''):
    '''
    This function returns the appropriate Stata command for a user's 
    Windows platform.
    '''
    command  = flavor + ' /e do' + ' %s ' + cl_arg # %s will take filename later
    return command


def is_unix():
    '''
    This function return True if the user's platform is Unix and false 
    otherwise.
    '''
    unix = ['darwin', 'linux', 'linux2']
    return platform in unix


def is_64_windows():
    '''
    This function return True if the user's platform is Windows (64 bit)
    and false otherwise.
    '''
    return 'PROGRAMFILES(X86)' in os.environ


def is_in_path(program):
    '''
    This general helper function checks whether `program` exists in the 
    user's path environment variable.
    '''
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
    '''Check that a path refers to a file that exists and can be exectuted.'''
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)


def make_list_if_string(source):
    '''Convert a string input into a singleton list containing that string.'''
    if isinstance(source, str):
        source = [source]
    return source


def check_code_extension(source_file, software):
    '''
    This function raises an exception if `source_file`'s extension
    does not match the software package specified by `software`.
    '''
    extensions = {'stata'  : '.do',
                  'r'      : '.r', 
                  'lyx'    : '.lyx',
                  'python' : '.py'}
    ext = extensions[software]
    source_file = str.lower(str(source_file))
    if not source_file.endswith(ext):
        raise BadExtensionError('First argument, ' + source_file + ', must be a ' + ext + ' file')
    return None


def current_time():
    '''
    This function returns the current time in a a Y-M-D H:M:S format.
    '''
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')   


def lyx_scan(node, env, path):
    contents = node.get_contents()
    SOURCE = [] 
    for ext in env.EXTENSIONS:
        src_find = re.compile(r'filename\s(\S+%s)' % ext, re.M)
        SOURCE = SOURCE + [source.replace('"', '') for source in src_find.findall(contents)]
    return SOURCE
