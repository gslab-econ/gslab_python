#! /usr/bin/env python

import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_scons  import build_stata, BadExecutableError, BadExtensionError
from gslab_make import get_externals

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

    def test_bad_user_executable(self):
        env = {'user_flavor':'bad_user_executable'}
        with self.assertRaises(BadExecutableError):
            build_stata('../build/stata.dta', './input/stata_test_script.do', env)

    def test_bad_extension(self):
        env = {'user_flavor':'bad_user_executable'}
        with self.assertRaises(BadExtensionError):
            build_stata('../build/stata.dta', ['bad', './input/stata_test_script.do'], env)

    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
        if os.path.exists('../external/'):
            shutil.rmtree('../external/')
        if os.path.exists('get_externals.log'):
            os.remove('get_externals.log')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
