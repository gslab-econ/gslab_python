#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import re
# Import gslab_scons testing helper modules
import _test_helpers as helpers
import _side_effects as fx

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout

system_patch = mock.patch('gslab_scons.builders.build_r.os.system')


class TestBuildR(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @system_patch
    def test_standard(self, mock_system):
        '''Test build_r()'s behaviour when given standard inputs.'''
        mock_system.side_effect = fx.r_side_effect
        helpers.standard_test(self, gs.build_r, 'R', 
                              system_mock = mock_system)

    @system_patch
    def test_target_list(self, mock_system):
        mock_system.side_effect = fx.r_side_effect
        # We don't expect that the targets actually need
        # to be created.
        targets = ['./build/r.rds', 'additional_target']
        gs.build_r(target = targets, 
                   source = './script.R', 
                   env    = {})
        # We expect build_r() to write its log to its first target's directory
        helpers.check_log(self, './build/sconscript.log')

    @system_patch
    def test_no_target(self, mock_system):
        '''Check that build_r() can run without creating its targets'''
        mock_system.side_effect = fx.r_side_effect
        gs.build_r(target = '', source = './script.R', env    = {})
        helpers.check_log(self, './sconscript.log')

    @system_patch
    def test_cl_arg(self, mock_system):
        mock_system.side_effect = fx.r_side_effect
        helpers.test_cl_args(self, gs.build_r, mock_system, 'R')

    # Test that build_r() recognises an inappropriate file extension
    test_bad_extension = \
        lambda self: helpers.bad_extension(self, gs.build_r, good = 'test.r')
   
    @system_patch
    def test_unintended_inputs(self, mock_system):
        # We expect build_r() to raise an error if its env
        # argument does not support indexing by strings. 
        mock_system.side_effect = fx.r_side_effect

        check = lambda **kwargs: helpers.input_check(self, gs.build_r, 
                                                     'r', **kwargs)

        for bad_env in [True, (1, 2), TypeError]:
            check(env = bad_env, error = TypeError)
        
        for bad_target in (None, 1):
            check(target = bad_target, error = TypeError)
        check(target = [], error = IndexError)     

        check(target = '', error = None)

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
