#! /usr/bin/env python

import unittest, sys, os, shutil, contextlib
sys.path.append('../../..')
from gslab_scons.build import *
from gslab_scons.log import *
from gslab_scons.exceptions import *
from gslab_make.get_externals import get_externals
from nostderrout import nostderrout

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
    
    def test_bad_order(self):
        env = ''
        with self.assertRaises(BadSourceOrderError):
            build_lyx('../build/lyx.pdf', ['bad', './input/lyx_test_file.lyx'], env)
   
    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
                
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
