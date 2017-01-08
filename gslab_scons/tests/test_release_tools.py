import unittest
import sys
import os
import re
import subprocess
import shutil
import mock

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons
import gslab_scons._release_tools as tools
from gslab_scons._exception_classes import ReleaseError
from gslab_make.tests import nostderrout


class test_misc(unittest.TestCase):

    @mock.patch('gslab_scons._release_tools.subprocess.call')
    def test_up_to_date(self, mock_call):
        '''
        Test that up_to_date() correctly recognises
        an SCons directory as up-to-date or out of date.
        '''
        # The mock of subprocess call should write pre-specified text
        # to stdout. This mock prevents us from having to set up real
        # SCons and git directories.
        mock_call.side_effect = self.make_side_effect('Your branch is up-to-date')
        self.assertTrue(gslab_scons._release_tools.up_to_date(mode = 'git'))
        mock_call.side_effect = self.make_side_effect('modified:   .sconsign.dblite')
        self.assertFalse(gslab_scons._release_tools.up_to_date(mode = 'git'))

        mock_call.side_effect = self.make_side_effect("scons: `.' is up to date.")
        self.assertTrue(gslab_scons._release_tools.up_to_date(mode = 'scons'))
        mock_call.side_effect = self.make_side_effect('python some_script.py')
        self.assertFalse(gslab_scons._release_tools.up_to_date(mode = 'scons'))
        
        # The up_to_date() function shouldn't work in SCons or git mode
        # when it is called outside of a SCons directory or a git 
        # repository, respectively.       
        mock_call.side_effect = self.make_side_effect("Not a git repository")
        with self.assertRaises(ReleaseError), nostderrout():
            gslab_scons._release_tools.up_to_date(mode = 'git')

        mock_call.side_effect = self.make_side_effect("No SConstruct file found")
        with self.assertRaises(ReleaseError), nostderrout():
            gslab_scons._release_tools.up_to_date(mode = 'scons')   

    @staticmethod
    def make_side_effect(text):
        '''
        Return a side effect to be used with mock that
        prints text to a file specified as the stderr
        argument of function being mocked.
        '''
        def side_effect(*args, **kwargs):
            log = kwargs['stdout']
            log.write(text)
            
        return side_effect

    def test_extract_dot_git(self):
        '''
        Test that extract_dot_git() correctly extracts repository
        information from a .git folder's config file.
        '''
        test_dir  = os.path.dirname(os.path.realpath(__file__))
        git_dir   = os.path.join(test_dir, '../../.git')
        repo_info = tools.extract_dot_git(git_dir)
        self.assertEqual(repo_info[0], 'gslab_python')
        self.assertEqual(repo_info[1], 'gslab-econ')

    def test_create_size_dictionary(self):
        '''
        Test that create_size_dictionary() correctly reports
        files' sizes in bytes.
        '''
        test_dir = os.path.dirname(os.path.realpath(__file__))
        test_dir = os.path.join(test_dir, 'input/size_test') 
        sizes    = tools.create_size_dictionary(test_dir)

        # Check that test.txt and test.jpg are in the dictionary
        txt_path = [path for path in sizes.keys() if re.search('test.txt$', path)]
        jpg_path = [path for path in sizes.keys() if re.search('test.jpg$', path)]

        self.assertTrue(bool(txt_path))
        self.assertTrue(bool(jpg_path))

        # Check that the size dictionary reports these files' correct sizes in bytes
        self.assertEqual(sizes[txt_path[0]], 93)
        self.assertEqual(sizes[jpg_path[0]], 149084)

if __name__ == '__main__':
    os.getcwd()
    unittest.main()
