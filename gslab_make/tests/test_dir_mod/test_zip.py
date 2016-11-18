#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_make import get_externals, make_links
from gslab_make.dir_mod import zip_dir, unzip, unzip_externals, clear_dirs
from gslab_make.tests import nostderrout


class testZip(unittest.TestCase):

    def setUp(self):
        '''Set up a synthetic externals directory for testing zip functions'''
        with nostderrout():
            clear_dirs('./externals/data')   
        
        shutil.copy('./input/zip_test_file.zip', 
                    './externals/zip_test_file.zip')
        
        with open('./externals/data/unzip_test.txt', 'wb') as f:
            f.write('Temporary test file\n')
        
    def test_unzip(self):
        self.assertTrue(os.path.exists('./externals/zip_test_file.zip'))
        unzip_externals('./externals/')
        self.assertTrue(os.path.isfile('./externals/test_data.txt'))
    
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
