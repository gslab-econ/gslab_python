#! /usr/bin/env python

##  Implements exceptions/errors that are needed in ConsumptionModel class and associated programs.
##

class Error(Exception):
    pass

class IncomeVecError(Error):
    def __init__(self):
        self.msg = "income_vec must have same length as horizon"
    def __str__(self):
        return repr(self.msg)

class UtilityError(Error):
    def __init__(self):
        self.msg = "rho must be between 0 and 1"
    def __str__(self):
        return repr(self.msg)

class InitWealthError(Error):
    def __init__(self):
        self.msg = "init_wealth must be positive"
    def __str__(self):
        return repr(self.msg)
        
class HorizonError(Error):
    def __init__(self):
        self.msg = "horizon must be positive"
    def __str__(self):
        return repr(self.msg)        
