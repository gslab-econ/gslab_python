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

import gslab_scons.misc as misc
import gslab_scons._exception_classes as ex_classes
from gslab_make.tests import nostderrout

# This class is used for testing current_time()
class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2017, 1, 20, 
                   15,   2, 18, 
                   133911)


class TestMisc(unittest.TestCase):
    @mock.patch('gslab_scons.misc.subprocess.check_output')
    def test_check_lfs_success(self, mock_check):
        '''
        Test that check_lfs() works when either of the commands
        `git-lfs install` or `git-lfs init` runs without error.
         '''
        try:
            mock_check.side_effect = self.make_side_effect(['install', 'init'])
            misc.check_lfs()
        except:
            self.fail('check_lfs() raised an error when '
                     '`git-lfs install` and `git-lfs init` were '
                      'both valid commands.')
        try:
            mock_check.side_effect = self.make_side_effect(['init'])
            misc.check_lfs()
        except:
            self.fail('check_lfs() raised an error when '
                      '`git-lfs init` was a valid command.')

        try:
            mock_check.side_effect = self.make_side_effect(['install'])
            misc.check_lfs()
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

    @mock.patch('gslab_scons.misc.subprocess.check_output')
    def test_check_lfs_failure(self, mock_check):
        '''
        Test that check_lfs() fails when neither `git-lfs install` nor
        `git-lfs init` are acceptable commands. 
        '''
        with self.assertRaises(ex_classes.LFSError):
            mock_check.side_effect = self.make_side_effect(['checkout'])
            misc.check_lfs()


    #== Tests for stata_command_unix() and stata_command_win() ======
    # The tests below patch sys.platform to mock various 
    # operating systems. 
    @mock.patch('gslab_scons.misc.sys.platform', 'darwin')
    def test_stata_command_unix_mac(self):
        '''
        Test that stata_command_unix() returns the expected
        command when run on Mac computers.
        '''
        output = misc.stata_command_unix('stata')
        self.assertEqual(output.strip(), 'stata -e %s')

        output = misc.stata_command_unix('stata', cl_arg = 'cl_arg')
        self.assertEqual(output.strip(), 'stata -e %s cl_arg')

        output = misc.stata_command_unix('stata', cl_arg = 1)
        self.assertEqual(output.strip(), 'stata -e %s 1')

    @mock.patch('gslab_scons.misc.sys.platform', 'linux')
    def test_stata_command_unix_linux(self):
        '''
        Test that stata_command_unix() returns the expected
        command when run on Linux computers.
        '''        
        output = misc.stata_command_unix('stata-se')
        self.assertEqual(output.strip(), 'stata-se -b %s')

        output = misc.stata_command_unix('stata', cl_arg = 'cl_arg')
        self.assertEqual(output.strip(), 'stata -b %s cl_arg')


    @mock.patch('gslab_scons.misc.sys.platform', 'win32')
    def test_stata_command_unix_windows(self):
        '''
        Test that stata_command_unix() raises an error when
        when on Windows computers.
        '''
        with self.assertRaises(KeyError):
            output = misc.stata_command_unix('stata-mp')

        with self.assertRaises(KeyError):
            output = misc.stata_command_unix('stata-mp', cl_arg = 'cl_arg')           
        
    @mock.patch('gslab_scons.misc.sys.platform', 'cygwin')
    def test_stata_command_unix_other(self):
        '''
        Test that stata_command_unix() raises an error when 
        run on non-Windows, non-Mac, non-Linux machines.
        '''
        with self.assertRaises(KeyError):
            output = misc.stata_command_unix('stata-mp')

    @mock.patch('gslab_scons.misc.sys.platform', 'win32')        
    def test_stata_command_win_windows(self):
        output = misc.stata_command_win('stata-mp')
        self.assertEqual(output.strip(), 'stata-mp /e do %s')

        output = misc.stata_command_win('stata-mp', cl_arg = 'cl_arg')
        self.assertEqual(output.strip(), 'stata-mp /e do %s cl_arg') 

        output = misc.stata_command_win('stata-mp', cl_arg = 1)
        self.assertEqual(output.strip(), 'stata-mp /e do %s 1')              

    @mock.patch('gslab_scons.misc.sys.platform', 'darwin')        
    def test_stata_command_win_unix(self):
        '''
        Test that stata_command_win() gives a Windows stata
        command even on a non-Windows machine. 
        '''
        output = misc.stata_command_win('stata-mp')
        self.assertEqual(output.strip(), 'stata-mp /e do %s')

        output = misc.stata_command_win('stata-mp', cl_arg = 'cl_arg')
        self.assertEqual(output.strip(), 'stata-mp /e do %s cl_arg')   

        output = misc.stata_command_win('stata-mp', cl_arg = 1)
        self.assertEqual(output.strip(), 'stata-mp /e do %s 1')               
    #================================================================
    
    def test_is_unix(self):
        '''
        Test that is_unix() returns True on Mac and Linux
        machines and False otherwise. 
        '''
        platform_ref = 'gslab_scons.misc.sys.platform'
        with mock.patch(platform_ref, 'win32'):
            self.assertFalse(misc.is_unix())

        with mock.patch(platform_ref, 'darwin'):
            self.assertTrue(misc.is_unix())  

        with mock.patch(platform_ref, 'linux'):
            self.assertTrue(misc.is_unix())    

        with mock.patch(platform_ref, 'atheos'):
            self.assertFalse(misc.is_unix())     

    def test_is_64_windows(self):
        '''
        Test that is_64_windows() returns True when PROGRAMFILES(X86)
        is a key in the system environment as accessed through 
        os.environ.
        '''
        environ = 'gslab_scons.misc.os.environ'
        mocked_environ = {'PROGRAMFILES(X86)': 'C:/Program Files (x86)'}
        with mock.patch(environ, mocked_environ):
            self.assertTrue(misc.is_64_windows())
        with mock.patch(environ, dict()):
            self.assertFalse(misc.is_64_windows())

    @mock.patch('gslab_scons.misc.os.environ', {'PATH': '/bin:usrs/local'})
    @mock.patch('gslab_scons.misc.os.pathsep', ':')
    @mock.patch('gslab_scons.misc.os.access')
    def test_is_in_path(self, mock_access):
        '''
        Test that is_in_path() returns i) the full path of 
        a recognised executable that the function takes as
        an argument and ii) None if the function's argument
        is not recognised as an executable. 
        '''
        mock_access.side_effect = self.access_side_effect

        self.assertEqual(misc.is_in_path('stata'), 
                         '/bin/stata')
        self.assertEqual(misc.is_in_path('executable_file'), 
                         'executable_file')
        self.assertEqual(misc.is_in_path('stata-mp'),
                         None)
                            
    @staticmethod
    def access_side_effect(*args, **kwargs):
        '''
        This function mocks os.access by defining which
        files our mocked up machine can execute or 
        otherwise access. 
        '''
        # Define the files to which we have access
        # Total access        
        execute_files = ['/bin/stata',
                         'executable_file']
        # Total access except execution
        other_files   = ['test_script.do']
        
        # Access the arguments of the os.access() call.
        path = args[0]
        mode = args[1]

        # If mode == os.X_OK, return True only for files with execute access
        if mode == os.X_OK and path in execute_files:
            result = True
        # For other modes return True if the file exists in our mocked set-up
        elif mode != os.X_OK and path in (execute_files + other_files):
            result = True
        # If the file doesn't "exist":
        else:
            result = False

        return result 

    def test_command_line_args(self):
        env = {'test' : ''}
        self.assertEqual(misc.command_line_args(env), '')

        env = {'CL_ARG' : 'Test'}
        self.assertEqual(misc.command_line_args(env), 'Test')

        env = {'CL_ARG' : 1}
        self.assertEqual(misc.command_line_args(env), '1')

        env = {'CL_ARG' : ['Test_1', 'Test_2']}
        self.assertEqual(misc.command_line_args(env), 'Test_1 Test_2')

        env = {'CL_ARG' : [True, None, 'Test']}
        self.assertEqual(misc.command_line_args(env), 'True None Test')             

    def test_make_list_if_string(self):
        self.assertEqual(misc.make_list_if_string(['test', 'test']), 
                                                  ['test', 'test'])
        self.assertEqual(misc.make_list_if_string('test'), ['test'])
        self.assertEqual(misc.make_list_if_string(['test']), ['test'])
        
        # We expect objects that are neither strings nor lists to be 
        # returned without being manipulated.
        self.assertEqual(misc.make_list_if_string(1), 1)
        self.assertEqual(misc.make_list_if_string(TypeError), TypeError)
        self.assertEqual(misc.make_list_if_string(False), False)
        self.assertEqual(misc.make_list_if_string(None), None)

    def test_check_code_extension(self):
        '''Unit tests for check_code_extension()

        This method tests that check_code_extensions() associates software with 
        file extensions as intended. The function should return None in cases 
        where the extension is correctly specified and raise an error otherwise.
        '''
        self.assertEqual(misc.check_code_extension('test.do',  'stata'),  None)
        self.assertEqual(misc.check_code_extension('test.r',   'r'),      None)
        self.assertEqual(misc.check_code_extension('test.R',   'r'),      None)
        self.assertEqual(misc.check_code_extension('test.lyx', 'lyx'),    None)
        self.assertEqual(misc.check_code_extension('test.py',  'python'), None)
        self.assertEqual(misc.check_code_extension('test.M',   'matlab'), None)
        
        with self.assertRaises(ex_classes.BadExtensionError), nostderrout():
            misc.check_code_extension('test.badextension', 'python')
        with self.assertRaises(KeyError):
            misc.check_code_extension('test.m', 'Matlab')
        with self.assertRaises(KeyError):
            misc.check_code_extension('test.r', 'R')

    @mock.patch('gslab_scons.misc.datetime.datetime', MockDateTime)
    def test_current_time(self):
        '''
        Test that current_time() prints the correct current time
        in the expected format. Here, the "correct current time"
        is a fixed value set within the MockDateTime class.
        '''                            
        the_time = misc.current_time()
        self.assertEqual('2017-01-20 15:02:18', the_time)

    def test_state_of_repo(self):
        env = {'MAXIT': '10'}
        target = source = ''

        # Test general functionality
        misc.state_of_repo(target, source, env)
        logfile = open('state_of_repo.log', 'rU').read()
        self.assertIn('GIT STATUS', logfile)
        self.assertIn('FILE STATUS', logfile)

        # Test maxit functionality
        os.mkdir('state_of_repo')
        for i in range(1, 20):
            with open('state_of_repo/test_%s.txt' % i, 'wb') as f:
                f.write('Test')
        misc.state_of_repo(target, source, env)
        logfile = open('state_of_repo.log', 'rU').read()
        self.assertIn('MAX ITERATIONS', logfile)

        # Cleanup
        shutil.rmtree('state_of_repo')
        os.remove('state_of_repo.log')

    def test_lyx_scan(self):
        # Open a test LyX file containing dependency statements
        infile = open('./input/lyx_test_dependencies.lyx').read()
        # Mock an SCons node object to return this file's contents
        # when its get_contents() method is called.
        node   = mock.MagicMock(get_contents = lambda: infile)
        # Mock an SCons environment object with an EXTENSIONS data attribute
        env    = mock.MagicMock(EXTENSIONS = ['.lyx', '.txt'])
        output = misc.lyx_scan(node, env, None)
        # Ensure lyx_scan scanned the test file correctly
        self.assertEqual(output, ['lyx_test_file.lyx', 'tables_appendix.txt'])


if __name__ == '__main__':
    unittest.main()
