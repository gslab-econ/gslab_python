import os
import re
import sys
import importlib
import subprocess
import pkg_resources
from misc import is_in_path, get_stata_executable, get_stata_command, is_unix, load_yaml_value
from _exception_classes import PrerequisiteError


def check_python(gslab_python_version, 
                 packages = ["yaml", "gslab_scons", "gslab_make", "gslab_fill"]):
    '''
    Check that an acceptable version of Python and the specified
    Python packages are installed.
    '''
    if sys.version_info[0] != 2:
        raise PrerequisiteError('Please use Python 2')
    check_python_packages(gslab_python_version, packages)


def check_python_packages(gslab_python_version, packages):
    gslab_python_version = str(gslab_python_version)
    packages             = convert_packages_argument(packages)

    missing = []
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)

    if len(missing) > 0:
        raise PrerequisiteError('Missing %s module(s)' % str(missing))

    installed = pkg_resources.get_distribution('gslab_tools').version.split('.')
    installed = int(installed[0]) * 10000 + \
                int(installed[1]) * 100 + \
                int(installed[2])
    required = gslab_python_version.split('.')
    required = int(required[0]) * 10000 + \
               int(required[1]) * 100 + \
               int(required[2])

    if installed < required:
        message = 'Your gslab_tools Python modules installation is outdated'
        raise PrerequisiteError(message)


def convert_packages_argument(packages):
    '''Try to convert the packages argument into a list of strings'''
    if not isinstance(packages, list):
        if isinstance(packages, str):
            packages = [packages]
        else:
            raise PrerequisiteError('Please supply a Python list of required' + \
                                    'packages, not %s.' % packages)
    for pkg in packages:
        if not isinstance(pkg, str):
            raise PrerequisiteError('All packages should be strings,' + \
                                    ' not %s.' % pkg)          
    return packages


def check_r(packages = ["yaml"]):
    '''
    Check that a recognized R executable is in the path and that 
    the specified R packages are installed.
    '''
    if is_in_path('R.exe') is None and is_in_path('R') is None:
        message = 'R is not installed or excecutable is not added to path'
        raise PrerequisiteError(message)

    check_r_packages(packages)


def check_r_packages(packages):
    '''Check that R packages are installed'''
    packages = convert_packages_argument(packages)
    missing_packages = []
    for pkg in packages:
        # http://stackoverflow.com/questions/6701230/call-r-function-in-linux-command-line
        # http://stackoverflow.com/questions/18962785/oserror-errno-2-no-such-file-or-directory-while-using-python-subprocess-in-dj
        try:
            command = 'R -q -e "suppressMessages(library(%s))"' % pkg
            subprocess.check_output(command, shell = True)
        except subprocess.CalledProcessError:
            missing_packages.append(pkg)

    if len(missing_packages) > 0:
        raise PrerequisiteError("R packages, %s, not found." % missing_packages)


def check_lyx():
    '''Check that there is a recognized LyX executable in the path'''
    if is_in_path('lyx.exe') is None and is_in_path('lyx') is None:
        message = 'LyX is not installed or executable is not added to path'
        raise PrerequisiteError(message)


def check_lfs():
    '''Check that Git LFS is installed'''
    try:
        output = subprocess.check_output("git-lfs install", shell = True)
    except:
        try:
            # init is a deprecated version of install
            output = subprocess.check_output("git-lfs init", shell = True) 
        except:
            raise PrerequisiteError('''
                              Either Git LFS is not installed 
                              or your Git LFS settings need to be updated. 
                              Please install Git LFS or run 
                              'git lfs install --force' if prompted above.''')


def check_and_expand_cache_path(cache):
    error_message = " Cache directory, '%s', is not created. " % cache + \
                    "Please manually create before running.\n\t\t" + \
                    "    Or fix the path in user-config.yaml.\n"
    try:
        cache = os.path.expanduser(cache)
        if not os.path.isdir(cache):
            raise PrerequisiteError(error_message)
        return cache
    except:
        raise PrerequisiteError(error_message)


def check_stata(packages = ["yaml"], user_yaml = "user-config.yaml"):
    '''
    Check that a valid Stata executable is in the path and that the specified
    Stata packages are installed.
    '''
    # Fake scons-like env dict for misc.get_stata_executable(env)
    fake_env = {'stata_executable': load_yaml_value(user_yaml, 
                                                    'stata_executable')} 
    stata_executable = get_stata_executable(fake_env)
    
    if stata_executable is None:
        message = 'Stata is not installed or executable is not added to path'
        raise PrerequisiteError(message)
    
    command = get_stata_command(stata_executable)
    check_stata_packages(command, packages)
    return stata_executable



def check_stata_packages(command, packages):
    '''Check that the specified Stata packages are installed'''
    if is_unix():
        command = command.split("%s")[0]
    elif sys.platform == "win32":
        command = command.split("do")[0]
    else:
        raise PrerequisiteError("Unrecognized OS: %s" % sys.platform)

    packages = convert_packages_argument(packages)
    try:
        for pkg in packages:
            call = (command + "which %s") % pkg
            # http://www.stata.com/statalist/archive/2009-12/msg00493.html 
            # http://stackoverflow.com/questions/18962785/oserror-errno-2-no-such-file-or-directory-while-using-python-subprocess-in-dj
            subprocess.check_output(call, stderr = subprocess.STDOUT, shell = True) 
            
            with open('stata.log', 'rU') as f:
                log = f.read()
            os.remove('stata.log')

            if re.search('command %s not found' % pkg, log):
                raise PrerequisiteError('Stata package %s is not installed' % pkg)

    except subprocess.CalledProcessError:
        raise PrerequisiteError("Stata command, '%s', failed.\n" % command.split(' ')[0] + \
                                "\t\t   Please supply a correct stata_executable" + \
                                " value in user-config.yaml.\n" )
