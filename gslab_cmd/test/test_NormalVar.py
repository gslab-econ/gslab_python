#! /usr/bin/env python

import unittest, os, sys
import numpy as np
sys.path.append('..')
from py_module.NormalVar import *

class test_NormalVar(unittest.TestCase):
    def test_minimizeQ(self):
        np.random.seed(10)
        data = np.random.normal(1, 3, 10)
        firstmoment = np.mean(data)
        secondmoment = np.mean(data ** 2)
        stats = np.matrix([[firstmoment], [secondmoment]])
        cmd = CMD_normalvar(W = np.identity(2), stats = stats)
        cmd.estimate([0, 0])
        self.assertAlmostEqual(np.abs(cmd.parameter_estimates[0] - np.mean(data)) + np.abs(cmd.parameter_estimates[1] - np.var(data)), 0, delta = .001)       
    
    def test_minimizeQ_trueparam(self):
        np.random.seed(20)
        data = np.random.normal(1, 3, 10000)
        firstmoment = np.mean(data)
        secondmoment = np.mean(data ** 2)
        stats = np.matrix([[firstmoment], [secondmoment]])
        cmd = CMD_normalvar(W = np.identity(2), stats = stats)
        cmd.estimate([0, 0])
        self.assertAlmostEqual(np.abs(cmd.parameter_estimates[0] - 1) + np.abs(cmd.parameter_estimates[1] - 9), 0, delta = .2)       
   
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
