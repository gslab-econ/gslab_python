#! /usr/bin/env python

import unittest, sys, os, shutil, contextlib
sys.path.append('../..')
from dir_mod import delete_files
from get_externals import get_externals
from nostderrout import nostderrout
    

class testDeleteFiles(unittest.TestCase):

    def setUp(self):
        os.mkdir('./input/externals_delete_files/')    
        get_externals('./input/externals_delete_files.txt', './input/externals_delete_files/', '', quiet = True)
        
    def test_single_file(self):
        file_list = os.listdir('./input/externals_delete_files/')
        file_number = len(file_list)
        self.assertTrue(os.path.isfile('./input/externals_delete_files/tables_onlineappdix.txt'))
        with nostderrout():
            delete_files('./input/externals_delete_files/tables_onlineappdix.txt')
        file_list = os.listdir('./input/externals_delete_files/')
        self.assertEqual(len(file_list), file_number - 1)
        self.assertFalse(os.path.isfile('./input/externals_delete_files/tables_onlineappdix.txt'))
    
    def test_wildcards(self):
        file_list = os.listdir('./input/externals_delete_files/internal/')
        self.assertEqual(len(file_list), 4)
        with nostderrout():        
            delete_files('./input/externals_delete_files/internal/*')
        file_list = os.listdir('./input/externals_delete_files/internal/')
        self.assertEqual(len(file_list), 0)
    
    def test_directory_fails(self):
        with nostderrout():
            with self.assertRaises(OSError):
                delete_files('./input/externals_delete_files/internal/')
            
    def tearDown(self):
        if os.path.isdir('./input/externals_delete_files/'):
            shutil.rmtree('./input/externals_delete_files/')   
        if os.path.isfile('get_externals.log'):
            os.remove('get_externals.log')            

if __name__ == '__main__':
    os.getcwd()
    unittest.main()