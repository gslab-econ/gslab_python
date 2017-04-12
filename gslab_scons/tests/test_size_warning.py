import unittest
import sys
import os
import re
import mock

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons
import gslab_scons.size_warning as sw
from gslab_scons._exception_classes import ReleaseError
from gslab_make.tests import nostderrout


class TestSizeWarning(unittest.TestCase):

    @mock.patch('gslab_scons.size_warning.raw_input')
    @mock.patch('gslab_scons.size_warning.create_size_dictionary')
    @mock.patch('gslab_scons.size_warning.list_ignored_files')
    def test_issue_size_warnings(self, mock_list_ignored, mock_create_dict,
                                 mock_input):
        bytes_in_MB = 1000000
        big_size = 3
        small_size = 1
        total_size = big_size + small_size
        mock_create_dict.return_value = {'large.txt':   big_size*bytes_in_MB,
                                         'small.txt': small_size*bytes_in_MB}
        mock_list_ignored.return_value = ['large.txt']
        mock_input.return_value = 'y'

        look_in = ['.']

        # Neither file over limit
        sw.issue_size_warnings(look_in,
                               file_MB_limit  = big_size + 0.1, 
                               total_MB_limit = big_size + 0.1)
        mock_input.assert_not_called()
        # Only ignored filed over limit
        sw.issue_size_warnings(look_in,
                               file_MB_limit  = big_size - 0.1, 
                               total_MB_limit = big_size + 0.1)
        mock_input.assert_not_called()
        
        # Ignored file no longer ignored
        mock_list_ignored.return_value = []
        with nostderrout():
            sw.issue_size_warnings(look_in,
                                   file_MB_limit  = big_size - 0.1, 
                                   total_MB_limit = total_size + 0.1)
        mock_input.assert_called_once()
        mock_input.reset_mock()

        # Both files over limit
        mock_list_ignored.return_value = []
        with nostderrout():
            sw.issue_size_warnings(look_in,
                                   file_MB_limit  = small_size - 0.1, 
                                   total_MB_limit = total_size + 0.1)
        self.assertEqual(mock_input.call_count, 2)
        mock_input.reset_mock()

        # No file over limit, but total size over limit
        with nostderrout():
            sw.issue_size_warnings(look_in,
                                   file_MB_limit  = big_size + 0.1, 
                                   total_MB_limit = total_size - 0.1)
        mock_input.assert_called_once()
        mock_input.reset_mock()

        # Large over limit and total size over limit
        with nostderrout():
            sw.issue_size_warnings(look_in,
                                   file_MB_limit = big_size - 0.1, 
                                   total_MB_limit = total_size - 0.1)
        self.assertEqual(mock_input.call_count, 2)
        mock_input.reset_mock()    

    @mock.patch('gslab_scons.size_warning.os.path.isfile')
    @mock.patch('gslab_scons.size_warning.os.path.isdir')
    @mock.patch('gslab_scons.size_warning.os.walk')
    @mock.patch('gslab_scons.size_warning.subprocess.check_output')
    def test_list_ignored_files(self, mock_check, mock_walk,
                                mock_isdir, mock_isfile):
        mock_check.side_effect  = check_ignored_side_effect('standard')
        mock_walk.side_effect   = walk_ignored_side_effect
        mock_isdir.side_effect  = isdir_ignored_side_effect
        mock_isfile.side_effect = isfile_ignored_side_effect

        look_in = ['raw', 'release']
        ignored = sw.list_ignored_files(look_in)
        expect_ignored = ['raw/large_file.txt',
                          'release/.DS_Store', 
                          'release/subdir/ignored.txt']
        print ignored
        self.assertEqual(len(ignored), len(expect_ignored))
        for i in range(len(ignored)):
            self.assertIn(ignored[i], expect_ignored)


        look_in = ['raw']
        ignored = sw.list_ignored_files(look_in)
        expect_ignored = ['raw/large_file.txt']

        self.assertEqual(len(ignored), len(expect_ignored))
        self.assertEqual(ignored[0], expect_ignored[0])       

        # Test that list_ignored_files returns an empty list when 
        # git is not ignoring any files.
        mock_check.side_effect  = check_ignored_side_effect(ignored = 'none')
        ignored = sw.list_ignored_files(look_in)

        self.assertIsInstance(ignored, list)
        self.assertEqual(len(ignored), 0)

    @mock.patch('gslab_scons.size_warning.os.path.getsize')
    @mock.patch('gslab_scons.size_warning.os.walk')
    @mock.patch('gslab_scons.size_warning.os.path.isdir')
    def test_create_size_dictionary(self, mock_isdir, mock_walk, mock_getsize):
        '''
        Test that create_size_dictionary() correctly reports
        files' sizes in bytes.
        '''
        # Assign side effects
        mock_isdir.side_effect   = isdir_dict_side_effect        
        mock_walk.side_effect    = walk_dict_side_effect
        mock_getsize.side_effect = getsize_dict_side_effect 

        # Test when one directory is provided
        sizes = sw.create_size_dictionary(['test_files'])

        self.assertEqual(len(sizes), 3)

        # Check that test.txt and test.jpg are in the dictionary
        root_path = [k for k in sizes.keys() if re.search('root_file.txt$', k)]
        pdf_path  = [k for k in sizes.keys() if re.search('test.pdf$', k)]
        self.assertTrue(bool(root_path))
        self.assertTrue(bool(pdf_path))

        # Check that the size dictionary reports these files' correct sizes in bytes
        self.assertEqual(sizes[root_path[0]], 100)
        self.assertEqual(sizes[pdf_path[0]], 1000)

        # Check when two directories are provided
        sizes = sw.create_size_dictionary(['test_files', 'release'])
        self.assertEqual(len(sizes), 4)
        path = [k for k in sizes.keys() if re.search('output.txt$', k)]
        self.assertTrue(bool(path))
        self.assertEqual(sizes[path[0]], 16)

        # Check that the function raises an error when its path argument
        # is not a directory.
        with self.assertRaises(ReleaseError), nostderrout():
            sizes = sw.create_size_dictionary(['nonexistent_directory'])
        # The path argument must be a string
        with self.assertRaises(TypeError), nostderrout():
            sizes = sw.create_size_dictionary([10])


#== Side effects for testing list_ignored_files() ===
# Define the mock file structure for testing list_ignored_files()
struct = {'.': ['untracked.txt', 'make.log', 'make.py'],
         'raw': ['large_file.txt', 'small_file.txt'], 
         'release': ['output.txt', '.DS_Store'],
         'release/subdir': ['ignored.txt']}

def check_ignored_side_effect(ignored = 'standard'):

    def effect(*args, **kwargs):
        '''Mock subprcess.check_output() for testing list_ignored_files()'''
    
        # Define mock messages from "git status --ignored"
        # i) Some files are ignored
        standard = \
            ['On branch testing\n',
             'Your branch is up-to-date with \'origin/testing\'.\n',
             'Changes not staged for commit:\n',
             '  (use "git add/rm <file>..." to update what will be committed)\n',
             '  (use "git checkout -- <file>..." to discard changes in working directory)\n',
             '\n',
             '\tmodified:   make.log\n',
             '\n',
             'Untracked files:\n',
             '  (use "git add <file>..." to include in what will be committed)\n',
             '\n',
             '\tuntracked.txt',
             '\n',
             'Ignored files:\n',
             '  (use "git add -f <file>..." to include in what will be committed)\n',
             '\n',
             '\traw/large_file.txt\n',
             '\trelease/.DS_Store\n',
             '\trelease/subdir/'
             '\n',
             '\n',
             'It took 2.44 seconds to enumerate untracked files. \'status -uno\'\n',
             'may speed it up, but you have to be careful not to forget to add\n',
             'new files yourself (see \'git help status\').\n',
             'no changes added to commit (use "git add" and/or "git commit -a")\n']
        
        # ii) No files are ignored
        none_ignored = \
            ['On branch issue59-size_warnings\n',
             'Your branch is up-to-date with \'origin/issue59-size_warnings\'.\n',
             'nothing to commit, working tree clean\n']

        if ignored == 'none':
            message = ''.join(none_ignored)
        else:
            message = ''.join(standard)

        command = args[0]
        if 'shell' in kwargs.keys():
            if kwargs['shell'] and (command == 'git status --ignored'):
                return message
    
        return None

    return effect


def walk_ignored_side_effect(*args, **kwargs):
    '''Mock os.walk() for testing list_ignored_files()'''
    path = args[0]
    path = os.path.relpath(path)

    if path not in struct.keys():
        raise StopIteration

    if path == 'release':
        subdirs = ['subdir']
    else:
        subdirs = []

    yield (path, subdirs, struct[path])
 

def isdir_ignored_side_effect(*args, **kwargs):
    path = args[0]
    if path == '':
        return False
        
    isdir = (os.path.relpath(path) in struct.keys())
    return isdir


def isfile_ignored_side_effect(*args, **kwargs):
    path = args[0]
    if path == '':
        return False

    file_list = []

    for k in struct.keys():
        file_list += [os.path.join(k, f) for f in struct[k]]

    isfile = (os.path.relpath(path) in map(os.path.relpath, file_list))
    return isfile


#== Side effects for testing create_size_dictionary() ===
# These functions mock a directory containing files of various sizes
# and a system that recognises no directory other than that one.
def isdir_dict_side_effect(*args, **kwargs):
    '''
    Mock os.path.isdir() so that it only recognises ./test_files/
    as an existing directory.
    '''
    path = args[0]
    if not isinstance(path, str):
        raise TypeError('coercing to Unicode: need string or buffer, '
                        '%s found' % type(path))
    return path in ['test_files', 'release']


def walk_dict_side_effect(*args, **kwargs):
    '''Mock os.walk() for a mock directory called ./test_files/.'''
    path = args[0]

    # Mock two directories at the root, one of which has a subdirectory
    roots       = ['test_files',      'test_files/size_test',   'release']
    directories = [['size_test'],     [],                       []]
    files       = [['root_file.txt'], ['test.txt', 'test.pdf'], ['output.txt']]

    for i in range(len(roots)):
        if re.search('^%s' % path, roots[i]):
            yield (roots[i], directories[i], files[i])


def getsize_dict_side_effect(*args, **kwargs):
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
    elif path == 'release/output.txt':
        size = 16
    else:
        raise OSError("[Errno 2] No such file or directory: '%s'" % path)

    return size


if __name__ == '__main__':
    unittest.main()
