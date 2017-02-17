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
    env['CL_ARG'] = env['MAXIT']
    maxit = int(command_line_arg(env))
    outfile = 'state_of_repo.log'
    with open(outfile, 'wb') as f:
        f.write("WARNING: Information about .sconsign.dblite may be misleading \n" +
                "as it can be edited after state_of_repo.log finishes running\n\n" +
                "===================================\n\n GIT STATUS" +
                "\n\n===================================\n")
        f.write("Last commit:\n\n")
    os.system("git log -n 1 >> state_of_repo.log")
    with open(outfile, 'ab') as f:
        f.write("\n\nFiles changed since last commit:\n\n")
    os.system("git diff --name-only >> state_of_repo.log")
    with open(outfile, 'ab') as f:
        f.write("\n===================================\n\n FILE STATUS" + 
                "\n\n===================================\n")
        for root, dirs, files in os.walk(".", followlinks = True):
            i = 1
            for name in files:
                if i <= maxit and not \
                        re.search('\./\.', os.path.join(root, name).replace('\\', '/')) and not \
                        re.search('.DS_Store', name):
                    stat_info = os.stat(os.path.join(root, name))
                    f.write(os.path.join(root, name) + ':\n')
                    f.write('   modified on: %s\n' % 
                        time.strftime('%d %b %Y %H:%M:%S', time.localtime(stat_info.st_mtime)))
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
    return None


def command_line_arg(env):
    try:
        cl_arg = env['CL_ARG']
    except KeyError:
        cl_arg = ''
    return cl_arg


def get_stata_executable(env):
    '''Return OS command to call Stata.
    
    This helper function returns a command (str) for Unix Bash or
    Windows cmd to carry a Stata batch job. 

    The function will check for user input in Scons env with
    the flag e.g. `sf=StataMP-64.exe`. With no user input,
    the function loops through common Unix and Windows executables
    and searches them in the system environment.
    '''
    # Get environment's user input flavor. Empty default = None.
    user_flavor  = env['user_flavor']  

    if user_flavor is not None:
        return user_flavor
    else:
        flavors = ['stata-mp', 'stata-se', 'stata']
        if is_unix():
            for flavor in flavors:
                if is_in_path(flavor): # check in $PATH
                    return flavor
        elif platform == 'win32':
            try:
                # Check in system environment variables
                key_exist = os.environ['STATAEXE'] is not None
                return "%%STATAEXE%%"
            except KeyError:
                # Try StataMP.exe and StataMP-64.exe, etc.
                flavors = [(f.replace('-', '') + '.exe') for f in flavors]
                if is_64_windows():
                    flavors = [f.replace('.exe', '-64.exe') for f in flavors]
                for flavor in flavors:
                    if is_in_path(flavor):
                        return flavor
    return None


def get_stata_command(executable):
    if is_unix():
        command = stata_command_unix(executable)
    elif platform == 'win32':
        command = stata_command_win(executable)
    return command


def stata_command_unix(flavor):
    '''
    This function returns the appropriate Stata command for a user's 
    Unix platform.
    '''
    options = {'darwin': '-e',
               'linux' : '-b',
               'linux2': '-b'}
    option  = options[platform]
    command = flavor + ' ' + option + ' %s %s'  # %s will take filename later
    return command


def stata_command_win(flavor):
    '''
    This function returns the appropriate Stata command for a user's 
    Windows platform.
    '''
    command  = flavor + ' /e do' + ' %s %s'  # %s will take filename later
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
    return False


def is_exe(file_path):
    '''Check that a path refers to a file that exists and can be exectuted.'''
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)


def make_list_if_string(source):
    '''Convert a string input into a singleton list containing that string.'''
    if not isinstance(source, list):
        if isinstance(source, str):
            source = [source]
        else:
            raise TypeError("Scons source/target input must be either list or string.")
    return source


def check_code_extension(source_file, extension):
    '''
    This function raises an exception if the extension in `source_file`
    does not match the software package specified by `software`.
    '''
    source_file = str.lower(str(source_file))
    extension   = str.lower(str(extension))
    if not source_file.endswith(extension):
        raise BadExtensionError('First argument, ' + source_file + ', must be a ' + extension + ' file')
    return None


def command_error_msg(executable, call):
    ''' This function prints an informative message given a CalledProcessError.'''
    return '''Could not call %s.
              Please check that the executable, source, and target files
              are correctly specified. 
              Command tried: %s''' % (executable, call) 


def current_time():
    '''
    This function returns the current time in a Y-M-D H:M:S format.
    '''
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')   


def lyx_scan(node, env, path):
    contents = node.get_contents()
    SOURCE = [] 
    for ext in env.EXTENSIONS:
        src_find = re.compile(r'filename\s(\S+%s)' % ext, re.M)
        SOURCE = SOURCE + [source.replace('"', '') for source in src_find.findall(contents)]
    return SOURCE
