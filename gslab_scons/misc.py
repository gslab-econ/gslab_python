import os
import re
import sys
import time
import shutil
import subprocess
import datetime
import yaml
import getpass
# Import gslab_scons modules
import _exception_classes
from size_warning import issue_size_warnings

def scons_debrief(target, env):
    '''Execute functions after SCons has built all targets'''
    # Log the state of the repo
    env['CL_ARG']      = env['MAXIT']
    maxit              = int(command_line_args(env))
    state_of_repo(maxit)

    # Issue size warnings
    look_in            = env['look_in']
    look_in            = look_in.split(';')
    lfs_required       = env['lfs_required']
    file_MB_limit_lfs  = float(env['file_MB_limit_lfs'])
    total_MB_limit_lfs = float(env['total_MB_limit_lfs'])
    file_MB_limit      = float(env['file_MB_limit'])
    total_MB_limit     = float(env['total_MB_limit'])
    git_attrib_path    = env['git_attrib_path']
        
    issue_size_warnings(look_in, file_MB_limit_lfs, total_MB_limit_lfs, file_MB_limit, \
                        total_MB_limit, lfs_required, git_attrib_path)
    return None

def state_of_repo(maxit):
    outfile = 'state_of_repo.log'
    with open(outfile, 'wb') as f:
        f.write("WARNING: Information about .sconsign.dblite may be misleading \n" +
                "as it can be edited after state_of_repo.log finishes running\n\n" +
                "===================================\n\n GIT STATUS" +
                "\n\n===================================\n")
        f.write("Last commit:\n\n")

    # https://stackoverflow.com/questions/876239/how-can-i-redirect-and-append-both-stdout-and-stderr-to-a-file-with-bash
    os.system("git log -n 1 >> state_of_repo.log 2>&1")
    with open(outfile, 'ab') as f:
        f.write("\n\nFiles changed since last commit:\n\n")
    os.system("git diff --name-only >> state_of_repo.log 2>&1")

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
    '''
    This helper function returns the most common Stata executable
    for Mac/Windows if the default executable is not available in env. 
    '''
    # Get environment's user input executable. Empty default = None.
    stata_executable  = env['stata_executable']  

    if stata_executable not in [None, 'None', '']:
        return stata_executable
    else:
        if is_unix():
            return 'stata-mp'
        elif sys.platform == 'win32':
            return 'StataMP-64.exe'
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


def check_code_extension(source_file, extensions):
    '''
    This function raises an exception if the extension in `source_file`
    does not match the software package specified by `software`.
    '''
    if not isinstance(extensions, list):
        extensions = [extensions]
    source_file = str.lower(str(source_file))
    error       = True
    for extension in extensions:
        extension = str.lower(str(extension))

        if source_file.endswith(extension):
            error = False

    if error:
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


def load_yaml_value(path, key):
    '''
    Load the yaml value indexed by the key argument in the file
    specified by the path argument.
    '''
    if key == "stata_executable":
        prompt = "Enter %s or None to search for defaults: "
    elif key == "github_token":
        prompt = "(Optional) Enter %s to be stored in config_user.yaml.\n" 
        prompt = prompt + "Github token can also be entered without storing to file later:" 
    else:
        prompt = "Enter %s: "

    # Check if file exists and is not corrupted. If so, load yaml contents.
    yaml_contents = None
    if os.path.isfile(path):
        try:
            yaml_contents = yaml.load(open(path, 'rU'))
            if not isinstance(yaml_contents, dict):
                raise yaml.scanner.ScannerError()

        except yaml.scanner.ScannerError:
            message  = "%s is a corrupted yaml file. Delete file and recreate? (y/n) "
            response = str(raw_input(message % path))
            if response.lower() == 'y':
                os.remove(path)
                yaml_contents = None
            else:
                message = "%s is a corrupted yaml file. Please fix." % path
                raise _exception_classes.PrerequisiteError(message)

    # If key exists, return value. Otherwise, add key-value to file.
    try:
        if yaml_contents[key] == "None":
            return None
        else:
            return yaml_contents[key]
    except:
        with open(path, 'ab') as f:  
            if key == "github_token":
                val = getpass.getpass(prompt = (prompt % key))
            else:
                val = str(raw_input(prompt % key))
            if re.sub('"', '', re.sub('\'', '', val.lower())) == "none":
                val = None
            f.write('%s: %s\n' % (key, val))
        return val


def check_and_expand_path(path):
    error_message = " The directory provided, '%s', cannot be found. " % path + \
                    "Please manually create before running\n" + \
                    "or fix the path in config_user.yaml.\n"
    try:
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise _exception_classes.PrerequisiteError(error_message)
        return path
    except:
        raise _exception_classes.PrerequisiteError(error_message)


def get_directory(path):
    '''
    Determine the directory of a file. This function returns
    './' rather than '' when `path` does not include a directory.
    '''
    directory = os.path.dirname(path)
    if directory == '':
        directory = './'

    return directory

def check_targets(target_files):
    '''
    This function raises an exception if any of the files listed as `target_files`
    do not exist after running a builder. 
    '''
    if not isinstance(target_files, list):
        target_files = [target_files]
    non_existence = []
    for target in target_files:
        target = str(target)
        if not os.path.isfile(target):
            non_existence.append(target)

    if non_existence:
        error_message = 'The following target files do not exist after build:\n' + '\n'.join(non_existence)
        raise _exception_classes.TargetNonexistenceError(error_message)

    return None

