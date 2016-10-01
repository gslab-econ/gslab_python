#! /usr/bin/env python

import unittest, sys, os, shutil, contextlib
sys.path.append('../..')
from build import *
from log import *
from gslab_make.get_externals import get_externals
from nostderrout import nostderrout

class testbuild_stata(unittest.TestCase):

    def setUp(self):
        get_externals('./input/externals_stata_ado.txt', '../external/', '', quiet = True)
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def test_default(self):
        env = {'user_flavor' : None}
        build_stata('../build/stata.dta', './input/stata_test_script.do', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')
        
    def test_user_executable(self):
        env = {'user_flavor':'statamp'}
        build_stata('../build/stata.dta', './input/stata_test_script.do', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')

   # def test_bad_user_executable(self):
   #     env = {'user_flavor':'bad_user_executable'}
   #     with nostderrout():
   #         build_stata('../build/stata.dta', './input/stata_test_script.do', env)
   #     logfile_data = open('../build/sconscript.log', 'rU').read()
   #     self.assertIn('Error: Cannot find Stata executable.', logfile_data)
   #     if os.path.isfile('../build/sconscript.log'):
   #         os.remove('../build/sconscript.log')

    #def test_bad_order(self):
    #    env = {'user_flavor':'bad_user_executable'}
    #    with nostderrout():
    #        build_stata('../build/stata.dta', ['bad', './input/stata_test_script.do'], env)
    #    logfile_data = open('../build/sconscript.log', 'rU').read()
    #    self.assertIn('Error: ' + 'First argument in', logfile_data)
    #    if os.path.isfile('../build/sconscript.log'):
    #        os.remove('../build/sconscript.log')
    
    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
                
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
