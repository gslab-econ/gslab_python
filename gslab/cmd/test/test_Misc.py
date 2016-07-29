
import unittest, os, sys
import numpy as np
sys.path.append('..')
from py_module.Misc import *

class test_Misc(unittest.TestCase):
    def test_isPSD_zeros(self):
        matrix = np.zeros([5, 5])
        T = isPSD(matrix)
        self.assertEqual(T, True)       
    
    def test_isPSD_identity(self):
        matrix = np.identity(13)
        T = isPSD(matrix)
        self.assertEqual(T, True)
    
    def test_isPSD_1(self):
        matrix = np.matrix([[2, -1, 0],
                            [-1, 2, -1],
                            [0, -1, 2]])
        T = isPSD(matrix)
        self.assertEqual(T, True)
   
if __name__ == '__main__':
    os.getcwd()
    unittest.main()