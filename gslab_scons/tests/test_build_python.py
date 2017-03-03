import unittest
import sys
import os
import shutil
import mock
import subprocess
import re
# Import gslab_scons testing helper modules
import _test_helpers as helpers
import _side_effects as fx

sys.path.append('../..')
import gslab_scons.builders.build_python as gs
from gslab_scons._exception_classes import BadExtensionError
from gslab_make.tests import nostderrout

# Define path to the builder for use in patching
path = 'gslab_scons.builders.build_python'

class TestBuildPython(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @mock.patch('%s.os.system' % path)
    def test_log_creation(self, mock_system):
        '''Test build_python()'s behaviour when given standard inputs.'''
        mock_system.side_effect = fx.python_side_effect
        helpers.standard_test(self, gs.build_python, 'py', 
                              system_mock = mock_system)

    def test_bad_extension(self):
        '''Test that build_python() recognises an improper file extension'''
        helpers.bad_extension(self, gs.build_python, good = 'test.py')
   
    @mock.patch('%s.os.system' % path)
    def test_cl_arg(self, mock_system):
        mock_system.side_effect = fx.python_side_effect
        helpers.test_cl_args(self, gs.build_python, mock_system, 'py')

    @mock.patch('%s.os.system' % path)
    def test_unintended_inputs(self, mock_system):
        '''
        Test that build_python() handles unintended inputs 
        as expected. 
        '''
        mock_system.side_effect = fx.python_side_effect

        check = lambda **kwargs: helpers.input_check(self, gs.build_python, 
                                                     'py', **kwargs)

        # env's class must support indexing by strings
        check(env = None,  error = TypeError)
        check(env = 'env', error = TypeError)        

        # The target should be a string or a container
        for ok_target in [('a', 'b'), '', [1, 2]]:
            check(target = ok_target, error = None) 
        for bad_target in [None, 1]:
            check(target = bad_target, error = TypeError) 

        test_source = ['./test_script.py', 'nonexistent_data.txt']
        check(source = test_source, error = None)
        test_source.reverse()
        check(source = test_source, error = BadExtensionError)

    def test_nonexistent_input(self):
        '''
        Test that build_python() doesn't raise errors if
        its source script doesn't exist.
        '''
        if os.path.exists('test.py'):
            os.remove('test.py')

        helpers.standard_test(self, gs.build_python, source = 'test.py')

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

        gs.build_python(target, source, env = {})
        # The target doesn't exist...
        with self.assertRaises(IOError):
            open(target, 'rU')
        # ...but the log does.
        helpers.check_log(self, './build/sconscript.log')
        os.remove(source)

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.exists('output.txt'):
            os.remove('output.txt')


if __name__ == '__main__':
    unittest.main()
