#! /usr/bin/env python

import unittest
import sys
import os
import shutil
import pdb
import re

sys.path.append('../..')
from gslab_make import start_make_logging, clear_dirs, get_externals
from gslab_make.private import CritError, LogicError
from gslab_make.tests import nostderrout
    
    
class testGetExternals(unittest.TestCase):

    def setUp(self):
        makelog_file = './output/make.log'
        output_dir   = './output/'
        external_dir = './external/'
        with nostderrout():
            clear_dirs(output_dir, external_dir)  
            start_make_logging(makelog_file)

    def test_legal_input(self):
        '''Test that get_externals() correctly handles legal output'''
        with nostderrout():
            get_externals('./input/externals_legal.txt', './external/', 
                          './output/make.log', quiet = True)
        
        with open('./output/make.log', 'rU') as log:
            logfile_lines = log.readlines()
        
        self.assertIn('get_externals.py ended:', logfile_lines[-1])
        
        with open('./output/make.log', 'rU') as log:
            logfile_data = log.read()
        
        self.assertNotIn('Error', logfile_data)
        self.assertTrue(os.path.isdir('./external/'))
        
    def test_illegal_input(self):
        '''Test that get_externals() correctly handles illegal output'''
        externals = './input/externals_illegal.txt'
        
        print('\n== Expecting svn errors... ==\n')
        with nostderrout():
            get_externals(externals, './external/', 
                          './output/make.log', quiet = True)
        print('\n== Done expecting errors ==')

        with open(externals, 'rU') as externals_file:
            externals_data = externals_file.readlines()

        comments = self.find_comment_lines(externals_data)
        number_of_externals = len(externals_data) - comments       
        self.assertTrue(self.check_results('./output/make.log', number_of_externals))
    
    def check_results(self, logfile, num_errors):
        logfile_data = open(logfile, 'rU').readlines()
        errors = 0
        for line in logfile_data:
            if re.match('^([A-Z][a-z]+)+Error:', line):
                errors += 1
                if errors > num_errors:
                    return False                
        return errors == num_errors
        
    def find_comment_lines(self, lines):
        comments = 0
        for line in lines:
            if re.match('^#', line):
                comments += 1
            if re.match('^\\n', line):
                comments += 1
        return comments        
   
    def tearDown(self):
        if os.path.isdir('./output/'):
            shutil.rmtree('./output/')
        if os.path.isdir('./external/'):
            shutil.rmtree('./external/')            
        if os.path.isfile('get_externals.log'):
            os.remove('get_externals.log') 
    
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
    