#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_make import get_externals, start_make_logging, list_directory, clear_dirs
from gslab_make.private import CritError
from gslab_make.tests import nostderrout
    

class testListDirectory(unittest.TestCase):

    def setUp(self):
        os.mkdir('./input/externals_list_directory/')  
        get_externals('./input/externals_list_directory.txt', 
                      './input/externals_list_directory/', '', quiet = True)
        
    def test_default_log(self):
        makelog_file = '../output/make.log'
        output_dir = '../output/'
        with nostderrout():
            clear_dirs(output_dir)
            start_make_logging(makelog_file)
            list_directory('./input/externals_list_directory/')
        self.check_log('./input/externals_list_directory/', makelog_file)
        self.check_log('./input/externals_list_directory/internal/', makelog_file)
    
    def test_custom_log(self):
        makelog_file = './output/custom_make.log'
        output_dir   = './output/'
        with nostderrout():
            clear_dirs(output_dir)
            start_make_logging(makelog_file)
            list_directory('./input/externals_list_directory/', 
                           './output/custom_make.log')
        self.check_log('./input/externals_list_directory/', makelog_file)
        self.check_log('./input/externals_list_directory/internal/', makelog_file)
        
    def check_log(self, directory, log_file):
        file_list = os.listdir(directory)
        if 'internal' in file_list:
            file_list.remove('internal')
        log_data = open(log_file, 'rU').readlines()
        log_words = []
        for line in log_data:
            log_words = log_words + line.split(' ')
        for file in file_list:
            self.assertIn(file, log_words)  

    def test_no_makelog(self):
        with nostderrout():    
            with self.assertRaises(CritError):
                list_directory('./input/externals_list_directory/')
    
    def tearDown(self):
        if os.path.isdir('./output/'):
            shutil.rmtree('./output/')
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')           
        if os.path.isdir('./input/externals_list_directory/'):
            shutil.rmtree('./input/externals_list_directory/') 
        if os.path.isfile('get_externals.log'):
            os.remove('get_externals.log')            
    
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
