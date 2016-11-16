#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_make import start_make_logging, clear_dirs, run_lyx
from gslab_make.tests import nostderrout
    

class testRunLyx(unittest.TestCase):

    def setUp(self):
        makelog_file = '../output/make.log'
        output_dir = '../output/'
        with nostderrout():
            clear_dirs(output_dir)
            start_make_logging(makelog_file)

    def test_default_log(self):
        with nostderrout():
            run_lyx(program = './input/lyx_test_file.lyx')
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))
        
    def test_custom_log(self):
        os.remove('../output/make.log')
        makelog_file = '../output/custom_make.log'
        output_dir = '../output/'      
        with nostderrout():        
            clear_dirs(output_dir)
            start_make_logging(makelog_file)
            run_lyx(program = './input/lyx_test_file.lyx', 
                    makelog = '../output/custom_make.log')
        logfile_data = open('../output/custom_make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))
        
    def test_independent_log(self):
        with nostderrout():
            run_lyx(program = './input/lyx_test_file.lyx', 
                    log     = '../output/lyx.log')
        makelog_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', makelog_data)
        self.assertTrue(os.path.isfile('../output/lyx.log'))
        lyxlog_data = open('../output/lyx.log', 'rU').read()
        self.assertIn('LaTeX', lyxlog_data)
        self.assertIn(lyxlog_data, makelog_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))    

    def test_no_extension(self):
        with nostderrout():
            run_lyx(program = './input/lyx_test_file')
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))
        
    def test_executable(self):
        with nostderrout():
            run_lyx(program    = './input/lyx_test_file.lyx', 
                    executable = 'lyx') 
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))
        
    def test_bad_executable(self):
        with nostderrout():
            run_lyx(program    = './input/lyx_test_file.lyx', 
                    executable = 'nonexistent_lyx_executable')
        logfile_data = open('../output/make.log', 'rU').read()
        if os.name == 'posix':
            self.assertIn('/bin/sh: nonexistent_lyx_executable: command not found', 
                          logfile_data)
        else:
            self.assertIn('\'nonexistent_lyx_executable\' is not recognized as an internal or external command', logfile_data)
    
    def test_no_program(self):
        with nostderrout():
            run_lyx(program = './input/nonexistent_lyx_file.lyx')
        logfile_data = open('../output/make.log', 'rU').readlines()
        self.assertTrue(logfile_data[-1].startswith('CritError:'))
    
    def test_option(self):
        with nostderrout():
            run_lyx(program = './input/lyx_test_file.lyx', option = '-e pdf')
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))
    
    def test_change_dir(self): 
        with nostderrout():    
            run_lyx(program = './input/lyx_test_file.lyx', changedir = True)
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../output/lyx_test_file.pdf'))
        
    def test_pdfout(self): 
        with nostderrout():    
            run_lyx(program = './input/lyx_test_file.lyx', 
                    pdfout = './input/custom_outfile.pdf')
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('./input/custom_outfile.pdf'))
        self.assertFalse(os.path.isfile('../output/lyx_test_file.pdf'))

    def test_comments(self):  
        temp_dir = '../temp/'
        with nostderrout():   
            clear_dirs(temp_dir)
            run_lyx(program = './input/lyx_test_file.lyx', 
                    comments = True)
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../temp/lyx_test_file_comments.pdf'))
        self.assertFalse(os.path.isfile('../output/lyx_test_file_comments.pdf'))
        
    def test_handout_with_comments(self):  
        temp_dir = '../temp/'
        with nostderrout():   
            clear_dirs(temp_dir)
            run_lyx(program = './input/lyx_beamer_test_file.lyx', 
                    handout = True, comments = True)
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../temp/lyx_beamer_test_file_handout.pdf'))
        self.assertFalse(os.path.isfile('../output/lyx_beamer_test_file_handout.pdf'))

    def test_handout_change_dir(self):
        temp_dir = '../temp/'
        with nostderrout():    
            clear_dirs(temp_dir)
            run_lyx(program = './input/lyx_test_file.lyx', 
                    handout = True, changedir = True)
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('../temp/lyx_test_file_handout.pdf'))

    def test_handout_pdfout(self):
        temp_dir = '../temp/'
        with nostderrout():    
            clear_dirs(temp_dir)
            run_lyx(program = './input/lyx_test_file.lyx', 
                    handout = True, pdfout = './input/custom_outfile.pdf')
        logfile_data = open('../output/make.log', 'rU').read()
        self.assertIn('LaTeX', logfile_data)
        self.assertTrue(os.path.isfile('./input/custom_outfile.pdf'))
        self.assertFalse(os.path.isfile('../temp/lyx_test_file_handout.pdf'))
        
    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
        if os.path.isdir('../temp/'):
            shutil.rmtree('../temp/')
        if os.path.isfile('./input/custom_outfile.pdf'):
            os.remove('./input/custom_outfile.pdf')
    
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()