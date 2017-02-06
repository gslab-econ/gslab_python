import unittest
import sys
import os
import shutil
import mock
import re

sys.path.append('../..')
import gslab_scons as gs
from gslab_scons._exception_classes import BadExtensionError


class TestBuildMatlab(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @mock.patch('gslab_scons.builders.build_matlab.misc.sys.platform', 'darwin')
    @mock.patch('gslab_scons.builders.build_matlab.os.system')
    def test_unix(self, mock_system):
        '''
        Test that build_matlab() creates a log and properly submits
        a matlab system command on a Unix machine.
        '''
        mock_system.side_effect = self.system_side_effect

        gs.build_matlab(target = './build/test.mat', 
                        source = './input/matlab_test_script.m', 
                        env    = {})

        self.check_log('./build/sconscript.log')

        mock_system.assert_called_once()
        command = mock_system.call_args[0][0]
        self.assertIn('-nosplash',  command.split(' '))
        self.assertIn('-nodesktop', command.split(' '))
        self.assertTrue(re.search('^matlab', command))
    
    @staticmethod
    def system_side_effect(*args, **kwargs):
        try:
            command = kwargs['command']
        except KeyError:
            command = args[0]

        log_match = re.search('> (?P<log>[-\.\w\/]+)', command)

        if log_match:
            log_path = log_match.group('log')
            with open(log_path, 'wb') as log_file:
                log_file.write('Test log')

        return None

    def check_log(self, log_path = './build/sconscript.log'):
        with open(log_path, 'rU') as log_file:
            log_data = log_file.read()

        self.assertIn('Log created:', log_data)
        os.remove(log_path)

    @mock.patch('gslab_scons.builders.build_matlab.misc.sys.platform', 'win32')
    @mock.patch('gslab_scons.builders.build_matlab.sys.platform', 'win32')
    @mock.patch('gslab_scons.builders.build_matlab.os.system')
    def test_windows(self, mock_system):
        '''
        Test that build_matlab() creates a log and properly submits
        a matlab system command on a Windows machine.
        '''
        mock_system.side_effect = self.system_side_effect

        gs.build_matlab(target = './build/test.mat', 
                        source = './input/matlab_test_script.m', 
                        env    = {})

        self.check_log('./build/sconscript.log')

        mock_system.assert_called_once()
        command = mock_system.call_args[0][0]
        self.assertIn('-nosplash', command.split(' '))
        self.assertIn('-minimize', command.split(' '))
        self.assertIn('-wait',     command.split(' '))

        self.assertTrue(re.search('^matlab', command))

    @mock.patch('gslab_scons.builders.build_matlab.os.system')
    def test_clarg(self, mock_system):
        '''
        Test that build_matlab() properly sets command-line arguments
        in its env argument as system environment variables.
        '''
        mock_system.side_effect = self.system_side_effect

        env = {'CL_ARG': 'COMMANDLINE'}
        gs.build_matlab(target = './build/testCOMMANDLINE.mat', 
                        source = './input/matlab_test_script.m', 
                        env    = env)

        self.check_log('./build/sconscript.log')
        mock_system.assert_called_once()
        self.assertEqual(os.environ['CL_ARG'], env['CL_ARG'])

    def test_bad_extension(self):
        '''
        Test that build_matlab() raises the correct error when
        its first source does not have a valid file extension.  
        '''
        with self.assertRaises(BadExtensionError):
            gs.build_matlab(target = './build/test.mat', 
                            source = ['bad', './input/matlab_test_script.m'], 
                            env    = {})
   
    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')


if __name__ == '__main__':
    unittest.main()
