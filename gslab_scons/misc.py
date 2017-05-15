import os
import re
import sys
import time
import shutil
import subprocess
import datetime
# Import gslab_scons modules
import _exception_classes
from size_warning import issue_size_warnings


def scons_debrief(target, source, env):
    '''Execute functions after SCons has built all targets'''
    # Log the state of the repo
    env['CL_ARG'] = env['MAXIT']
    maxit = int(command_line_args(env))
    state_of_repo(maxit)

    # Issue size warnings
    look_in = env['look_in']
    look_in = look_in.split(';')
    file_MB_limit = float(env['file_MB_limit'])
    total_MB_limit = float(env['total_MB_limit'])
    issue_size_warnings(look_in, file_MB_limit, total_MB_limit)


def state_of_repo(maxit):
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
                path = os.path.join(root, name).replace('\\', '/')
                if i <= maxit and not \
                        re.search('\./\.', path) and not \
                        re.search('.DS_Store', name):
                    stat_info = os.stat(os.path.join(root, name))
                    f.write(os.path.join(root, name) + ':\n')
                    f.write('   modified on: %s\n' % 
                        time.strftime('%d %b %Y %H:%M:%S', 
                                      time.localtime(stat_info.st_mtime)))
                    f.write('   size of file: %s\n' % stat_info.st_size)
                    i = i + 1
                elif i > maxit:
                    f.write('MAX ITERATIONS (%s) HIT IN DIRECTORY: %s\n' % \
                            (maxit, root))
                    break
    return None


def command_line_args(env):
    '''
    Return the content of env['CL_ARG'] as a string
    with spaces separating entries. If env['CL_ARG']
    doesn't exist, return an empty string. 
    '''
    try:
        cl_arg = env['CL_ARG']
        if not isinstance(cl_arg, str):
            try:
                # Join arguments as strings by spaces
                cl_arg = ' '.join(map(str, cl_arg))
            except TypeError:
                cl_arg = str(cl_arg)
                
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
        elif sys.platform == 'win32':
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
    elif sys.platform == 'win32':
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
    option  = options[sys.platform]
    command = flavor + ' ' + option + ' %s %s'  # %s will take filename and cl_arg later

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
    return sys.platform in unix


def is_64_windows():
    '''
    This function return True if the user's platform is Windows (64 bit)
    and False otherwise.
    '''
    return 'PROGRAMFILES(X86)' in os.environ


def is_in_path(program):
    '''
    This general helper function checks whether `program` exists in the 
    user's path environment variable.
    '''
    if os.access(program, os.X_OK):
        return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip("'")
            exe = os.path.join(path, program)
            if os.access(exe, os.X_OK):
                return exe
    return False


def make_list_if_string(source):
    '''Convert a string input into a singleton list containing that string.'''
    if not isinstance(source, list):
        if isinstance(source, str):
            source = [source]
        else:
            message = "SCons source/target input must be either list or string. " + \
                      "Here, it is %s, a %s." % (str(source), str(type(source)))
            raise TypeError(message)
    return source


def check_code_extension(source_file, extension):
    '''
    This function raises an exception if the extension in `source_file`
    does not match the software package specified by `software`.
    '''
    source_file = str.lower(str(source_file))
    extension   = str.lower(str(extension))
    if not source_file.endswith(extension):
        error_message = 'First argument, %s, must be a %s file.' % \
                (source_file, extension)
        raise _exception_classes.BadExtensionError(error_message)

    return None


def command_error_msg(executable, call):
    '''Print an informative message given a CalledProcessError.'''
    return '''Could not call %s.
              Please check that the executable, source, and target files
              are correctly specified. 
              Command tried: %s''' % (executable, call) 


def current_time():
    '''Return the current time in a Y-M-D H:M:S format.'''
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')   


def lyx_scan(node, env, path):
    contents = node.get_contents()
    SOURCE = [] 
    for ext in env.EXTENSIONS:
        src_find = re.compile(r'filename\s(\S+%s)' % ext, re.M)

        SOURCE = SOURCE + [source.replace('"', '') \
                 for source in src_find.findall(contents)]

    return SOURCE


def get_directory(path):
    '''
    Determine the directory of a file. This function returns
    './' rather than '' when `path` does not include a directory.
    '''
    directory = os.path.dirname(path)
    if directory == '':
        directory = './'

    return directory
