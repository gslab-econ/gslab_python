import unittest
import sys
import os
import re
import shutil
import mock
import datetime

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons.configuration_tests as configuration_tests
import gslab_scons._exception_classes as ex_classes
from gslab_make.tests import nostderrout


class TestConfigurationTests(unittest.TestCase):

    @mock.patch('gslab_scons.configuration_tests.check_python_packages')
    def test_check_python(self, mock_check_python_packages):
        # Incorrect python
        with mock.patch('gslab_scons.configuration_tests.sys.version_info', [3]):
            with self.assertRaises(ex_classes.PrerequisiteError):
                configuration_tests.check_python('3.0.2')
            mock_check_python_packages.assert_not_called()


        with mock.patch('gslab_scons.configuration_tests.sys.version_info', [2]):
            # Test default arguments and correct python
            mock_sys_version = [2]
            configuration_tests.check_python('3.0.2')
            mock_check_python_packages.assert_called_with('3.0.2', ["yaml", "gslab_scons", 
                                                           "gslab_make", "gslab_fill"])

            # Test alternative arguments and correct python
            packages = ["yaml"]
            configuration_tests.check_python(3.0, packages)
            mock_check_python_packages.assert_called_with(3.0, ["yaml"])        

            # Test alternative arguments format and correct python
            packages = "yaml"
            configuration_tests.check_python('3.0.2', packages)
            mock_check_python_packages.assert_called_with('3.0.2', "yaml") 




    # Tests for check_lfs #
    @mock.patch('gslab_scons.configuration_tests.subprocess.check_output')
    def test_check_lfs_success(self, mock_check):
        '''
        Test that check_lfs() works when either of the commands
        `git-lfs install` or `git-lfs init` runs without error.
         '''
        try:
            mock_check.side_effect = self.make_side_effect(['install', 'init'])
            configuration_tests.check_lfs()
        except:
            self.fail('check_lfs() raised an error when '
                     '`git-lfs install` and `git-lfs init` were '
                      'both valid commands.')
        try:
            mock_check.side_effect = self.make_side_effect(['init'])
            configuration_tests.check_lfs()
        except:
            self.fail('check_lfs() raised an error when '
                      '`git-lfs init` was a valid command.')

        try:
            mock_check.side_effect = self.make_side_effect(['install'])
            configuration_tests.check_lfs()
        except:
            self.fail('check_lfs() raised an error when '
                      '`git-lfs install` was a valid command.')

    @staticmethod
    def make_side_effect(available_options):
        '''
        This function returns a side effect that does nothing if 
        the command specified by its first positional argument
        is i) not a git-lfs command or ii) a git-lfs command 
        followed by one of the commands specified in the 
        available_options argument. 
        '''
        def side_effect(*args, **kwargs):
            command = args[0]
            if re.search('^git-lfs', command.strip(), flags = re.I):
                option = re.sub('git-lfs', '', command).strip()
                if option not in available_options:
                    raise subprocess.CalledProcessError(1, command)  
                else:
                    pass  
            else:
                pass
        return side_effect

    @mock.patch('gslab_scons.configuration_tests.subprocess.check_output')
    def test_check_lfs_failure(self, mock_check):
        '''
        Test that check_lfs() fails when neither `git-lfs install` nor
        `git-lfs init` are acceptable commands. 
        '''
        with self.assertRaises(ex_classes.PrerequisiteError):
            mock_check.side_effect = self.make_side_effect(['checkout'])
            configuration_tests.check_lfs()


if __name__ == '__main__':
    unittest.main()
