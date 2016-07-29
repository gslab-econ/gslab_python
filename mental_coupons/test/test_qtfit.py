import unittest
import numpy as np
import pandas as pd
import pyqt_fit.kernels as kernels
import pyqt_fit.npr_methods as npmeth
import pyqt_fit.nonparam_regression as npreg

class test(unittest.TestCase):

    def setup_tests(self, degree):
        test_input = pd.read_csv('../temp/lpoly_test_input.csv')

        bwpath = '../temp/bandwidths_degree{}.txt'.format(degree)
        bwidths = pd.read_table(bwpath, header = None, index_col = 0)

        lpoly = npreg.NonParamRegression(
                    test_input['length'].values.astype(np.float64),
                    test_input['weight'].values.astype(np.float64),
                    bandwidth = bwidths.ix['epanechnikov',:].values[0],
                    kernel = kernels.Epanechnikov(),
                    method = npmeth.LocalPolynomialKernel(q=degree)
                )
        qtfit_epanechnikov = lpoly.evaluate(test_input['length'].values.astype(np.float64))
        
        lpoly = npreg.NonParamRegression(
                    test_input['length'].values.astype(np.float64),
                    test_input['weight'].values.astype(np.float64),
                    bandwidth = bwidths.ix['gaussian',:].values[0],
                    kernel = kernels.normal_kernel(1),
                    method = npmeth.LocalPolynomialKernel(q=degree)
                )
        qtfit_gaussian = lpoly.evaluate(test_input['length'].values.astype(np.float64))
        return {'epanechnikov' : qtfit_epanechnikov, 'gaussian' : qtfit_gaussian}

    def test_gaussian_kernel(self):
        for degree in [0, 1, 2, 3]:
            qtfit_values = self.setup_tests(degree)
        
            N = qtfit_values['gaussian'].size
            stata_values = pd.read_csv('../temp/stata_lpoly_degree{}.csv'.format(degree))
            stata_gaussian = stata_values['gaussian'].values.reshape(N,)

            self.assertTrue(np.allclose(qtfit_values['gaussian'], stata_gaussian))

    def test_epanechnikov_kernel(self):
        for degree in [2, 3]:
            qtfit_values = self.setup_tests(degree)
        
            N = qtfit_values['epanechnikov'].size
            stata_values = pd.read_csv('../temp/stata_lpoly_degree{}.csv'.format(degree))
            stata_epanechnikov = stata_values['epanechnikov'].values.reshape(N,)

            self.assertTrue(np.allclose(qtfit_values['epanechnikov'], stata_epanechnikov))

    def test_first_degree(self):
        test_input = pd.read_csv('../temp/lpoly_test_input.csv')

        lpoly = npreg.NonParamRegression(
                    test_input['length'].values.astype(np.float64),
                    test_input['weight'].values.astype(np.float64),
                    kernel = kernels.Epanechnikov(),
                    method = npmeth.LocalPolynomialKernel(q=1)
                )
        epanechnikov = lpoly.evaluate(test_input['length'].values.astype(np.float64))
        
        lpoly = npreg.NonParamRegression(
                    test_input['length'].values.astype(np.float64),
                    test_input['weight'].values.astype(np.float64),
                    kernel = kernels.normal_kernel(1),
                    method = npmeth.LocalPolynomialKernel(q=1)
                )
        gaussian = lpoly.evaluate(test_input['length'].values.astype(np.float64))
        self.assertTrue(np.allclose(epanechnikov, gaussian))

if __name__=='__main__':
    unittest.main()