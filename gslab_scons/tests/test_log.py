import unittest
import sys
import os
import mock
import time

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons.log as gs
import gslab_scons.misc as misc
import gslab_scons._exception_classes as ex_classes
from gslab_make.tests import nostderrout

class TestLog(unittest.TestCase):

    # I think that we should mock check_lfs in all tests
    # so that the tests run irrespectively of whether the
    # user has git_lfs

    def setUp(self):
        if os.path.isfile('sconstruct.log'):
            os.remove('sconstruct.log')

    # Set the platform to darwin (sys.platform = 'darwin' on  Mac machines).
    @mock.patch('gslab_scons.log.misc.sys.platform', 'darwin')
    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_stdout_on_unix(self, mock_lfs):
        '''
        Test that start_log() leads stdout to be captured in 
        a log file on Unix machines. 
        '''    
        initial_stdout = sys.stdout

        gs.start_log()
        print "Test message"
        sys.stdout.close()
        sys.stdout = initial_stdout

        with open('sconstruct.log', 'rU') as f:
            log_contents = f.read()
        self.assertEqual("Test message", log_contents.strip())

    @mock.patch('gslab_scons.log.misc.sys.platform', 'darwin')
    @mock.patch('gslab_scons.log.os.popen')
    @mock.patch('gslab_scons.log.open')
    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_popen_on_unix(self, mock_lfs, mock_open, mock_popen):
        '''
        Test that start_log() uses popen() to initialise its log
        on Unix machines.
        '''    
        gs.start_log()
        mock_popen.assert_called_with('tee sconstruct.log', 'wb')
        gs.start_log('test_log.txt')
        mock_popen.assert_called_with('tee test_log.txt', 'wb')       

        mock_open.assert_not_called()

    # Set the platform to Windows
    @mock.patch('gslab_scons.log.sys.platform', 'win32')
    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_stdout_on_windows(self, mock_lfs):
        '''
        Test that start_log() leads stdout to be captured in 
        a log file on Windows machines. 
        '''       
        initial_stdout = sys.stdout

        gs.start_log()
        print "Test message"
        sys.stdout.close()
        sys.stdout = initial_stdout

        with open('sconstruct.log', 'rU') as f:
            log_contents = f.read()
        self.assertEqual("Test message", log_contents.strip())

    @mock.patch('gslab_scons.log.misc.sys.platform', 'win32')
    @mock.patch('gslab_scons.log.os.popen')
    @mock.patch('gslab_scons.log.open')
    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_open_on_windows(self, mock_lfs, mock_open, mock_popen):
        '''
        Test that start_log() uses open() to initialise its log
        on Windows machines.
        '''
        gs.start_log()
        mock_open.assert_called_with('sconstruct.log', 'wb')
        gs.start_log('test_log.txt')
        mock_open.assert_called_with('test_log.txt', 'wb')       

        mock_popen.assert_not_called()

    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_no_lfs(self, mock_check_lfs):
        # Check that start_log() fails if check_lfs() finds that
        # git-lfs is not installed
        mock_check_lfs.side_effect = self.check_lfs_effect
        with self.assertRaises(ex_classes.LFSError), nostderrout():
            gs.start_log()

    @mock.patch('gslab_scons.log.misc.sys.platform', 'cygwin')
    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_other_os(self, mock_lfs):
        '''
        Test start_log()'s behaviour when run on a platform other
        than Windows, Darwin, or Linux.
        (We don't expect it to change sys.stderr or sys.stdout.)
        '''
        initial_stderr = sys.stderr
        initial_stdout = sys.stdout
        gs.start_log()
        self.assertEqual(initial_stderr, sys.stderr)
        self.assertEqual(initial_stdout, sys.stdout)

    @mock.patch('gslab_scons.log.misc.sys.platform', 'darwin')
    @mock.patch('gslab_scons.log.misc.check_lfs')
    def test_start_log_nonstring_input(self, mock_lfs):
        '''
        Test start_log()'s behaviour when its log argument is
        not a string.
        '''
        initial_stdout = sys.stdout
        gs.start_log(1)
        self.check_log_creation('1', initial_stdout)

        gs.start_log(True)
        self.check_log_creation('True', initial_stdout)

        gs.start_log([1, 2, 3])
        self.check_log_creation(['[1,', '2,', '3]'], initial_stdout)

    def check_log_creation(self, log_names, initial_stdout):
        sys.stdout.close()
        if isinstance(log_names, str):
            log_names = [log_names]
        for log in log_names:
            self.assertTrue(os.path.isfile(log))
            os.remove(log)
        sys.stdout = initial_stdout

    @staticmethod
    def check_lfs_effect(*args, **kwargs):
        raise ex_classes.LFSError('Git LFS is not installed.')

    def test_log_timestamp(self):
        '''Test that log_timestamp() correctly adds start/end times to a log'''
        # Write the test log file and use log_timestamp() to add 
        # stand-in starting and ending time messages.
        with open('test.txt', 'wb') as f:
            f.write('TEST CONTENT')
    	gs.log_timestamp('test_time_start', 'test_time_end', 'test.txt')
        
        # Read the test log file and ensure log_timestamp() worked
        # as intended.
        with open('test.txt', 'rU') as f:
            content = f.read()
        self.assertEqual(content, 'Log created:    ' + 'test_time_start' + 
                                  '\n' + 
                                  'Log completed:  ' + 'test_time_end'   + 
                                  '\n \n' + 
                                  'TEST CONTENT')
        os.remove('test.txt')
       
    def tearDown(self):
        if os.path.isfile('sconstruct.log'):
           os.remove('sconstruct.log')
        if os.path.isfile('test_log.txt'):
           os.remove('test_log.txt')


if __name__ == '__main__':
    unittest.main()
