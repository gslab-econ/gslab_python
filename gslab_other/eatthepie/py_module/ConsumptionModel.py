#! /usr/bin/env python

##  ConsumptionModel is the abstract base class for a broad class of consumption models. It includes 
##  a general Bellman Grid Solving technique using backwards recursion for consumption models along with the option to allow 
##  interpolation of the grid for improved accuracy. In order to implement a subclass of ConsumptionModel,
##  the only required method is to implement a utility function (see eatthepie for an example). This utility
##  function can take one input (consumption) and should ouput the utility from the given consumption.
##  Also includes plotting capabilities.
##
##


from __future__ import division
from abc import ABCMeta, abstractmethod
import numpy as np
import pylab as pl
from scipy.interpolate import *
from MiscFunctions import *
import ErrorCalls
import scipy.optimize

import multiprocessing as mp
from numba import jit

class ConsumptionModel(object):

    __metaclass__ = ABCMeta

    def __init__(self, 
            init_wealth     = 5, 
            income_vec      = np.zeros(5),
            horizon         = 5, 
            R               = 1.08, 
            delta           = 1 / (1 + .06), 
            BequestValue    = 0
            ):
        self.init_wealth            = init_wealth
        self.income_vec             = income_vec
        self.horizon                = int(horizon)
        self.R                      = R
        self.delta                  = delta
        self.BequestValue           = BequestValue
        self.consumption_path       = 0
        self.analytic_consumption   = 0
        if len(self.income_vec) != self.horizon:
            raise ErrorCalls.IncomeVecError()
        if init_wealth <= 0:
            raise ErrorCalls.InitWealthError()
        if horizon < 0:
            raise ErrorCalls.HorizonError()
    
    def BellmanGridSolve(self, gridmesh = .005, interp_method = "linear"):
        income_wealth = 0
        for j in range(self.horizon):
            income_wealth = income_wealth + ((self.R ** (self.horizon - j)) * self.income_vec[j])
        maxW = (self.R ** self.horizon) * self.init_wealth + income_wealth
        maxC = maxW 
        Gw = np.arange(0, maxW + 2 * gridmesh, gridmesh)
        Gc = np.arange(0, maxC + 2 * gridmesh, gridmesh)
        Value = np.zeros((self.horizon + 1, len(Gw)))
        Value[self.horizon, ] = self.BequestValue * Gw
        Consumption = np.zeros((self.horizon, len(Gw)))
        temp_value = np.zeros((len(Gc)))
        utility = np.zeros(len(Gc))
        for k in range(len(Gc)):
            utility[k] = self.utility(Gc[k])  ## precompute utility for consumption grid
                        
        if interp_method == "none":
            ## Backwards induction
            for t in np.arange(self.horizon - 1, -1, -1):
                for i in range(len(Gw)):
                    for j in range(len(Gc)):
                        temp_w = self.R * (Gw[i] - Gc[j] + self.income_vec[t])
                        if temp_w < 0:
                            break ## Can't go in debt
                        if temp_w < maxW:
                            temp_w_loc = approxloc(temp_w, Gw)
                            temp_value[j] = utility[j] + self.delta * Value[t + 1, temp_w_loc]
                    Value[t, i] = max(temp_value)
                    Consumption[t, i] = Gc[approxloc(Value[t, i], temp_value)]
                    temp_value = np.zeros((len(Gc)))
        
        else: 
        ## Uses interpolation to improve accuracy
            ## Backwards induction
            for t in np.arange(self.horizon - 1, -1, -1):
                value_interp = interp1d(Gw, Value[t + 1, ], kind = interp_method)
                for i in range(len(Gw)):
                    for j in range(len(Gc)):
                        temp_w = self.R * (Gw[i] - Gc[j] + self.income_vec[t])                    
                        if temp_w < 0:
                            break ## Can't go in debt
                        if temp_w < maxW:
                            temp_value[j] = utility[j] + self.delta * value_interp(temp_w)
                    if j > 1:         
                        interp_temp_negvalue = Akima1DInterpolator(Gc[0:j], -temp_value[0:j])
                        optim = scipy.optimize.minimize(interp_temp_negvalue, [0], method = "Nelder-Mead")
                        Value[t, i] = -optim.fun
                        Consumption[t, i] = optim.x[0]
                    else: 
                        Value[t, i] = temp_value[0]                        
                        Consumption[t, i] = 0
        
        ## Starting with initial wealth and creating optimal path
        wealth = self.R * (self.init_wealth + self.income_vec[0])
        final_consumption = np.zeros(self.horizon)
        for t in range(self.horizon):
            if interp_method == "none":
                wealth_loc = approxloc(wealth, Gw)
                final_consumption[t] = Consumption[t, wealth_loc]
            else:
                consum_interp = interp1d(Gw, Consumption[t, ], kind = interp_method, bounds_error = False, fill_value = 0)
                final_consumption[t] = consum_interp(wealth)
            if t < (self.horizon - 1):
                wealth = self.R * (wealth - final_consumption[t] + self.income_vec[t + 1])
                
        self.consumption_path = final_consumption
        return final_consumption    
        
    def plot(self, 
             analytic = "none", 
             show = "on", 
             legend_loc = "lower right", 
             title = "Consumption Model", 
             xlab = "Time", 
             ylab = "Consumption"
             ):
        if show != "on":
            pl.ioff()
       
        xlength = len(self.consumption_path)
        x = np.arange(1, xlength + 1)
        if analytic == "none":
            pl.plot(x, self.consumption_path, '-')
        else:
            self.analytic_solution()
            pl.plot(x, self.consumption_path, linestyle = '-', label = "Numerical Solution")
            pl.plot(x, self.analytic_consumption, linestyle =  '--', label = "Analytic Solution")
            pl.legend(("Numerical Solution", "Analytic Solution"), loc = legend_loc)
        pl.xlabel(xlab)
        pl.ylabel(ylab)
        pl.title(title)
            
    @abstractmethod
    def utility():
        pass

    @abstractmethod
    def analytic_solution():
        pass

    @abstractmethod
    def print_parameters():
        pass







        
        
