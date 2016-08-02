#! /usr/bin/env python

## Note that Q function does not have a leading negative as some references do.
## paramfunction should return an nx1 vector in all subclasses.
##
##

from __future__ import division
from abc import ABCMeta, abstractmethod
from Misc import *
import ErrorCalls
from scipy.optimize import *
import numpy as np

class CMD(object):

    __metaclass__ = ABCMeta
    
    def __init__(self, W, stats): 
        self.W       = np.matrix(W)
        self.stats   = np.matrix(stats)
        self.n       = len(self.stats)
        
        if isPSD(W) != True:
            raise ErrorCalls.WError()
        if np.shape(self.W[:, 0]) != np.shape(self.stats): ## If W is n x n, then stats must be n x 1. 
            raise ErrorCalls.statsError()
    
    def estimate(self, init, tol = .00001, method = "Nelder-Mead", bounds = "none"): # Q function does not have the leading negative. Hence, minimize.
        if bounds == "none":        
            results = minimize(self.Q, init, tol = tol, method = method)
        else:
            results = minimize(self.Q, init, tol = tol, bounds = bounds, method = method)
        self.parameter_estimates = results.x
        return(results)
    
    def Q(self, theta):    # Does not have the leading negative as some references do.
        paramfunction_theta = np.matrix(self.paramfunction(theta))
        dist                = self.stats - paramfunction_theta
        temp                = (np.transpose(dist)) * self.W * dist
        return(temp)
        
    @abstractmethod
    def paramfunction(self, params):
        pass



