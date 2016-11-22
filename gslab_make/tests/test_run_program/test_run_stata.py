#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
import gslab_make.private.metadata as metadata
from gslab_make import start_make_logging, clear_dirs, run_stata, get_externals
from gslab_make.tests import nostderrout

    
class testRunStata(unittest.TestCase):

    def setUp(self):
        makelog_file = '../output/make.log'
        output_dir = '../output/'
        external_dir = '../external/'
        with nostderrout():
            clear_dirs(output_dir, external_dir)
            start_make_logging(makelog_file)
            get_externals('./input/externals_stata_ado.txt', 
                          '../external/', '', quiet = True)

    def test_default_log(self):
        with nostderrout():
            run_stata(program = './input/stata_test_script.do')
        self.assertTrue(self.last_line_equals('../output/make.log', 
                                              'end of do-file\n'))
        
    def test_custom_log(self):
        os.remove('../output/make.log')
        makelog_file = '../output/custom_make.log'
        output_dir   = '../output/'
        external_dir = '../external/'

        with nostderrout():    
            clear_dirs(output_dir, external_dir)
            start_make_logging(makelog_file)
            get_externals('./input/externals_stata_ado.txt', 
                          '../external/', '', quiet = True)
            run_stata(program = './input/stata_test_script.do', 
                      makelog = '../output/custom_make.log')
        
        self.assertTrue(self.last_line_equals('../output/custom_make.log', 
                                              'end of do-file\n'))
        
    def test_independent_log(self):
        with nostderrout():
            run_stata(program = './input/stata_test_script.do', 
                      log     = '../output/stata.log')

        self.assertTrue(self.last_line_equals('../output/make.log', 
                                              'end of do-file\n'))

        self.assertTrue(os.path.isfile('../output/stata.log'))

        self.assertTrue(self.last_line_equals('../output/stata.log', 
                                              'end of do-file\n'))
        
    def test_no_extension(self):
        with nostderrout():
            run_stata(program = './input/stata_test_script')
        self.assertTrue(self.last_line_equals('../output/make.log', 
                                              'end of do-file\n'))
        
    def test_executable(self):
        with nostderrout():
            if os.name == 'posix':
                run_stata(program    = './input/stata_test_script.do', 
                          executable = metadata.default_executables['stataunix']) 
            else:
                run_stata(program    = './input/stata_test_script.do', 
                          executable = metadata.default_executables['statawin']) 

        self.assertTrue(self.last_line_equals('../output/make.log', 'end of do-file\n'))
        
    def test_bad_executable(self):
        with nostderrout():
            run_stata(program    = './input/stata_test_script.do', 
                      executable = 'nonexistent_stata_executable')

        logfile_data = open('../output/make.log', 'rU').read()
        if os.name == 'posix':
            self.assertIn('/bin/sh: nonexistent_stata_executable: command not found', 
                          logfile_data)
        else:
            self.assertIn('\'nonexistent_stata_executable\' is not recognized as an internal or external command', 
                          logfile_data)
    
    def test_no_program(self):
        with nostderrout():
            run_stata(program = './input/nonexistent_stata_script.do')
        logfile_data = open('../output/make.log', 'rU').readlines()
        self.assertTrue(logfile_data[-1].startswith('CritError:'))

    def test_change_dir(self):
        os.mkdir('output')
        os.mkdir('external')
        get_externals('./input/externals_stata_ado.txt', 
                      './external/', '', quiet = True)
        with nostderrout():
            run_stata(program   = './input/stata_test_script.do', 
                      changedir = True)

        self.assertTrue(self.last_line_equals('../output/make.log', 
                                              'end of do-file\n'))    
        self.assertTrue(os.path.isfile('./output/stata1.dta'))
        self.assertFalse(os.path.isfile('../output/stata1.dta'))
    
    def last_line_equals(self, filename, string):
        file_data = open(filename, 'rU')
        file_data.seek(-2, 2)
        file_data.read(2)
        string_len = len(string)

        if file_data.newlines == '\n' or file_data.newlines == '\r' :
            file_data.seek(-string_len, 2)
        elif file_data.newlines == '\r\n':
            file_data.seek(-string_len -1, 2)

        return string == file_data.read(string_len)
    
    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
        if os.path.isdir('../external/'):
            shutil.rmtree('../external/')
        if os.path.isdir('./output/'):
            shutil.rmtree('./output/')
        if os.path.isdir('./external/'):
            shutil.rmtree('./external/')             
        if os.path.isfile('get_externals.log'):
            os.remove('get_externals.log') 
      

if __name__ == '__main__':
    os.getcwd()
    unittest.main()
