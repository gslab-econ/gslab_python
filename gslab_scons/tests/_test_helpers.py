import os
import re
import sys
import mock
import inspect

sys.path.append('../..')
import gslab_scons.misc as misc
from gslab_scons._exception_classes import BadExtensionError


def platform_patch(platform, path):
    '''
    This script produces a mock.patch decorator that mocks
    sys.platform as `platform` in both the module given by 
    `path` and, if possible, this module's
    imported misc module. 
    '''
    main_patch  = mock.patch('%s.sys.platform' % path, platform)
    
    # Try to also patch misc.sys.platform
    try:
        misc_patch  = mock.patch('%s.misc.sys.platform' % path, platform)
        total_patch = lambda f: misc_patch(main_patch(f))
    except ImportError:
        total_patch = main_patch

    return total_patch

def command_match(command, executable, which = None):
    if executable in ['python', 'py']:
        match = re.match('\s*'
                         '(?P<executable>python)'
                         '\s*'
                         '(?P<source>[-\.\/\w]+)'
                         '\s*'
                         '(?P<args>(\s?[\.\/\w]+)*)?'
                         '\s*'
                         '(?P<log>>\s*[\.\/\w]+)?',
                         command)

    elif executable in ['r', 'R']:
        match = re.match('\s*'
                         '(?P<executable>R CMD BATCH)'
                         '\s+'
                         '(?P<option>--no-save)?'
                         '\s*'
                         "(?P<args>'--args .*')?"
                         '\s*'
                         '(?P<source>[\.\/\w]+\.[rR])'
                         '\s*'
                         '(?P<log>[\.\/\w]+(\.\w+)?)?',
                         command)  

    elif executable in ['stata', 'do']: 
        match = re.match('\s*'
                         '(?P<executable>\S+)'
                         '\s+'
                         '(?P<options>(\s?[-\/][-A-Za-z]+)+)?'
                         '\s*'
                         '(?P<do>do)?'
                         '\s*'
                         '(?P<source>[\.\/\w]+\.do)'
                         '\s*'
                         '(?P<args>.*)',
                         command)

    if which:
        return match.group(which)
    else:
        return match


def check_log(test_object, log_path, timestamp = True):
    '''Check for the existence of a timestamped log'''
    with open(log_path, 'rU') as log_file:
        log_data = log_file.read()

    if timestamp:
        test_object.assertIn('Log created:', log_data)
    else:
        test_object.assertNotIn('Log created:', log_data)

    os.remove(log_path)


def bad_extension(test_object, builder, 
                  bad  = 'bad',
                  good = None,
                  env = {}):
    if good:
        source = [bad, good]
    else:
        source = [bad]

    with test_object.assertRaises(BadExtensionError):
        builder(target = './test_output.txt', 
                source = [bad, good], 
                env    = env)

def standard_test(test_object, builder, 
                  extension   = None,  
                  system_mock = None,
                  source = None,
                  target = None,
                  env    = None):

    if not source:
        source = './test_script.%s' % extension
    if not target:
        target = './test_output.txt'
    if not env:
        env = {}

    builder(source = source, target = target, env = env)
    
    if isinstance(target, str):
        log_directory = misc.get_directory(target)
    else:
        log_directory = misc.get_directory(target[0])

    log_path = os.path.join(log_directory, 'sconscript.log')
    check_log(test_object, log_path)

    if system_mock:
        system_mock.assert_called_once()
        system_mock.reset_mock()


def input_check(test_object, builder, extension,
                source = 'missing',
                target = 'missing',
                env    = 'missing',
                error  = 'missing'):
    # If alternatives are not provided, define 
    # standard builder arguments
    if source == 'missing':
        source = 'test_script.%s' % extension
    if target == 'missing':
        target = './test_output.txt'
    if env == 'missing':
        env    = {}

    if not error:
        builder(source = source, target = target, env = env)
        check_log(test_object, './sconscript.log')
    else:
        with test_object.assertRaises(error):
            builder(source = source, target = target, env = env)


def test_cl_args(test_object, builder, system_mock, extension,
                 env = {}):
    
    source = './test_script.%s' % extension
    target = './test_output.txt'

    # i) Single command line argument
    if env:
        env['CL_ARG'] = 'test'
    else:
        env = {'CL_ARG': 'test'}
    
    builder(source = source, target = target, env    = env)

    # The system command is the first positional argument
    command = system_mock.call_args[0][0] 
    args    = command_match(command, extension, which = 'args')
    if extension in ['r', 'R']:
        args = re.sub("('|--args)", '', args).strip()

    test_object.assertIn('test', args.split(' '))
    test_object.assertEqual(len(args.split(' ')), 1)
    check_log(test_object, './sconscript.log')

    # Multiple command line arguments
    env['CL_ARG'] = [1, 2, None]

    builder(source = source, 
            target = target, 
            env    = env)

    command = system_mock.call_args[0][0] 
    args    = command_match(command, extension, which = 'args')
    if extension in ['r', 'R']:
        args = re.sub("('|--args)", '', args).strip()

    for arg in env['CL_ARG']:
        test_object.assertIn(str(arg), args.split(' '))

    test_object.assertEqual(len(args.split(' ')), 3)
    check_log(test_object, './sconscript.log')
