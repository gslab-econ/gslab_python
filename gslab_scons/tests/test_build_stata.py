#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import subprocess
import re
# Import gslab_scons testing helper modules
import _test_helpers as helpers
import _side_effects as fx

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import BadExecutableError, BadExtensionError
from gslab_make  import get_externals
from gslab_make.tests import nostderrout

# Define path to the builder for use in patching
path = 'gslab_scons.builders.build_stata'


class TestBuildStata(unittest.TestCase):

    @helpers.platform_patch('darwin', path)
    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_unix(self, mock_check, mock_path):
        '''Test build_stata()'s standard behaviour on Unix machines'''
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        # Mock is_in_path() to finds just one flavor of Stata 
        mock_path.side_effect = lambda *args, **kwargs: args[0] == 'stata-mp'
        env = {'user_flavor' : None}

        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)


    @helpers.platform_patch('win32', path)
    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    @mock.patch('%s.misc.is_64_windows'      % path)
    def test_windows(self, mock_is_64, mock_check, mock_path):
        '''
        Test that build_stata() behaves correctly on a Windows machine
        when given appropriate inputs. 
        '''
        # i) Non-64-bit Windows without a STATAEXE environment variable
        mock_check.side_effect = fx.make_stata_side_effect('statamp.exe')
        mock_path.side_effect  = \
            lambda *args, **kwargs: args[0] == 'statamp.exe'
        mock_is_64.return_value = False

        env = {'user_flavor' : None}

        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

        # ii) 64-bit Windows without a STATAEXE environment variable
        mock_check.side_effect = fx.make_stata_side_effect('statamp-64.exe')
        mock_path.side_effect  = \
            lambda *args, **kwargs: args[0] == 'statamp-64.exe'
        mock_is_64.return_value = True

        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

        # ii) Windows with a STATAEXE environment variable
        mock_check.side_effect = fx.make_stata_side_effect(r'%STATAEXE%')
        mock_path.side_effect  = \
            lambda *args, **kwargs: args[0] == r'%STATAEXE%'

        with mock.patch('%s.os.environ' % path, 
                        {'STATAEXE': 'statamp.exe'}):
            helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

    @helpers.platform_patch('cygwin', path)
    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_other_platform(self, mock_check, mock_path):
        '''
        Test build_stata()'s standard behaviour on a non-Unix,
        non-win32 machine.
        '''
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        # Mock is_in_path() to finds just one flavor of Stata 
        mock_path.side_effect = lambda *args, **kwargs: args[0] == 'stata-mp'

        # build_stata() will fail to define a command irrespective of
        # whether a user_flavour is specified
        env = {'user_flavor' : 'stata-mp'}
        with self.assertRaises(NameError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

        env = {'user_flavor' : None}
        with self.assertRaises(NameError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)
    

    @helpers.platform_patch('darwin', path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_user_executable_unix(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        env = {'user_flavor': 'stata-mp'}
        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

    @helpers.platform_patch('win32', path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_user_executable_windows(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')

        env = {'user_flavor': 'stata-mp'}
        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

    @mock.patch('%s.subprocess.check_output' % path)
    def test_cl_arg(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        
        env = {'user_flavor' : None}
        helpers.test_cl_args(self, gs.build_stata, mock_check, 'do',
                             env = env)

    def test_bad_user_executable(self):
        env = {'user_flavor': 'bad_user_executable'}
        with self.assertRaises(BadExecutableError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_no_executable_in_path(self, mock_check, mock_path):
        '''
        Test build_stata()'s behaviour when there no valid Stata
        executables in the user's path variable
        '''
        # We mock the system to only find an executable called Rscript
        # in the path.
        mock_check.side_effect = fx.make_stata_side_effect('Rscript')
        # Mock is_in_path() to finds just one flavor of Stata 
        mock_path.side_effect = lambda *args, **kwargs: args[0] == 'Rscript'

        env = {'user_flavor': None}
        with helpers.platform_patch('darwin', path), self.assertRaises(NameError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

        with helpers.platform_patch('win32', path), self.assertRaises(NameError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

    @mock.patch('%s.subprocess.check_output' % path)
    def test_unavailable_executable(self, mock_check):
        '''
        Test build_stata()'s behaviour when a Stata flavour that 
        isn't recognised is specified. 
        '''
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')

        env = {'user_flavor' : 'stata-se'}
        with self.assertRaises(BadExecutableError):
            gs.build_stata(target = './build/stata.dta', 
                           source = './input/stata_test_script.do', 
                           env    = env)

    @mock.patch('%s.subprocess.check_output' % path)
    def test_bad_extension(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        env = {'user_flavor': 'stata-mp'}
        helpers.bad_extension(self, gs.build_stata, 
                              good = 'test.do', env = env)


if __name__ == '__main__':
    unittest.main()
