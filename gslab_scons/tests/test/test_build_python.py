#! /usr/bin/env python

import unittest, sys, os, shutil, contextlib
sys.path.append('../..')
from build import *
from log import *
from gslab_make.get_externals import get_externals
from nostderrout import nostderrout

class testbuild_python(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def test_default(self):
        env = ''
        build_python('../build/py.py', './input/python_test_script.py', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')
    
    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
                
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
