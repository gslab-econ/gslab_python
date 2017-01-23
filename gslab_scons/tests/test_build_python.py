#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import subprocess

sys.path.append('../..')
import gslab_scons.builders.build_python as gs
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout

class TestBuildPython(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    def test_log_creation(self):
        '''
        Test that build_python() creates a log in its
        target's directory.
        '''
        gs.build_python(target = './build/py.py', 
                       source = './input/python_test_script.py', 
                       env    = '')
        self.check_log('./build/sconscript.log')

    def check_log(self, log_path = './build/sconscript.log'):
        with open(log_path, 'rU') as log_file:
            log_data = log_file.read()

        self.assertIn('Log created:', log_data)
        os.remove(log_path)

    def test_bad_extension(self):
        '''
        Test that build_python() raises the appropriate error
        when the first source lacks the appropriate file extension.
        '''
        with self.assertRaises(BadExtensionError):
            gs.build_python('./build/py.py', 
                           ['bad', './input/python_test_script.py'], 
                           env = '')

    def test_unintended_inputs(self):
        '''
        Test that build_python() handles unintended inputs
        as we expect it to. 
        '''
        env    = None
        source = './input/python_test_script.py'
        target = './build/py.py'
        log    = './build/sconscript.log'
        # env can be None
        gs.build_python(target, source, env)
        self.check_log(log)

        #== target ===============
        # Containers of strings should not raise errors
        gs.build_python(('a', 'b'), source, env)           
        self.check_log('./sconscript.log')
        # Neither should empty strings
        gs.build_python('', source, env)           
        self.check_log('./sconscript.log')       
        # Other non-string inputs should
        with self.assertRaises(TypeError):
            gs.build_python(None, source, env)
        with self.assertRaises(TypeError):
            gs.build_python(1, source, env)

        #== source ===============
        # We can have multiple sources, and we can 
        # specify sources that don't exist...
        gs.build_python(target = '', 
                        source = ['./input/python_test_script.py', 
                                 'nonexistent_data.txt'], 
                        env    = None)           
        self.check_log('./sconscript.log')
        # ...but a .py script must be the first source.
        with self.assertRaises(BadExtensionError):
            gs.build_python(target = '', 
                            source = ['nonexistent_data.txt',
                                   './input/python_test_script.py'], 
                            env    = None)
        # build_python() does not raise an error if this .py file
        # doesn't actually exist (this may be undesirable).
        # Instead, we expect it to print an error message to the 
        # console and continue. 
        print "Expecting console output suggesting an error:\n"
        gs.build_python(target = '', 
                        source = ['nonexistent_data.py',
                              './input/python_test_script.py'], 
                         env    = None)
        print "No longer expecting an error message.\n"
        self.check_log('./sconscript.log')

    def test_target_creation_unnecessary(self):
        '''
        Test that build_python() can run without
        actually creating its target.
        '''
        source = './input/test_script.py'
        target = './build/test_target.txt'
        with open(source, 'wb') as test_script:
            test_script.write('def main():\n'
                              '    pass   \n'
                              'main()     \n')
        gs.build_python(target, source, env = '')
        # The target doesn't exist...
        with self.assertRaises(IOError):
            open(target, 'rU')
        # ...but the log does.
        self.check_log('./build/sconscript.log')
        os.remove(source)

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
