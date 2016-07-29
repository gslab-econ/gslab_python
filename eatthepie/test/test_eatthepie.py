#! /usr/bin/env python

import unittest, os, sys
import numpy as np
sys.path.append('..')
import py_module.eatthepie as eatthepie


class test_eatthepie(unittest.TestCase):
    def test_utility(self):
        etp = eatthepie.ETP(rho = .5)
        self.assertEqual(etp.utility(9), 6)
        etplogutility = eatthepie.ETP(rho = 1)
        self.assertEqual(etplogutility.utility(10), np.log(10))

    def test_analytic(self):
        etp = eatthepie.ETP(init_wealth = 5, income_vec = np.zeros(5), horizon = 5,
                            R = 1.08, delta = 1 / (1 + .06), BequestValue = 0, rho = .8, error_checks = "on")
        numerical = etp.BellmanGridSolve(gridmesh = .05, interp_method = "linear")
        analytic = etp.analytic_solution()
        for i in range(etp.horizon - 1):
            self.assertAlmostEqual(abs(analytic[i] - numerical[i]), 0.00, places = 2)
    
    def test_flatconsumption(self):
        etp = eatthepie.ETP(init_wealth = 5, income_vec = np.zeros(5), horizon = 5, 
                            R = 1.10, delta = 1 / (1.10), BequestValue = 0, rho = .8, error_checks = "on")
        numerical = etp.BellmanGridSolve(gridmesh = .05, interp_method = "linear")
        for i in range(etp.horizon - 1):
            self.assertAlmostEqual(numerical[i], numerical[i + 1], places = 2)    
    
    def test_floathorizon(self):
        etp = eatthepie.ETP(init_wealth = 5, income_vec = np.zeros(5), horizon = 5.00, 
                            R = 1.10, delta = 1 / (1.10), BequestValue = 0, rho = .8, error_checks = "on")
        self.assertEqual(isinstance(etp.horizon, int), 1)

    def test_errorchecks(self):
        etp = eatthepie.ETP(init_wealth = 5, income_vec = np.zeros(5), horizon = 5, 
                            R = 1.10, delta = 1 / (1.10), BequestValue = 0, rho = 1.2, error_checks = "off")
        self.assertEqual(etp.error_checks, "off")           
   
    def test_zeroconsumption(self):
        etp = eatthepie.ETP(init_wealth = 0, income_vec = np.zeros(3), horizon = 3, 
                            R = 1.10, delta = .1, BequestValue = 0, rho = 1.2, error_checks = "off")
        numerical = etp.BellmanGridSolve(gridmesh = .01, interp_method = "linear")
        for i in range(etp.horizon):
            self.assertAlmostEqual(np.abs(numerical[i]), 0.00, places = 2) 
        
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
