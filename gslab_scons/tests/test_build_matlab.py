import unittest
import sys
import os
import shutil
import mock
import re
# Import gslab_scons testing helper modules
import _test_helpers as helpers
import _side_effects as fx

sys.path.append('../..')
import gslab_scons as gs
from gslab_scons._exception_classes import BadExtensionError

# Define main test patch
path  = 'gslab_scons.builders.build_matlab'
system_patch = mock.patch('%s.os.system'   % path)
copy_patch   = mock.patch('%s.shutil.copy' % path)
main_patch   = lambda f: system_patch(copy_patch(f))


class TestBuildMatlab(unittest.TestCase):

    @helpers.platform_patch('darwin', path)
    @main_patch
    def test_unix(self, mock_copy, mock_system):
        '''
        Test that build_matlab() creates a log and properly submits
        a matlab system command on a Unix machine.
        '''
        # Mock copy so that it just creates the destination file
        mock_copy.side_effect   = fx.matlab_copy_effect
        mock_system.side_effect = fx.matlab_side_effect

        helpers.standard_test(self, gs.build_matlab, 'm')
        self.check_call(mock_system, ['-nosplash', '-nodesktop'])
        
    def check_call(self, mock_system, options):
        '''
        Check that build_matlab() called Matlab correctly. 
        mock_system should be the mock of os.system in build_matlab().
        '''
        # Extract the system command
        command = mock_system.call_args[0][0]
        # Look for the expected executable and options
        self.assertTrue(re.search('^matlab', command))  
        for option in options:
            self.assertIn(option, command.split(' '))       

    @helpers.platform_patch('win32', path)
    @main_patch
    def test_windows(self, mock_copy, mock_system):
        '''
        Test that build_matlab() creates a log and properly submits
        a matlab system command on a Windows machine.
        '''
        mock_copy.side_effect   = fx.matlab_copy_effect
        mock_system.side_effect = fx.matlab_side_effect

        helpers.standard_test(self, gs.build_matlab, 'm')
        self.check_call(mock_system, ['-nosplash', '-minimize', '-wait'])

    @helpers.platform_patch('riscos', path)
    @main_patch
    def test_other_os(self, mock_copy, mock_system):
        '''
        Test that build_matlab() raises an exception when run on a
        non-Unix, non-Windows operating system.
        '''
        mock_copy.side_effect   = fx.matlab_copy_effect
        mock_system.side_effect = fx.matlab_side_effect
        with self.assertRaises(Exception):
            gs.build_matlab(target = './build/test.mat', 
                            source = './input/matlab_test_script.m', 
                            env    = {})

    @main_patch
    def test_clarg(self, mock_copy, mock_system):
        '''
        Test that build_matlab() properly sets command-line arguments
        in its env argument as system environment variables.
        '''
        mock_copy.side_effect   = fx.matlab_copy_effect
        mock_system.side_effect = fx.matlab_side_effect

        env = {'CL_ARG': 'COMMANDLINE'}
        helpers.standard_test(self, gs.build_matlab, 'm', 
                              system_mock = mock_system, env = env)
        self.assertEqual(os.environ['CL_ARG'], env['CL_ARG'])

    def test_bad_extension(self): 
        '''Test that build_matlab() recognises an improper file extension'''
        helpers.bad_extension(self, gs.build_matlab, good = 'test.m')
   

if __name__ == '__main__':
    unittest.main()
