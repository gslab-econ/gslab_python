#! /usr/bin/env python

import unittest, os, sys
import numpy as np
sys.path.append('..')
from py_module.MiscFunctions import *


class test_approxloc(unittest.TestCase):
    def test_outofrange(self):
        array = np.arange(5.7, 5.634, -.001)
        self.assertEqual(approxloc(6, array), 0)

    def test_neg(self):
        array = np.arange(-1, -2, -.01)
        self.assertEqual(approxloc(-1.056, array), 6)
    
    def test_pos(self):
        array = np.arange(1, 2, .01)
        self.assertEqual(approxloc(1.056, array), 6)
    
        
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
