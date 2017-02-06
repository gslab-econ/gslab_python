#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import subprocess
import re
import _test_helpers as helpers

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import BadExecutableError, BadExtensionError
from gslab_make  import get_externals
from gslab_make.tests import nostderrout


class TestBuildStata(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @mock.patch('gslab_scons.builders.build_stata.misc.sys.platform', 'darwin')
    @mock.patch('gslab_scons.builders.build_stata.misc.is_in_path')
    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_unix(self, mock_check, mock_path):
        '''
        Test that build_stata() behaves correctly on a Unix machine
        when given appropriate inputs. 
        '''
        mock_check.side_effect = self.make_check_side_effect('stata-mp')
        # Mock is_in_path() so that it finds just one flavor
        # of Stata deterministically across machines
        mock_path.side_effect = lambda *args, **kwargs: args[0] == 'stata-mp'
        env = {'user_flavor' : None}

        gs.build_stata('./test_output.dta', './test_script.do', env)
        helpers.check_log(self, './sconscript.log')

    @staticmethod
    def make_check_side_effect(recognised_command):
        '''
        Make a side effect mocking the behaviour of 
        subprocess.check_output() when `recognised_command` is
        the only recognised system command. 
        '''
        def check_side_effect(*args, **kwargs):
            command = args[0]
    
            if re.search('%s [-\/]e' % recognised_command, command):
                # Find the Stata script's name
                script_name = re.sub('%s [-\/]e' % recognised_command, 
                                     '', 
                                     command).strip()
                stata_log   = os.path.basename(script_name).replace('.do','.log')
                # Write a log
                with open(stata_log, 'wb') as logfile:
                    logfile.write('Test Stata log.\n')
    
            elif not re.search(recognised_command, command):
                # Raise an error if the exectuable is not the only recognised one.
                raise subprocess.CalledProcessError(1, command)

        return check_side_effect

    @mock.patch('gslab_scons.builders.build_stata.misc.sys.platform', 'win32')
    @mock.patch('gslab_scons.builders.build_stata.sys.platform', 'win32')
    @mock.patch('gslab_scons.builders.build_stata.misc.is_in_path')
    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    @mock.patch('gslab_scons.builders.build_stata.misc.is_64_windows')
    def test_windows(self, mock_is_64, mock_check, mock_path):
        '''
        Test that build_stata() behaves correctly on a Windows machine
        when given appropriate inputs. 
        '''
        # i) Non-64-bit Windows without a STATAEXE environment variable
        mock_check.side_effect = self.make_check_side_effect('statamp.exe')
        mock_path.side_effect  = \
            lambda *args, **kwargs: args[0] == 'statamp.exe'
        mock_is_64.return_value = False

        env = {'user_flavor' : None}

        gs.build_stata(target = './test_output.dta', 
                       source = './test_script.do', 
                       env    = env)
        helpers.check_log(self, './sconscript.log') 

        # ii) 64-bit Windows without a STATAEXE environment variable
        mock_check.side_effect = self.make_check_side_effect('statamp-64.exe')
        mock_path.side_effect  = \
            lambda *args, **kwargs: args[0] == 'statamp-64.exe'
        mock_is_64.return_value = True

        gs.build_stata(target = './test_output.dta', 
                       source = './test_script.do', 
                       env    = env)
        helpers.check_log(self, './sconscript.log')


        # ii) Windows with a STATAEXE environment variable
        mock_check.side_effect = self.make_check_side_effect(r'%STATAEXE%')
        mock_path.side_effect  = \
            lambda *args, **kwargs: args[0] == r'%STATAEXE%'

        build_stata_environ = 'gslab_scons.builders.build_stata.os.environ'
        with mock.patch(build_stata_environ, {'STATAEXE': 'statamp.exe'}):
            gs.build_stata(target = './test_output.dta', 
                           source = './test_script.do', 
                           env    = env)
        helpers.check_log(self, './sconscript.log')


    @mock.patch('gslab_scons.builders.build_stata.misc.sys.platform', 'darwin')
    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_user_executable_unix(self, mock_check):
        mock_check.side_effect = self.make_check_side_effect('stata-mp')

        env = {'user_flavor': 'stata-mp'}
        gs.build_stata(target = './build/stata.dta', 
                       source = './input/stata_test_script.do', 
                       env    = env)

        logfile_data = open('./build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)

        if os.path.isfile('./build/sconscript.log'):
            os.remove('./build/sconscript.log')

    @mock.patch('gslab_scons.builders.build_stata.misc.sys.platform', 'win32')
    @mock.patch('gslab_scons.builders.build_stata.sys.platform', 'win32')
    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_user_executable_windows(self, mock_check):
        mock_check.side_effect = self.make_check_side_effect('stata-mp')

        env = {'user_flavor': 'stata-mp'}
        gs.build_stata(target = './build/stata.dta', 
                       source = './input/stata_test_script.do', 
                       env    = env)

        helpers.check_log(self, './build/sconscript.log')

    def test_clarg(self):
        env = {'user_flavor' : None, 'CL_ARG' : 'COMMANDLINE'}
        gs.build_stata(target = './build/stata.dta', 
                       source = './input/stata_test_script.do',
                       env    = env)
        logfile_data = open('./build/sconscript.log', 'rU').read()
        self.assertIn('COMMANDLINE', logfile_data)
        if os.path.isfile('./build/sconscript.log'):
            os.remove('./build/sconscript.log')

    def test_bad_user_executable(self):
        env = {'user_flavor': 'bad_user_executable'}
        with self.assertRaises(BadExecutableError):
            gs.build_stata(target = './build/stata.dta', 
                           source = './input/stata_test_script.do', 
                           env    = env)

    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_unavailable_executable(self, mock_check):
        '''
        Test build_stata()'s behaviour when a Stata flavour that 
        isn't recognised is specified. 
        '''
        mock_check.side_effect = self.make_check_side_effect('stata-mp')

        env = {'user_flavor' : 'stata-se'}
        with self.assertRaises(BadExecutableError):
            gs.build_stata(target = './build/stata.dta', 
                           source = './input/stata_test_script.do', 
                           env    = env)

    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_bad_extension(self, mock_check):
        mock_check.side_effect = self.make_check_side_effect('stata-mp')
        env = {'user_flavor': 'stata-mp'}
        with self.assertRaises(BadExtensionError), nostderrout():
            gs.build_stata('./build/stata.dta', 
                          ['bad', './input/stata_test_script.do'], env)

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
