import os
import sys
sys.path.append('../..')
from gslab_scons._exception_classes import BadExtensionError


def check_log(test_object, log_path, expected_text = ''):
    '''Check for the existence of a timestamped log'''
    with open(log_path, 'rU') as log_file:
        log_data = log_file.read()

    test_object.assertIn('Log created:', log_data)

    if expected_text:
        test_object.assertIn(expected_text, log_data)

    os.remove(log_path)


def bad_extension(test_object, builder, 
                  bad  = 'bad',
                  good = None,
                  env = {}):
    if good:
        source = [bad, good]
    else:
        source = [bad]

    with test_object.assertRaises(BadExtensionError):
        builder(target = './test_output.txt', 
                source = [bad, good], 
                env    = env)

