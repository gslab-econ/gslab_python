#! /usr/bin/env python

import unittest, os, sys
sys.path.append('..')
from py.externals_search import *

class TestArguments(unittest.TestCase):
   
    def test_correct_output(self):
        externals_search(
            search_terms = ["ANES", "lib"], 
            rev_num      = "20000",
            results_name = "ANES_lib_20000_results",
            search_path  = "http://gslab.chicagobooth.edu/svn/trunk/analysis/Media Productivity/")
        
        correct_results = ['term\tfile\n', 'lib\tcode/externals.txt\n']
        actual_results = open("..\output\ANES_lib_20000_results.txt", 'r').readlines()
        self.assertEqual(correct_results, actual_results)
        
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
    