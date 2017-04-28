import os
import re
import sys
import importlib
import subprocess
import pkg_resources
from misc import is_in_path, get_stata_executable, get_stata_command, is_unix
from _exception_classes import PrerequisiteError


def check_python(gslab_python_version, 
                 packages = ["yaml", "gslab_scons", "gslab_make", "gslab_fill"]):
    if sys.version_info[0] != 2:
        raise PrerequisiteError('Please use python 2')
    check_python_packages(gslab_python_version, packages)

def check_python_packages(gslab_python_version, packages):
    gslab_python_version = str(gslab_python_version)
    packages             = convert_packages_argument(packages)

    missing_packages = []
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing_packages.append(pkg)

    if len(missing_packages) > 0:
        raise PrerequisiteError('Missing %s module(s)' % missing_packages)

    installed_version = pkg_resources.get_distribution('gslab_tools').version.split('.')
    installed_version = int(installed_version[0]) * 10000 + \
                        int(installed_version[1]) * 100 + \
                        int(installed_version[2])
    required_version = gslab_python_version.split('.')
    required_version = int(required_version[0]) * 10000 + \
                       int(required_version[1]) * 100 + \
                       int(required_version[2])
    if installed_version < required_version:
        raise PrerequisiteError('Wrong version of gslab_tools python modules')

def convert_packages_argument(packages):
    if not isinstance(packages, list):
        if isinstance(packages, str):
            packages = [packages]
        else:
            raise PrerequisiteError('Please supply a python list of required' + \
                                    'packages, not %s.' % packages)
    for pkg in packages:
        if not isinstance(pkg, str):
            raise PrerequisiteError('All packages should be strings,' + \
                                    ' not %s.' % pkg)          
    return packages

def check_r(packages = ["yaml"]):
    if is_in_path('R.exe') is None and is_in_path('R') is None:
        raise PrerequisiteError('R is not installed or excecutable is not added to path')
    check_r_packages(packages)

def check_r_packages(packages):
    packages = convert_packages_argument(packages)
    missing_packages = []
    for pkg in packages:
        # http://stackoverflow.com/questions/6701230/call-r-function-in-linux-command-line
        # and http://stackoverflow.com/questions/18962785/oserror-errno-2-no-such-file-or-directory-while-using-python-subprocess-in-dj
        try:
            subprocess.check_output('R -q -e "suppressMessages(library(%s))"' % pkg, shell = True)
        except subprocess.CalledProcessError:
            missing_packages.append(pkg)

    if len(missing_packages) > 0:
        raise PrerequisiteError("R packages, %s, not found." % missing_packages)

def check_lyx():
    if is_in_path('lyx.exe') is None and is_in_path('lyx') is None:
        raise PrerequisiteError('Lyx is not installed or executable is not added to path')

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
    sf = load_yaml_value(user_yaml, "stata_executable")

    # Fake scons-like env dict for misc.get_stata_executable(env)
    fake_env = {'user_flavor': sf} 
    stata_exec = get_stata_executable(fake_env)
    
    if stata_exec is None:
        raise PrerequisiteError('Stata is not installed or executable is not added to path')
    
    command = get_stata_command(stata_exec)
    check_stata_packages(command, packages)
    return sf

def load_yaml_value(path, key):
    import yaml

    if key == "stata_executable":
        prompt = "Enter %s value or None to search for defaults: "
    else:
        prompt = "Enter %s value: "

    # Check if file exists and is not corrupted. 
    # If so, load yaml contents.
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
                raise PrerequisiteError("%s is a corrupted yaml file. Please fix." % path)

    # If key exists, return value.
    # Otherwise, add key-value to file.
    try:
        if yaml_contents[key] == "None":
            return None
        else:
            return yaml_contents[key]
    except:
        with open(path, 'ab') as f:        
            val = str(raw_input(prompt % key))
            if re.sub('"', '', re.sub('\'', '', val.lower())) == "none":
                val = None
            f.write('\n%s: %s\n' % (key, val))
        return val

def check_stata_packages(command, packages):
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
            # and http://stackoverflow.com/questions/18962785/oserror-errno-2-no-such-file-or-directory-while-using-python-subprocess-in-dj
            subprocess.check_output(call, stderr = subprocess.STDOUT, shell = True) 
            
            with open('stata.log', 'rU') as f:
                log = f.read()
            os.remove('stata.log')

            if re.search('command %s not found' % pkg, log):
                raise PrerequisiteError('Stata package %s is not installed' % pkg)

    except subprocess.CalledProcessError:
        raise PrerequisiteError("Stata command, '%s', failed.\n" % command.split(' ')[0] + \
                                "\t\t   Please supply a correct stata_executable" + \
                                " value in user_config.yaml.\n" )


