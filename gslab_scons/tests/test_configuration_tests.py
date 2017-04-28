import unittest
import sys
import os
import re
import shutil
import mock
import datetime
import subprocess

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


    @mock.patch("gslab_scons.configuration_tests.pkg_resources.get_distribution")
    @mock.patch('gslab_scons.configuration_tests.importlib.import_module')
    @mock.patch('gslab_scons.configuration_tests.convert_packages_argument')
    def test_check_python_packages(self, mock_convert_packages, mock_import, mock_version):
        # Setup
        class MockVersionSideEffect(object):
            def __init__(self):
                self.version = '3.0.2'

        def version_side_effect(*args, **kwargs):
            return MockVersionSideEffect()

        mock_version.side_effect          = version_side_effect
        mock_convert_packages.side_effect = lambda x: ['yaml', 'os']
        mock_import.side_effect           = lambda x: None

        # Default correct test
        configuration_tests.check_python_packages('3.0.2', ['yaml', 'os'])
        mock_convert_packages.assert_called_with(['yaml', 'os'])
        mock_import.assert_called()
        mock_version.assert_called_with('gslab_tools')

        # Incorrect gslab_python version
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_python_packages('3.0.3', ['yaml', 'os'])
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_python_packages('3.0.13', ['yaml', 'os'])
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_python_packages('10.00.01', ['yaml', 'os'])
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_python_packages('3.2.2', ['yaml', 'os'])

        # Module doesn't exist
        def import_side_effect(*args, **kwargs):
            if args[0] == 'os':
                raise ImportError(args[0])

        with self.assertRaises(ex_classes.PrerequisiteError):
            mock_import.side_effect = import_side_effect
            configuration_tests.check_python_packages('3.0.2', ['yaml', 'os'])


    def test_convert_packages_argument(self):
        self.assertEqual(configuration_tests.convert_packages_argument(['test']), ['test'])
        self.assertEqual(configuration_tests.convert_packages_argument(['test', 'test1']), 
                                                                       ['test', 'test1'])
        self.assertEqual(configuration_tests.convert_packages_argument('test'), ['test'])
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.convert_packages_argument(123)
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.convert_packages_argument({'test'})
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.convert_packages_argument(['test', 2])
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.convert_packages_argument([2, 2])
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.convert_packages_argument(lambda x: 'test')


    @mock.patch('gslab_scons.configuration_tests.is_in_path')
    @mock.patch('gslab_scons.configuration_tests.check_r_packages')
    def test_check_r(self, mock_check_r_packages, mock_is_in_path):
        # No R executable
        mock_is_in_path.side_effect = lambda x: None
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_r()
        mock_check_r_packages.assert_not_called()

        # Test default arguments 
        mock_is_in_path.side_effect = lambda x: x == 'R'
        configuration_tests.check_r()
        mock_check_r_packages.assert_called_with(["yaml"])

        # Test alternative arguments
        packages = ["yaml", "ggplot"]
        configuration_tests.check_r(packages)
        mock_check_r_packages.assert_called_with(["yaml", "ggplot"])        

        # Test alternative arguments format
        packages = "yaml"
        configuration_tests.check_r(packages)
        mock_check_r_packages.assert_called_with("yaml")


    @mock.patch('gslab_scons.configuration_tests.subprocess.check_output')
    @mock.patch('gslab_scons.configuration_tests.convert_packages_argument')
    def test_check_r_packages(self, mock_convert_packages, mock_check_output):
        # Setup
        def output_side_effect(*args, **kwargs):
            cmd_line_call = args[0]
            if cmd_line_call in ['R -q -e "suppressMessages(library(%s))"' % a \
                                        for a in ['yaml', 'ggplot']]:
                return 0
            else:
                subprocess.check_call("exit 1", shell = True)

        mock_convert_packages.side_effect = lambda x: ['yaml', 'ggplot']
        mock_check_output.side_effect     = output_side_effect

        # Default correct test
        configuration_tests.check_r_packages(['yaml', 'ggplot'])
        mock_convert_packages.assert_called_with(['yaml', 'ggplot'])
        mock_check_output.assert_called()

        # Module doesn't exist
        mock_convert_packages.side_effect = lambda x: ['yaml', 'os']
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_r_packages(['yaml', 'os'])

        mock_convert_packages.side_effect = lambda x: ['sys', 'os']
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_r_packages(['sys', 'os'])


    @mock.patch('gslab_scons.configuration_tests.is_in_path')
    def test_check_lyx(self, mock_is_in_path):
        # No lyx executable
        mock_is_in_path.side_effect = lambda x: None
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_lyx()

        # Test default 
        mock_is_in_path.side_effect = lambda x: x == 'lyx'
        configuration_tests.check_lyx()


    @mock.patch('gslab_scons.configuration_tests.subprocess.check_output')
    def test_check_lfs(self, mock_check):
        mock_check.side_effect = self.make_side_effect(['install', 'init'])
        configuration_tests.check_lfs()

        mock_check.side_effect = self.make_side_effect(['init'])
        configuration_tests.check_lfs()

        mock_check.side_effect = self.make_side_effect(['install'])
        configuration_tests.check_lfs()

        with self.assertRaises(ex_classes.PrerequisiteError):
            mock_check.side_effect = self.make_side_effect(['checkout'])
            configuration_tests.check_lfs()

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


    @mock.patch('gslab_scons.configuration_tests.os.path.expanduser')
    @mock.patch('gslab_scons.configuration_tests.os.path.isdir')
    def test_check_and_expand_cache_path(self, mock_is_dir, mock_expanduser):
        mock_expanduser.side_effect = lambda x: re.sub('~', 'Users/lb', x)
        mock_is_dir.side_effect     = lambda x: x == 'Users/lb/cache'

        configuration_tests.check_and_expand_cache_path('~/cache')
        configuration_tests.check_and_expand_cache_path('Users/lb/cache')
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_and_expand_cache_path('~/~/cache')
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_and_expand_cache_path('lb/cache')
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_and_expand_cache_path(3)


    @mock.patch('gslab_scons.configuration_tests.check_stata_packages')
    @mock.patch('gslab_scons.configuration_tests.load_yaml_value')
    @mock.patch('gslab_scons.configuration_tests.get_stata_executable')
    @mock.patch('gslab_scons.configuration_tests.get_stata_command')
    def test_check_stata(self, mock_stata_command, mock_stata_exec, 
                         mock_load_yaml, mock_stata_packages):
        # Setup
        def stata_package_side_effect(*args, **kwargs):
            command  = args[0]
            packages = args[1]
            if command != 'statamp':
                raise ex_classes.PrerequisiteError()
            for package in packages:
                if package != 'yaml':
                    raise ex_classes.PrerequisiteError()

        mock_load_yaml.return_value      = 'statamp'
        f = lambda x: x['user_flavor'] if x['user_flavor'] is not None else 'statamp'
        mock_stata_exec.side_effect     = f
        mock_stata_command.side_effect  = lambda x: x
        mock_stata_packages.side_effect = stata_package_side_effect

        # Correct tests

        # Has yaml value
        self.assertEqual(configuration_tests.check_stata(), 'statamp')

        # No yaml value
        # Function only returns user-specified executable or none, not the defaults
        mock_load_yaml.return_value = None
        self.assertEqual(configuration_tests.check_stata(), None)

        # Failures

        # No yaml value and no default value in path
        mock_stata_exec.side_effect = lambda x: None
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_stata()

        # Bad package
        mock_stata_exec.side_effect = f
        with self.assertRaises(ex_classes.PrerequisiteError):
            configuration_tests.check_stata(packages = ['bad_package'])


    @mock.patch('gslab_scons.configuration_tests.raw_input')
    def test_load_yaml_value(self, mock_raw_input):
        # Setup
        def raw_input_side_effect(*args, **kwargs):
            message = args[0]
            if re.search("corrupted", message):
                return 'y'
            if re.search("Enter", message):
                return 'value'

        def raw_input_side_effect2(*args, **kwargs):
            message = args[0]
            if re.search("corrupted", message):
                return 'n'
            if re.search("Enter", message):
                return 'none'

        mock_raw_input.side_effect = raw_input_side_effect

        def make_yaml(string):
            if os.path.isfile('yaml.yaml'):
                os.remove('yaml.yaml')  
            with open('yaml.yaml', 'wb') as f:
                f.write('%s\n' % string)

        # Test Good

        # Yaml file exists, is not corrupt, and has key.
        make_yaml('key: value')
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'key'), 'value')

        # Yaml file exists, is not corrupt, and doesn't have key. User enters value for key.
        make_yaml('bad_key: bad_value')
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'key'), 'value')
        
        # But now yaml has a correct key and doesn't require user input.
        mock_raw_input.side_effect = lambda x: "bad_value"
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'key'), 'value')
        mock_raw_input.side_effect = raw_input_side_effect

        # Yaml file exists and is corrupt. User deletes and re-creates. 
        make_yaml('key value')
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'key'), 'value')

        # Yaml file does not exist. User enters value to create. 
        os.remove('yaml.yaml')
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'key'), 'value')

        # Yaml file does not exist. User enters none value to create. 
        os.remove('yaml.yaml')
        mock_raw_input.side_effect = raw_input_side_effect2
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'stata_executable'), None)

        # Yaml file now exists with none value.
        self.assertTrue(os.path.isfile('yaml.yaml'))
        self.assertEqual(configuration_tests.load_yaml_value('yaml.yaml', 'stata_executable'), None)

        # Test bad
        with self.assertRaises(ex_classes.PrerequisiteError):
            # Corrupt file and user doesn't choose to delete and re-create 
            make_yaml('key value')
            configuration_tests.load_yaml_value('yaml.yaml', 'key')

        if os.path.isfile('yaml.yaml'):
            os.remove('yaml.yaml')  


    @mock.patch('gslab_scons.configuration_tests.is_unix')
    @mock.patch('gslab_scons.configuration_tests.convert_packages_argument')
    @mock.patch('gslab_scons.configuration_tests.subprocess.check_output')
    def test_check_stata_packages(self, mock_check_output, mock_package_argument, 
                                  mock_is_unix):

        def check_output_side_effect(*args, **kwargs):
            command = args[0].split("which ")[0]
            if not re.search("statamp", command):
                raise subprocess.CalledProcessError(1, args[0])  

            with open('stata.log', 'wb') as f:
                if not re.search('yaml', args[0]):
                    package = args[0].split("which ")[1]
                    f.write("command %s not found" % package)

        mock_check_output.side_effect     = check_output_side_effect
        mock_package_argument.side_effect = lambda x: ['yaml']
        mock_is_unix.return_value = True  

        with mock.patch('gslab_scons.configuration_tests.sys.platform', 'win32'):
            # Good tests

            # Unix (is.unix is checked before sys.platform)
            configuration_tests.check_stata_packages("statamp", "yaml")

            # Windows
            mock_is_unix.return_value = False
            configuration_tests.check_stata_packages("statamp", "yaml")

            # No packages
            mock_check_output.reset_mock()
            mock_package_argument.side_effect = lambda x: []
            configuration_tests.check_stata_packages("statamp", [])
            mock_check_output.assert_not_called()

            # Bad Tests
            with self.assertRaises(ex_classes.PrerequisiteError):
                # Bad package
                mock_package_argument.side_effect = lambda x: ['bad_package']
                configuration_tests.check_stata_packages("statamp", "bad_package")
            
            with self.assertRaises(ex_classes.PrerequisiteError):
                # Bad executable
                mock_package_argument.side_effect = lambda x: ['yaml']
                configuration_tests.check_stata_packages("bad_executable", "yaml")

        # More bad tests
        with self.assertRaises(ex_classes.PrerequisiteError): 
            with mock.patch('gslab_scons.configuration_tests.sys.platform', 'Unknown'):
                # Unknown platform
                configuration_tests.check_stata_packages("statamp", "yaml")
        



if __name__ == '__main__':
    unittest.main()
