#! /usr/bin/env python

import unittest
import sys
import os
import shutil
import mock
import re

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
                   env    = '')
        self.check_log('./build/sconscript.log')

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

    def check_log(self, log_path = './build/sconscript.log'):
        '''
        Check that log_path is a file that has a 
        log-creation timestamp.
        '''
        self.assertTrue(os.path.isfile(log_path))
        
        with open(log_path, 'rU') as log_file:
            log_data = log_file.read()
        self.assertIn('Log created:', log_data)

        os.remove(log_path)

    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_target_list(self, mock_system):
        mock_system.side_effect = self.os_system_side_effect
        # We don't expect that the targets actually need
        # to be created.
        targets = ['./build/r.rds', 'additional_target']
        gs.build_r(target = targets, 
                   source = './script.R', 
                   env    = '')
        # We expect build_r() to write its log to its 
        # first target's directory
        self.check_log('./build/sconscript.log')

    def test_bad_extension(self):
        '''Test that build_r() recognises an inappropriate file extension'''
        with self.assertRaises(BadExtensionError), nostderrout():
            gs.build_r(target = './build/r.rds', 
                       source = ['bad', './script.R'], 
                       env    = '')

    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_unintended_inputs(self, mock_system):
        # We don't expect the env argument to affect the function's
        # behaviour in any way or to raise errors
        mock_system.side_effect = self.os_system_side_effect

        gs.build_r('output.txt', 'script.R', True)
        self.check_log('./sconscript.log')

        gs.build_r('output.txt', 'script.R', (1, 2, 3))
        self.check_log('./sconscript.log')

        gs.build_r('output.txt', 'script.R', TypeError)
        self.check_log('./sconscript.log')

        env = None
        # We need a string or list of strings in the first argument...
        with self.assertRaises(TypeError), nostderrout():
            gs.build_r(None, 'script.R', env)
        with self.assertRaises(TypeError), nostderrout():
            gs.build_r(1, 'script.R', env)                     
        # ...but it can be an empty string.
        gs.build_r('', 'script.R', env)
        self.check_log('./sconscript.log')

        # Empty lists won't work.
        with self.assertRaises(IndexError), nostderrout():
            gs.build_r([], 'script.R', env)  

    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
