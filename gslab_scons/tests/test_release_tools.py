#! /usr/bin/env python
import unittest
import sys
import os
import re
import subprocess
import shutil

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons._release_tools as tools
from gslab_make.tests import nostderrout


class test_misc(unittest.TestCase):

    def test_up_to_date(self):
        '''
        Test that up_to_date() correctly recognises
        an SCons directory as up-to-date or out of date.
        '''

        # Check out a stable commit of gslab-econ/template on which
        # to test the function.
        command = 'git clone git@github.com:gslab-econ/template.git .test_up_to_date'
        null_out = open(os.devnull, 'wb')
        subprocess.call(command, shell = True,
                        stdout = null_out, 
                        stderr = subprocess.STDOUT)
        initial_wd = os.getcwd()
        os.chdir('.test_up_to_date')
        subprocess.call('git checkout 046ce99fb897f0d09', shell = True,
                        stdout = null_out, 
                        stderr = subprocess.STDOUT)
        
        # At freshly cloned commit, sconsign.dblite should be unmodified.
        # But there should be unconstructed SCons targets.
        self.assertTrue(tools.up_to_date(mode = 'git'))
        self.assertFalse(tools.up_to_date(mode = 'scons'))
        
        # Calling SCons should build all targets and change sconsign.dblite.
        subprocess.call('scons', shell = True,
                        stdout = null_out, 
                        stderr = subprocess.STDOUT)
        self.assertFalse(tools.up_to_date(mode = 'git'))
        self.assertTrue(tools.up_to_date(mode = 'scons'))
        
        null_out.close()
        os.chdir(initial_wd)

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

    def tearDown(self):
        if os.path.isdir('.test_up_to_date'):
            shutil.rmtree('.test_up_to_date')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
