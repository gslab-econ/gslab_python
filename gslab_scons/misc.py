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
    
    This helper function returns a command (str) for Unix bash or
    Windows cmd to carry a Stata batch job. 

    The function checks for a Stata executable in env, an SCons 
    Environment object. If env does not specify an executable, then 
    the function searches for common executables in the system environment.
    '''
    # Get environment's user input executable. Empty default = None.
    stata_executable  = env['stata_executable']  

    if stata_executable is not None:
        return stata_executable
    else:
        executables = ['stata-mp', 'stata-se', 'stata']
        if is_unix():
            for executable in executables:
                if is_in_path(executable): # check in $PATH
                    return executable

        elif sys.platform == 'win32':
            if 'STATAEXE' in os.environ.keys():
                return "%%STATAEXE%%"
            else:
                # Try StataMP.exe and StataMP-64.exe, etc.
                executables = [(e.replace('-', '') + '.exe') for e in executables]
                if is_64_windows():
                    executables = [e.replace('.exe', '-64.exe') for e in executables]
                for executable in executables:
                    if is_in_path(executable):
                        return executable
    return None


def get_stata_command(executable):
    if is_unix():
        command = stata_command_unix(executable)
    elif sys.platform == 'win32':
        command = stata_command_win(executable)
    return command


def stata_command_unix(executable):
    '''
    This function returns the appropriate Stata command for a user's 
    Unix platform.
    '''
    options = {'darwin': '-e',
               'linux' : '-b',
               'linux2': '-b'}
    option  = options[sys.platform]

    # %s will take filename and cl_arg later
    command = executable + ' ' + option + ' %s %s' 

    return command


def stata_command_win(executable):
    '''
    This function returns the appropriate Stata command for a user's 
    Windows platform.
    '''
    command  = executable + ' /e do' + ' %s %s'  # %s will take filename later
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
    ''' This function prints an informative message given a CalledProcessError.'''
    return '''%s did not run successfully.
              Please check that the executable, source, and target files
              Check SConstruct.log for errors.
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
