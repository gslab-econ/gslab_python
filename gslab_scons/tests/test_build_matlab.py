#! /usr/bin/env matlab
import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_scons import build_matlab
from gslab_scons._exception_classes import BadExtensionError


class testbuild_matlab(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def test_default(self):
        env = {}
        build_matlab('../build/test.mat', './input/matlab_test_script.m', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Builder log created:', logfile_data)
        self.assertTrue(os.path.isfile('../build/test.mat'))
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')
     
    def test_clarg(self):
        env = {'CL_ARG' : 'COMMANDLINE'}
        build_matlab('../build/testCOMMANDLINE.mat', './input/matlab_test_script.m', env)
        self.assertTrue(os.path.isfile('../build/testCOMMANDLINE.mat'))
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')

    def test_bad_extension(self):
        env = {}
        with self.assertRaises(BadExtensionError):
            build_matlab('../build/test.mat', 
                         ['bad', './input/matlab_test_script.m'], 
                         env)
   
    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
