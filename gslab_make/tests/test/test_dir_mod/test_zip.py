#! /usr/bin/env python

import unittest
import sys
import os
import shutil
import contextlib

sys.path.append('../..')
from dir_mod import zip_dir, unzip, unzip_externals, clear_dirs
from get_externals import get_externals
from make_links import make_links
from nostderrout import nostderrout


class testZip(unittest.TestCase):

    def setUp(self):
        clear_dirs('./externals/')
        get_externals('./input/externals_zip.txt', 
                        external_dir = './externals/', 
                        makelog = '', 
                        quiet = True)
        
    def test_unzip(self):
        self.assertTrue(os.path.exists('./externals/data/'))
        unzip_externals('./externals/')
        self.assertTrue(os.path.isfile('./externals/data/purchases_2007.dta'))
    
    def test_zip(self):
        self.assertTrue(os.path.exists('./externals/data/'))
        with nostderrout():
            zip_dir('./externals/data/', './externals/purchases')
        self.assertTrue(os.path.isfile('./externals/purchases.zip'))
        
    def tearDown(self):
        if os.path.isdir('./externals/'):
            shutil.rmtree('./externals/')
        if os.path.isfile('./get_externals.log'):
            os.remove('./get_externals.log')

if __name__ == '__main__':
    os.getcwd()
    unittest.main()
