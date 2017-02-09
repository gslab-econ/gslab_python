#! /usr/bin/env python
import unittest
import sys
import os
import re
import shutil
import mock

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons
import gslab_scons.misc as misc
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout


class test_misc(unittest.TestCase):

    def test_check_lfs(self):
        pass

    @unittest.skipIf(sys.platform.startswith("win"), 
        "skipped test_stata_command_unix because on a windows machine")
    def test_stata_command_unix(self):
        cl_arg = 'test'
    	output = misc.stata_command_unix('flavor', cl_arg)
    	if sys.platform == 'darwin':
    		option = '-e'
    	else:
    		option = '-b'
    	self.assertEqual(output, 'flavor %s' % (option) + ' %s ' + cl_arg)

    @unittest.skipUnless(sys.platform.startswith("win"), 
        "skipped test_stata_command_win because on a unix machine")
    def test_stata_command_win(self):
        cl_arg = 'test'
    	output = misc.stata_command_win('flavor', cl_arg)
    	self.assertEqual(output, 'flavor %s' % ('/e do') + ' %s ' + cl_arg)

    def test_is_unix(self):
        self.assertEqual(misc.is_unix(), not sys.platform.startswith("win"))

    def test_is_64_windows(self):
        pass

    def test_command_line_arg(self):
        self.assertEqual(misc.command_line_arg({'test' : ''}), '')
        self.assertEqual(misc.command_line_arg({'CL_ARG' : 'Test'}), 'Test')

    @unittest.skipIf(sys.platform.startswith("win"), 
    "skipped test_is_in_path because on a windows machine")
    def test_is_in_path(self):
        self.assertEqual(misc.is_in_path('jabberwocky_long_program_name_that_fails'), False)
        self.assertTrue(re.search('python', misc.is_in_path('python')))

    @unittest.skipIf(sys.platform.startswith("win"), 
    "skipped test_is_exe because on a windows machine")
    def test_is_exe(self):
        pyth_exec = misc.is_in_path('python')
        self.assertTrue(misc.is_exe(pyth_exec))
        self.assertFalse(misc.is_exe('BAD_EXEC_FILE'))

    def test_make_list_if_string(self):
        self.assertEqual(misc.make_list_if_string(['test', 'test']), ['test', 'test'])
        self.assertEqual(misc.make_list_if_string('test'), ['test'])
        self.assertEqual(misc.make_list_if_string(['test']), ['test'])

    def test_check_code_extension(self):
        '''Unit tests for check_code_extension()

        This method tests that check_code_extensions() associates software with 
        file extensions as intended.
        '''
    	self.assertEqual(misc.check_code_extension('test.do',  'stata'),  None)
    	self.assertEqual(misc.check_code_extension('test.r',   'r'),      None)
    	self.assertEqual(misc.check_code_extension('test.lyx', 'lyx'),    None)
        self.assertEqual(misc.check_code_extension('test.py',  'python'), None)
        self.assertEqual(misc.check_code_extension('test.m',   'matlab'), None)
        self.assertEqual(misc.check_code_extension('test.M',   'matlab'), None)
    	
        with self.assertRaises(BadExtensionError), nostderrout():
            misc.check_code_extension('test.badextension', 'python')

    def test_current_time(self):
        '''Test that current_time() prints times in the expected format'''
        the_time = misc.current_time()
        self.assertTrue(re.search('\d+-\d+-\d+\s\d+:\d+:\d+', the_time))
    
    def test_state_of_repo(self):
        env = {'MAXIT' : '10'}
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
        infile = open('./input/lyx_test_dependencies.lyx').read()
        node   = mock.MagicMock(get_contents = lambda: infile)
        env    = mock.MagicMock(EXTENSIONS = ['.lyx', '.txt'])
        output = misc.lyx_scan(node, env, None)
        self.assertEqual(output, ['lyx_test_file.lyx', 'tables_appendix.txt'])


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
