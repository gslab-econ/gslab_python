#! /usr/bin/env python

import unittest
import sys
import os
import shutil

# Ensure the script is run from its own directory 
os.chdir(os.path.dirname(os.path.realpath(__file__)))

sys.path.append('../../..')
from gslab_make import start_make_logging, end_make_logging, clear_dirs
from gslab_make.private import CritError
from gslab_make.tests import nostderrout


class testEndMakeLogging(unittest.TestCase):

    def setUp(self):
        makelog_file = '../output/make.log'
        output_dir = '../output/'
        with nostderrout():
            clear_dirs(output_dir)
            start_make_logging(makelog_file)

    def test_end(self):
        with nostderrout():
            end_make_logging('../output/make.log')
        logfile_data = open('../output/make.log', 'rU').readlines()
        self.assertTrue(logfile_data[-1].startswith(' make.py ended:'))

    def test_end_fail(self):
        os.remove('../output/make.log')
        with self.assertRaises(CritError):
            end_make_logging('../output/make.log')

    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
            
            
if __name__ == '__main__':
    os.getcwd()
    unittest.main()