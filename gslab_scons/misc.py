import os
import sys
import shutil
import subprocess

from datetime import datetime
from sys import platform
from _exception_classes import BadExtensionError


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
    command = flavor + ' ' + option + ' %s ' # %s will take filename later
    return command


def stata_command_win(flavor):
    '''
    This function returns the appropriate Stata command for a user's 
    Windows platform.
    '''
    command  = flavor + ' /e do' + ' %s ' # %s will take filename later
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
    if isinstance(source, str):
        source = [source]
    return source


def check_code_extension(source_file, extension):
    '''
    This function raises an exception if `source_file`'s extension
    does not match the software package specified by `software`.
    '''
    source_file = str.lower(str(source_file))
    extension   = str.lower(str(extension))
    if not source_file.endswith(extension):
        raise BadExtensionError('First argument, ' + source_file + ', must be a ' + extension + ' file')
    return None


def current_time():
    '''
    This function returns the current t ime in a a Y-M-D H:M:S format.
    '''
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')   
