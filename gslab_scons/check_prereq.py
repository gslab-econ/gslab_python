import sys
import subprocess
import pkg_resources

import misc
from _exception_classes import PrerequisiteError


def check_prereq(prereq, manual_execs = {}, gslab_vers = None):
    '''
    '''
    prereq_clean = str(prereq).lower().strip()
    path_checkers = ['r', 'stata', 'matlab', 'lyx', 'latex']
    if prereq_clean in path_checkers:
        executable = misc.get_executable(prereq_clean, manual_execs)
        if not misc.is_in_path(executable):
            message = 'Cannot find executable for %s in PATH.' % prereq_clean
            raise PrerequisiteError(message)
    elif prereq_clean == 'python':
        if sys.version_info[0] != 2:
            raise PrerequisiteError('Please use Python 2')
    elif prereq_clean == 'gslab_python':
        required_version  = process_gslab_version(gslab_vers)
        installed_version = pkg_resources.get_distribution('gslab_tools').version
        installed_version = process_gslab_version(installed_version)
        if not check_gslab_version(installed_version, required_version):
            message = 'Your version of gslab_python (%s) is outdated. ' \
                      'This repository requires gslab_python %s or higher to run' \
                      % ('.'.join(installed_version), '.'.join(required_version))
            raise PrerequisiteError(message)
    elif prereq_clean == 'git_lfs':
        check_git_lfs()
    else:
        message = 'Cannot find prerequisite check for %s' % prereq
        raise PrerequisiteError(message)
    return None


def process_gslab_version(gslab_version):
    '''
    '''
    try:
        vers = gslab_version.split('.')
    except:
        message = 'You must pass gslab_version as a string value.'
        raise PrerequisiteError(message)
    if len(vers) != 3:
        message = 'The gslab_version argument must have exectly two periods `.` ' \
                  'to corrsepond to semantic versioning.'
        raise PrerequisiteError(message)
    try:
        vers = [int(val) for val in vers]
    except ValueError:
        message = 'All components of gslab_version between periods ' \
                  'must be expressable as integers.'
        raise PrerequisiteError(message)
    return vers


def check_gslab_version(required, installed):
    '''
    '''
    required_val = required[0]
    installed_val = installed[0]
    # Recursive case
    if required_val == installed_val:
        check_gslab_version(required[1:], installed[1:])
    # Base cases
    elif required_val > installed_val:
        up_to_date = True
    else:
        up_to_date = False
    return up_to_date


def check_git_lfs():
    '''
    '''
    try:
        _ = subprocess.check_output('git-lfs install', shell = True)
    except subprocess.CalledProcessError:
        try:
            _ = subprocess.check_output('git-lfs init', shell = True)
        except subprocess.CalledProcessError:
            message = "Either Git LFS is not installed " \
                      "or your Git LFS settings need to be updated. " \
                      "Please install Git LFS or run " \
                      "'git lfs install --force' if prompted above."
            raise PrerequisiteError(message)
    return None
