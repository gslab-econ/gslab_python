import unittest
import sys
import numpy as np
import pandas as pd

sys.path.append('../py')
import ivreg

class test(unittest.TestCase):

    def test_ivreg(self):
        test_input = pd.read_csv('../temp/ivreg_test_input.csv')
        stata_vcov = np.fromfile('../temp/stata_variance.txt', sep='\t').reshape(2,2)
        stata_coeff = np.fromfile('../temp/stata_coeffs.txt', sep='\t').reshape(2,1)
        stata_dof = np.fromfile('../temp/stata_dof.txt', sep='\t')[0]

        N = len(test_input.index)
        cons = np.ones((N,1))
        endog = test_input['mpg'].values.reshape(N,1)
        inst  = test_input['displacement'].values.reshape(N,1)
        depvar = test_input['price'].values.reshape(N,1)

        (b, V, dof) = ivreg.tsls(depvar=depvar, inst=inst, endog=endog, exog=cons)

        self.assertTrue(np.allclose(b, stata_coeff))
        self.assertTrue(np.allclose(V, stata_vcov))
        self.assertTrue(dof == stata_dof)

if __name__=='__main__':
    unittest.main()