#! /usr/bin/env python

import unittest
import sys
import os
import shutil
import mock

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout


class testbuild_r(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def test_default(self):
        env = ''
        gs.build_r('../build/r.rds', './input/R_test_script.R', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')

    def test_target_list(self):
        env = ''
        # We don't expect that the targets actually need
        # to be created.
        targets = ['../build/r.rds', 'additional_target']
        gs.build_r(targets, './input/R_test_script.R', env)
        logfile_data = open('../build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        # build_r() uses the first target to determine
        # where it writes its log.
        if os.path.isfile('../build/sconscript.log'):
            os.remove('../build/sconscript.log')

    def test_bad_extension(self):
        '''Test that build_r() recognises an inappropriate file extension'''
        env = ''
        with self.assertRaises(BadExtensionError), nostderrout():
            gs.build_r('../build/r.rds', ['bad', './input/R_test_script.R'], env)

    @mock.patch('gslab_scons.builders.build_r.log_timestamp')
    @mock.patch('gslab_scons.builders.build_r.os.system')
    def test_unintended_inputs(self, mock_system, mock_timestamp):
        # We don't expect the env argument to affect the function's
        # behaviour in any way or to raise errors
        gs.build_r('output.txt', 'script.R', True)
        self.check_call(mock_system, mock_timestamp, 1)

        gs.build_r('output.txt', 'script.R', (1, 2, 3))
        self.check_call(mock_system, mock_timestamp, 2)

        gs.build_r('output.txt', 'script.R', TypeError)
        self.check_call(mock_system, mock_timestamp, 3)

        env = ''
        # We need a string or list of strings in the first argument...
        with self.assertRaises(TypeError), nostderrout():
            gs.build_r(None, 'script.R', env)
        with self.assertRaises(TypeError), nostderrout():
            gs.build_r(1, 'script.R', env)                     

        # ...but it can be an empty string ;).
        gs.build_r('', 'script.R', env)

        # Empty lists won't work.
        with self.assertRaises(IndexError), nostderrout():
            gs.build_r([], 'script.R', env)  

    def check_call(self, mock_system, mock_timestamp, count):
        expected_command = 'R CMD BATCH --no-save script.R /sconscript.log'
        mock_system.assert_called_with(expected_command)
        self.assertEqual(mock_system.call_count, count)
        self.assertEqual(mock_timestamp.call_args[0][2], '/sconscript.log')

    def tearDown(self):
        if os.path.exists('../build/'):
            shutil.rmtree('../build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
