import os
import re
import mock
import requests
import shutil
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
        # If no log path is specified, create one by using the 
        # R script's path after replacing .R (if present) with .Rout.
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
            stata_log   = os.path.basename(script_name).replace('.do', '.log')
            
            # Write a log
            with open(stata_log, 'wb') as logfile:
                logfile.write('Test Stata log.\n')

        else:
            # Raise an error if the executable is not recognised.
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
    match = helpers.command_match(command, 'lyx')

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

    # Mock a list of the files that LyX sees as existing
    # source_exists should be True only if the source script 
    # specified in the system command belongs to existing_files. 
    existing_files = ['test_script.lyx', './input/lyx_test_file.lyx']
    source_exists  = os.path.abspath(source) in \
                         map(os.path.abspath, existing_files)

    if is_lyx and option_type == '-e' and option_setting == 'pdf2' \
              and source_exists:
        out_path = re.sub('lyx$', 'pdf', source, flags = re.I)
        with open(out_path, 'wb') as out_file:
            out_file.write('Mock .pdf output')


def make_call_side_effect(text):
    '''
    Intended for mocking the subprocess.call() in testing
    _release_tools.up_to_date(). Return a side effect that
    prints text to mocked function's stdout argument.
    '''
    def side_effect(*args, **kwargs):
        log = kwargs['stdout']
        log.write(text)
        
    return side_effect


def upload_asset_side_effect(*args, **kwargs):
    '''
    This side effect, intended for mocking 
    _release_tools.upload_asset() in testing release(), 
    copies an asset so it can be checked by tests. 
    '''
    assets_path    = kwargs['file_name']
    shutil.copyfile(assets_path, 'assets_listing.txt')    


def post_side_effect(*args, **kwargs):
  '''
  Intended for mocking requests.session.post in testing release().
  This side effect returns a MagicMock that raises an error 
  when its raise_for_status() method is called unless
  a specific release_path is specified.
  '''
  # The release path is specified by the first positional argument.
  mock_output = mock.MagicMock(raise_for_status = mock.MagicMock())
  release_path = args[0]
  real_path = "https://test_token:@api.github.com/repos/org/repo/releases"

  def raise_http_error():
      raise requests.exceptions.HTTPError('404 Client Error')

  if release_path != real_path:
      mock_output.raise_for_status.side_effect = raise_http_error

  return mock_output  


def dot_git_open_side_effect(repo   = 'repo',
                             org    = 'org',
                             branch = 'branch',
                             url    = True):
    '''
    This function produces a side effect mocking the behaviour of
    open() when used to read the lines of the 'config' or 'HEAD' file
    in a GitHub repository's '.git' directory.
    '''

    def open_side_effect(*args, **kwargs):
        path = args[0]
        if path not in ['.git/config', '.git/HEAD']:
            raise Exception('Cannot open %s' % path)

        # If specified by the url argument, include the url of the origin
        # in the mock .git file, as is standard. 
        github_url = '\turl = https://github.com/%s/%s\n' % (org, repo)
        github_url = ['', github_url][int(url)]

        if path == '.git/config':
            # These are the mocked contents of a .git/config file
            lines = ['[core]\n', 
                         '\trepositoryformatversion = 0\n', 
                         '\tfilemode = true\n', 
                         '\tbare = false\n', 
                         '\tlogallrefupdates = true\n', 
                         '\tignorecase = true\n', 
                         '\tprecomposeunicode = true\n', 
                     '[remote "origin"]\n', 
                         github_url, 
                         '\tfetch = +refs/heads/*:refs/remotes/origin/*\n', 
                     '[branch "master"]\n', 
                         '\tremote = origin\n', 
                     '\tmerge = refs/heads/master\n']

        elif path == '.git/HEAD':
            # These are the mocked contents of a .git/HEAD file
            lines = ['ref: refs/heads/%s\n' % branch]

        # Ultimately return a mock whose readlines() method
        # just returns a list of lines from our mocked-up file.
        file_object = mock.MagicMock(readlines = lambda: lines)

        return file_object

    return open_side_effect


#== Side effects for testing create_size_dictionary() ===
# These functions mock a directory containing files of various sizes
# and a system that recognises no directory other than that one.
def isdir_side_effect(*args, **kwargs):
    '''
    Mock os.path.isdir() so that it only recognises ./test_files/
    as an existing directory.
    '''
    path = args[0]
    if not isinstance(path, str):
        raise TypeError('coercing to Unicode: need string or buffer, '
                        '%s found' % type(path))
    return path == 'test_files'


def walk_side_effect(*args, **kwargs):
    '''
    Mock os.walk() for a mock directory called ./test_files/.
    '''
    path = args[0]

    if path != 'test_files':
        raise StopIteration

    roots       = ['test_files',      'test_files/size_test']
    directories = [['size_test'],     []]
    files       = [['root_file.txt'], ['test.txt', 'test.pdf']]

    for i in range(len(roots)):
        yield (roots[i], directories[i], files[i])


def getsize_side_effect(*args, **kwargs):
    '''
    Mock os.path.getsize() to return mock sizes of files in our
    mock ./test_files/ directory.
    '''
    path = args[0]
    if path == 'test_files/root_file.txt':
        size = 100
    elif path == 'test_files/size_test/test.txt':
        size = 200
    elif path == 'test_files/size_test/test.pdf':
        size = 1000
    else:
        raise OSError("[Errno 2] No such file or directory: '%s'" % path)

    return size



