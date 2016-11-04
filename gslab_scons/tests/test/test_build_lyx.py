#! /usr/bin/env python

import unittest
import sys
import os
import shutil
sys.path.append('../../..')
from gslab_scons.build import *
from gslab_scons.log import *
from gslab_scons.exceptions import *

class testbuild_lyx(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def test_default(self):
        env = ''
        build_lyx('../build/lyx.pdf', './input/lyx_test_file.lyx', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')
    
    def test_bad_extension(self):
        env = ''
        with self.assertRaises(BadExtensionError):
            build_lyx('../build/lyx.pdf', ['bad', './input/lyx_test_file.lyx'], env)
   
    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')
                
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
