#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import subprocess
import re

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
    def test_default(self, mock_check, mock_path):
        '''
        Test that build_stata() behaves correctly when given
        appropriate inputs. 
        '''
        mock_check.side_effect = self.check_output_side_effect
        # Mock is_in_path() so that it finds just one flavor
        # of Stata deterministically across machines
        mock_path.side_effect = self.is_in_path_side_effect
        env = {'user_flavor' : None}

        gs.build_stata('./test_output.dta', './test_script.do', env)

        logfile_data = open('./sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)
        if os.path.isfile('./sconscript.log'):
            os.remove('./sconscript.log')        
      
    @staticmethod
    def is_in_path_side_effect(*args, **kwargs):
        flavor = args[0]
        if flavor == 'stata-mp':
            return True
        else:
            return False

    @staticmethod
    def check_output_side_effect(*args, **kwargs):
        command = args[0]

        if re.search('stata-mp -e', command):
            # Find the Stata script's name
            script_name = re.sub('stata-mp -e', '', command).strip()
            stata_log   = os.path.basename(script_name).replace('.do','.log')
            # Write a log
            with open(stata_log, 'wb') as logfile:
                logfile.write('Test Stata log.\n')

        elif not re.search('stata-mp', command):
            # Raise an error if the exectuable is not the only recognised one.
            raise subprocess.CalledProcessError(1, command)

    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_user_executable(self, mock_check):
        mock_check.side_effect = self.check_output_side_effect

        env = {'user_flavor': 'stata-mp'}
        gs.build_stata('./build/stata.dta', './input/stata_test_script.do', env)

        logfile_data = open('./build/sconscript.log', 'rU').read()
        self.assertIn('Log created:', logfile_data)

        if os.path.isfile('./build/sconscript.log'):
            os.remove('./build/sconscript.log')

    def test_clarg(self):
        env = {'user_flavor' : None, 'CL_ARG' : 'COMMANDLINE'}
        gs.build_stata('./build/stata.dta', './input/stata_test_script.do', env)
        logfile_data = open('./build/sconscript.log', 'rU').read()
        self.assertIn('COMMANDLINE', logfile_data)
        if os.path.isfile('./build/sconscript.log'):
            os.remove('./build/sconscript.log')

    def test_bad_user_executable(self):
        env = {'user_flavor': 'bad_user_executable'}
        with self.assertRaises(BadExecutableError):
            gs.build_stata('./build/stata.dta', './input/stata_test_script.do', env)

    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_unavailable_executable(self, mock_check):
        '''
        Test build_stata()'s behaviour when a Stata flavour that 
        isn't recognised is specified. 
        '''
        mock_check.side_effect = self.check_output_side_effect

        env = {'user_flavor' : 'stata-se'}
        with self.assertRaises(BadExecutableError):
            gs.build_stata('./build/stata.dta', './input/stata_test_script.do', env)

    @mock.patch('gslab_scons.builders.build_stata.subprocess.check_output')
    def test_bad_extension(self, mock_check):
        mock_check.side_effect = self.check_output_side_effect
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
