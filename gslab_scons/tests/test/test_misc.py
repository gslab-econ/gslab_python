#! /usr/bin/env python

import unittest
import sys
import os
import re
sys.path.append('../../..')
from gslab_scons.misc import *
from sys import platform

class test_misc(unittest.TestCase):

    def test_check_lfs(self):
		pass

    @unittest.skipIf(sys.platform.startswith("win"), "skipped test_stata_command_unix because on a windows machine")
    def test_stata_command_unix(self):
    	output = stata_command_unix('flavor')
    	if platform == 'darwin':
    		option = '-e'
    	else:
    		option = '-b'
    	self.assertEqual(output, 'flavor %s' % (option) + ' %s ')

    @unittest.skipUnless(sys.platform.startswith("win"), "skipped test_stata_command_win because on a unix machine")
    def test_stata_command_win(self):
    	output = stata_command_win('flavor')
    	self.assertEqual(output, 'flavor %s' % ('/e do') + ' %s ')

    def test_is_unix(self):
    	self.assertEqual(is_unix(), not sys.platform.startswith("win"))

    def test_is_64_windows(self):
    	pass

    def test_is_in_path(self):
    	self.assertEqual(is_in_path('jabberwocky_long_program_name_that_fails'), None)
    	self.assertTrue(re.search('python', is_in_path('python')))

    def test_is_exe(self):
    	pyth_exec = is_in_path('python')
    	self.assertTrue(is_exe(pyth_exec))
    	self.assertFalse(is_exe('BAD_EXEC_FILE'))

    def test_make_list_if_string(self):
    	self.assertEqual(make_list_if_string(['test', 'test']), ['test', 'test'])
    	self.assertEqual(make_list_if_string('test'), ['test'])
    	self.assertEqual(make_list_if_string(['test']), ['test'])

    def test_check_code_extension(self):
    	self.assertEqual(check_code_extension('test.do', 'stata'), None)
    	self.assertEqual(check_code_extension('test.r', 'r'), None)
    	self.assertEqual(check_code_extension('test.lyx', 'lyx'), None)
    	self.assertEqual(check_code_extension('test.py', 'python'), None)
    	with self.assertRaises(BadExtensionError):
    		check_code_extension('test.badextension', 'python')

    def test_current_time(self):
    	t = current_time()
    	self.assertTrue(re.search('\d+-\d+-\d+\s\d+:\d+:\d+', t))
                
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
