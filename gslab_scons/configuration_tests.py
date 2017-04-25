import sys
import importlib
import subprocess
from _exception_classes import PrerequisiteError

def check_python(gslab_python_version, 
                 packages = ["yaml", "gslab_scons", "gslab_make", "gslab_fill"]):
    if sys.version_info[0] != 2:
        raise PrerequisiteError('Please use python 2')
    check_python_packages(gslab_python_version, packages)

def check_python_packages(gslab_python_version, packages):
    gslab_python_version = str(gslab_python_version)
    if not isinstance(packages, list):
        if isinstance(packages, str):
            packages = [packages]
        else:
            raise PrerequisiteError('Please supply a python list of required' + \
                                    'packages, not %s.' % packages)
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except:
            raise PrerequisiteError('Missing %s module' % pkg)

    if pkg_resources.get_distribution('gslab_tools').version < gslab_python_version:
        raise PrerequisiteError('Wrong version of gslab_python modules')

def check_r(packages = ["yaml"]):
    from gslab_scons.misc import is_in_path
    if is_in_path('R.exe') is None and is_in_path('R') is None:
        raise PrerequisiteError('R is not installed or excecutable is not added to path')
    check_r_packages(packages)

def check_r_packages(packages):
    for pkg in packages:
        # http://stackoverflow.com/questions/6701230/call-r-function-in-linux-command-line
        # and http://stackoverflow.com/questions/18962785/oserror-errno-2-no-such-file-or-directory-while-using-python-subprocess-in-dj
        subprocess.check_output('R -q -e "library(%s)"' % pkg, shell = True)

def check_lyx():
    from gslab_scons.misc import is_in_path
    if is_in_path('lyx.exe') is None and is_in_path('lyx') is None:
        raise PrerequisiteError('Lyx is not installed or excecutable is not added to path')

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


def check_stata(ARGUMENTS, packages = ["yaml"], user_yaml = "user-config.yaml"):
    import yaml
    import gslab_scons.misc as misc

    sf_configs = load_yaml_value(user_yaml, "stata_executable")
    sf         = ARGUMENTS.get('sf', sf_configs) 

    # Fake scons-like env dict for misc.get_stata_executable(env)
    fake_env = {'user_flavor': sf} 
    stata_exec = misc.get_stata_executable(fake_env)
    
    if stata_exec is None:
        raise PrerequisiteError('Stata is not installed or executable is not added to path')
    
    command = misc.get_stata_command(stata_exec)
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
    import gslab_scons.misc as misc
    if misc.is_unix():
        command = command.split("%s")[0]
    elif sys.platform == "win32":
        command = command.split("do")[0]

    try:
        for pkg in packages:
            call = (command + "which %s") % pkg
            # http://www.stata.com/statalist/archive/2009-12/msg00493.html 
            # and http://stackoverflow.com/questions/18962785/oserror-errno-2-no-such-file-or-directory-while-using-python-subprocess-in-dj
            subprocess.check_output(call, stderr = subprocess.STDOUT, shell = True) 
            with open('stata.log', 'rU') as f:
                log = f.read()
    except subprocess.CalledProcessError:
        raise PrerequisiteError("Stata command, '%s', failed.\n" % command.split(' ')[0] + \
                                "\t\t   Please supply a correct stata_executable" + \
                                " value in user_config.yaml.\n" )

    os.remove('stata.log')
    if re.search('command %s not found' % pkg, log):
        raise PrerequisiteError('Stata package %s is not installed' % pkg)



