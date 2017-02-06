#! /usr/bin/env python

import unittest
import sys
import os
import shutil
import mock
import re
import _test_helpers as helpers

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout


class TestBuildR(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_standard(self, mock_system):
        '''
        Test that build_r() behaves as expected when used 
        in a standard way.
        '''
        mock_system.side_effect = self.os_system_side_effect
        gs.build_r(target = './build/r.rds', 
                   source = './input/script.R', 
                   env    = {})
        helpers.check_log(self, './build/sconscript.log')

    @staticmethod
    def os_system_side_effect(*args, **kwargs):
        '''
        This side effect mocks the behaviour of a system call
        on a machine with R set up for command-line use.
        '''
        # Get and parse the command passed to os.system()
        command = args[0]
        match = re.match('\s*'
                            '(?P<executable>R CMD BATCH)'
                            '\s+'
                            '(?P<option>--no-save)?'
                            '\s*'
                            '(?P<source>[\.\/\w]+(\.\w+)?)?'
                            '\s*'
                            '(?P<log>[\.\/\w]+(\.\w+)?)?',
                         command)

        executable = match.group('executable')
        log        = match.group('log')

        # As long as the executable is correct and a log path 
        # is specified, write a log.
        if executable == "R CMD BATCH" and log:
            with open(log.strip(), 'wb') as log_file:
                log_file.write('Test log\n')


    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_target_list(self, mock_system):
        mock_system.side_effect = self.os_system_side_effect
        # We don't expect that the targets actually need
        # to be created.
        targets = ['./build/r.rds', 'additional_target']
        gs.build_r(target = targets, 
                   source = './script.R', 
                   env    = {})
        # We expect build_r() to write its log to its first target's directory
        helpers.check_log(self, './build/sconscript.log')

    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_clarg(self):
        env = {'CL_ARG' : 'COMMANDLINE'}
        gs.build_r('./build/r.rds', './input/R_test_script.R', env)

        helpers.check_log(self, './build/sconscript.log',
                          expected_text = 'COMMANDLINE')

    # Test that build_r() recognises an inappropriate file extension
    test_bad_extension = \
        lambda self: helpers.bad_extension(self, gs.build_r, good = 'test.r')
   
    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_unintended_inputs(self, mock_system):
        # We expect build_r() to raise an error if its env
        # argument does not support indexing by strings. 
        mock_system.side_effect = self.os_system_side_effect

        for env in [True, (1, 2), TypeError]:
            with self.assertRaises(TypeError), nostderrout():
                gs.build_r('output.txt', 'script.R', env)
        
        env = {}
        # We need a string or list of strings in the first argument...
        for source in (None, 1):
            with self.assertRaises(TypeError), nostderrout():
                gs.build_r(1, 'script.R', env)                     
        
        # ...but it can be an empty string.
        gs.build_r('', 'script.R', env)
        helpers.check_log(self, './sconscript.log')

        # Empty lists won't work.
        with self.assertRaises(IndexError), nostderrout():
            gs.build_r([], 'script.R', env)  

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
