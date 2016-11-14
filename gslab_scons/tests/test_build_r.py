#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_scons.build        import build_r
from gslab_scons.exceptions   import BadExtensionError
from gslab_make.get_externals import get_externals

class testbuild_r(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def test_default(self):
        env = ''
        build_r('../build/r.rds', './input/R_test_script.R', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')

    def test_bad_extension(self):
        '''Test that build_r() recognises an inappropriate file extension'''
        env = ''
        with self.assertRaises(BadExtensionError):
            build_r('../build/r.rds', ['bad', './input/R_test_script.R'], env)

    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')

if __name__ == '__main__':
    os.getcwd()
    unittest.main()
