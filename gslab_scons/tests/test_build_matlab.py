import unittest
import sys
import os
import shutil
import mock
import re
import _test_helpers as helpers

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

        helpers.check_log(self, './build/sconscript.log')
        self.check_call(mock_system, ['-nosplash', '-nodesktop'])
    
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

    def check_call(self, mock_system, options):
        '''
        Check that build_matlab() made a Matlab system command
        with the correct options. 

        mock_system should be the mock of os.system used
        when calling build_matlab().
        '''
        mock_system.assert_called_once()
        command = mock_system.call_args[0][0]

        for option in options:
            self.assertIn(option,  command.split(' '))

        self.assertTrue(re.search('^matlab', command))        

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

        helpers.check_log(self, './build/sconscript.log')
        self.check_call(mock_system, ['-nosplash', '-minimize', '-wait'])

    @mock.patch('gslab_scons.builders.build_matlab.misc.sys.platform', 'riscos')
    @mock.patch('gslab_scons.builders.build_matlab.sys.platform', 'riscos')
    @mock.patch('gslab_scons.builders.build_matlab.os.system')
    def test_other_os(self, mock_system):
        '''
        Test that build_matlab() raises an exception when run on a
        non-Unix, non-Windows operating system.
        '''
        mock_system.side_effect = self.system_side_effect
        with self.assertRaises(Exception):
            gs.build_matlab(target = './build/test.mat', 
                            source = './input/matlab_test_script.m', 
                            env    = {})

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

        helpers.check_log(self, './build/sconscript.log')
        mock_system.assert_called_once()
        self.assertEqual(os.environ['CL_ARG'], env['CL_ARG'])

    test_bad_extension_alt = \
        lambda self: helpers.bad_extension(self, gs.build_matlab, good = 'test.m')
   
    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')


if __name__ == '__main__':
    unittest.main()
