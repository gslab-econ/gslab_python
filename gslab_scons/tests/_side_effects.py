import os
import re
import subprocess
import _test_helpers as helpers


def r_side_effect(*args, **kwargs):
    '''
    This side effect mocks the behaviour of a system call
    on a machine with R set up for command-line use.
    '''
    # Get and parse the command passed to os.system()
    command = args[0]
    match   = helpers.command_match(command, 'R')

    executable = match.group('executable')
    log        = match.group('log')

    if log is None:
        # If no log path is specified, the R script's after 
        # removing .R (if present) and adding .Rout.
        source = match.group('source')
        log    = '%s.Rout' % re.sub('\.R', '', source)

    if executable == "R CMD BATCH" and log:
        with open(log.strip(), 'wb') as log_file:
            log_file.write('Test log\n')


def python_side_effect(*args, **kwargs):
    command = args[0]
    match   = helpers.command_match(command, 'python')

    if match.group('log'):
        log_path = re.sub('(\s|>)', '', match.group('log'))
        with open(log_path, 'wb') as log_file:
            log_file.write('Test log')


def matlab_side_effect(*args, **kwargs):
    '''Mock os.system for Matlab commands'''
    try:
        command = kwargs['command']
    except KeyError:
        command = args[0]

    log_match = re.search('> (?P<log>[-\.\w\/]+)', command)

    if log_match:
        log_path = log_match.group('log')
        with open(log_path, 'wb') as log_file:
            log_file.write('Test log')

    return None


def make_stata_side_effect(recognised_command):
    '''
    Make a side effect mocking the behaviour of 
    subprocess.check_output() when `recognised_command` is
    the only recognised system command. 
    '''
    def stata_side_effect(*args, **kwargs):
        command = args[0]
        match   = helpers.command_match(command, 'stata')

        if match.group('executable') == recognised_command:
            # Find the Stata script's name
            script_name = match.group('source')
            stata_log   = os.path.basename(script_name).replace('.do','.log')
            
            # Write a log
            with open(stata_log, 'wb') as logfile:
                logfile.write('Test Stata log.\n')

        else:
            # Raise an error if the exectuable is not the only recognised one.
            raise subprocess.CalledProcessError(1, command)

    return stata_side_effect


def lyx_side_effect(*args, **kwargs):
    '''
    This side effect mocks the behaviour of a system call.
    The mocked machine has lyx set up as a command-line executable
    and can export .lyx files to .pdf files only using 
    the "-e pdf2" option.
    '''
    # Get and parse the command passed to os.system()
    command = args[0]
    match = re.match('\s*'
                        '(?P<executable>\w+)'
                        '\s+'
                        '(?P<option>-\w+ \w+)?'
                        '\s*'
                        '(?P<source>[\.\/\w]+\.\w+)?'
                        '\s*'
                        '(?P<log_redirect>\> [\.\/\w]+\.\w+)?',
                     command)

    executable   = match.group('executable')
    option       = match.group('option')
    source       = match.group('source')
    log_redirect = match.group('log_redirect')

    option_type    = re.findall('^(-\w+)',  option)[0]
    option_setting = re.findall('\s(\w+)$', option)[0]

    is_lyx = bool(re.search('^lyx$', executable, flags = re.I))

    # As long as output is redirected, create a log
    if log_redirect:
        log_path = re.sub('>\s*', '', log_redirect)
        with open(log_path, 'wb') as log_file:
            log_file.write('Test log\n')

    # If LyX is the executable, the options are correctly specified,
    # and the source exists, produce a .pdf file with the same base 
    # name as the source file.

    # Make a mocked-up comprehensive list of existing files
    existing_files = ['test_script.lyx', './input/lyx_test_file.lyx']
    source_exists  = os.path.abspath(source) in \
                         map(os.path.abspath, existing_files)

    if is_lyx and option_type == '-e' and option_setting == 'pdf2' \
              and source_exists:
        out_path = re.sub('lyx$', 'pdf', source, flags = re.I)
        with open(out_path, 'wb') as out_file:
            out_file.write('Mock .pdf output')
