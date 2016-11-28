#! /usr/bin/env python
import unittest
import sys
import os
import re

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons._release_tools as tools



class test_misc(unittest.TestCase):

    def test_release(self):
        pass

    def test_upload_asset(self):
        pass

    def test_up_to_date(self):
        '''
        Test that up_to_date() correctly recognises
        an SCons directory as up-to-date or out of date.
        '''
        pass

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
        print sizes
        self.assertTrue(bool(txt_path))
        self.assertTrue(bool(jpg_path))

        # Check that the size dictionary reports these files' correct sizes in bytes
        self.assertEqual(sizes[txt_path[0]], 93)
        self.assertEqual(sizes[jpg_path[0]], 149084)

  

if __name__ == '__main__':
    os.getcwd()
    unittest.main()
