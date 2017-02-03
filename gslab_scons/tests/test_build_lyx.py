#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import re

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons.builders.build_lyx as gs
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout


class TestBuildLyX(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')
        if not os.path.exists('./input/lyx_test_file.lyx'):
            with open('./input/lyx_test_file.lyx', 'wb') as test_file:
                test_file.write('Test LyX file\n')

    @mock.patch('gslab_scons.builders.build_lyx.os.system')
    def test_default(self, mock_system):
        '''
        Test that build_lyx() behaves correctly when provided with
        standard inputs. 
        '''
        mock_system.side_effect = self.os_system_side_effect
        target = './build/lyx.pdf'

        gs.build_lyx(target, source = './input/lyx_test_file.lyx', env = '')
        self.check_output(log_path = './build/sconscript.log',
                          target   = target)

    @staticmethod
    def os_system_side_effect(*args, **kwargs):
        '''
        This side effect mocks the behaviour of a system call.
        The mocked machine has lyx set up as a command-line executable
        and can export .lyx files to .pdf files only using 
        the "-e pdf2" option.
        '''
        # Get and parse the command passed to os.system()
        command = args[0]
        match = re.match('\s*'
                            '(?P<executable>\w+)'
                            '\s+'
                            '(?P<option>-\w+ \w+)?'
                            '\s*'
                            '(?P<source>[\.\/\w]+\.\w+)?'
                            '\s*'
                            '(?P<log_redirect>\> [\.\/\w]+\.\w+)?',
                         command)

        executable   = match.group('executable')
        option       = match.group('option')
        source       = match.group('source')
        log_redirect = match.group('log_redirect')

        option_type    = re.findall('^(-\w+)',  option)[0]
        option_setting = re.findall('\s(\w+)$', option)[0]

        is_lyx = bool(re.search('^lyx$', executable, flags = re.I))

        # As long as output is redirected, create a log
        if log_redirect:
            log_path = re.sub('>\s*', '', log_redirect)
            with open(log_path, 'wb') as log_file:
                log_file.write('Test log\n')

        # If LyX is the executable, the options are correctly specified,
        # and the source exists, produce a .pdf file with the same base 
        # name as the source file.
        if is_lyx and option_type == '-e' and option_setting == 'pdf2' \
                  and os.path.isfile(source):
            out_path = re.sub('lyx$', 'pdf', source, flags = re.I)
            with open(out_path, 'wb') as out_file:
                out_file.write('Mock .pdf output')


    def check_output(self, 
                     log_path = './build/sconscript.log', 
                     target   = './build/lyx.pdf'):
        '''
        Check that the file specified by log_path has a 
        log creation timestamp and that target exits.
        '''
        with open(log_path, 'rU') as log_file:
            log_data = log_file.read()

        self.assertIn('Log created:', log_data)
        os.remove(log_path)

        self.assertTrue(os.path.isfile(target))


    @mock.patch('gslab_scons.builders.build_lyx.os.system')
    def test_list_arguments(self, mock_system):
        '''
        Check that build_lyx() works when its source and target 
        arguments are lists
        '''
        mock_system.side_effect = self.os_system_side_effect
        target = './build/lyx.pdf'

        gs.build_lyx(target, source  = ['./input/lyx_test_file.lyx'], env = '')
        self.check_output('./build/sconscript.log', target)


    def test_bad_extension(self):
        '''Test that build_lyx() recognises an inappropriate file extension'''
        with self.assertRaises(BadExtensionError), nostderrout():
            gs.build_lyx(target = './build/lyx.pdf', 
                         source = ['bad', './input/lyx_test_file.lyx'], 
                         env    = '')
   
    @mock.patch('gslab_scons.builders.build_lyx.os.system')
    def test_env_argument(self, mock_system):
        '''
        Test that numerous types of objects can be passed to 
        build_lyx() without affecting the function's operation.
        '''
        mock_system.side_effect = self.os_system_side_effect
        target = './build/lyx.pdf'
        source = ['./input/lyx_test_file.lyx']
        log    = './build/sconscript.log'

        gs.build_lyx(target, source, env = True)
        self.check_output(log, target)

        gs.build_lyx(target, source, env = [1, 2, 3])
        self.check_output(log, target)  

        gs.build_lyx(target, source, env = ('a', 'b'))
        self.check_output(log, target) 

        gs.build_lyx(target, source, env = None)
        self.check_output(log, target)    

        gs.build_lyx(target, source, env = TypeError)
        self.check_output('./build/sconscript.log')  


    @mock.patch('gslab_scons.builders.build_lyx.os.system')
    def test_nonexistent_source(self, mock_system):
        '''
        Test build_lyx()'s behaviour when the source file
        does not exist.
        '''
        mock_system.side_effect = self.os_system_side_effect
        # i) Directory doesn't exist
        with self.assertRaises(IOError), nostderrout():
            gs.build_lyx('./build/lyx.pdf', 
                         ['./nonexistent_directory/lyx_test_file.lyx'], env = True)
        # ii) Directory exists, but file doesn't
        with self.assertRaises(IOError), nostderrout():
            gs.build_lyx('./build/lyx.pdf', 
                         ['./input/nonexistent_file.lyx'], env = True)   


    @mock.patch('gslab_scons.builders.build_lyx.os.system')
    def test_nonexistent_target_directory(self, mock_system):
        '''
        Test build_lyx()'s behaviour when the target file's
        directory does not exist.
        '''
        mock_system.side_effect = self.os_system_side_effect
        with self.assertRaises(IOError), nostderrout():
            gs.build_lyx('./nonexistent_directory/lyx.pdf', 
                         ['./input/lyx_test_file.lyx'], env = True)


    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')
        if os.path.exists('./input/lyx_test_file.lyx'):
            os.remove('./input/lyx_test_file.lyx')
                
if __name__ == '__main__':
    unittest.main()
