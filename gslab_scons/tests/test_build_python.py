#! /usr/bin/env python
import unittest
import sys
import os
import shutil

sys.path.append('../..')
from gslab_scons import build_python
from gslab_scons._exception_classes import BadExtensionError


class TestBuildPython(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    def test_log_creation(self):
        '''
        Test that build_python() creates a log in its
        target's directory.
        '''
        build_python(target = './build/py.py', 
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
            build_python('./build/py.py', 
                         ['bad', './input/python_test_script.py'], 
                         env = '')

    def test_unintended_inputs(self):
        env    = None
        source = './input/python_test_script.py'
        target = './build/py.py'
        log    = './build/sconscript.log'
        # env can be None
        build_python(target, source, env)
        self.check_log(log)

        #== target ===============
        # Containers of strings should not raise errors
        build_python(('a', 'b'), source, env)           
        self.check_log('./sconscript.log')
        # Other non-string inputs should
        with self.assertRaises(TypeError):
            build_python(None, source, env)
        with self.assertRaises(TypeError):
            build_python(1, source, env)

        #== source ===============

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
        build_python(target, source, env = '')
        # The target doesn't exist...
        with self.assertRaises(IOError):
            open(target, 'rU')
        # ...but the log does.
        self.check_log('./build/sconscript.log')


    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
