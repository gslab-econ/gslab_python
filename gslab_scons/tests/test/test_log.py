#! /usr/bin/env python

import unittest
import sys
import os
sys.path.append('../../..')
from gslab_scons.log import *

class test_log(unittest.TestCase):

    def test_start_log(self):
        pass

    def test_log_timestamp(self):
        with open('test.txt', 'wb') as f:
            f.write('TEST CONTENT')
    	log_timestamp('test_time_start', 'test_time_end', 'test.txt')
        with open('test.txt', 'rU') as f:
            content = f.read()
        self.assertEqual(content, 'Log created:    ' + 'test_time_start'+ '\n' + 
                'Log completed:  ' + 'test_time_end'  + '\n \n' + 'TEST CONTENT')
        os.remove('test.txt')
                
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
