##  Implements a simple Consumption Model using the abstract class ConsumptionModel. Also, implements a
##  analytic solution. ETP.analytic_solution gives the exact analytic solution to the consumption problem
##  assuming no income.


from __future__ import division
import ConsumptionModel as CM
import numpy as np
import ErrorCalls

class ETP(CM.ConsumptionModel):

    def __init__(self,
            init_wealth     = 5, 
            income_vec      = np.zeros(5),
            horizon         = 5, 
            R               = 1.08, 
            delta           = 1 / (1 + .06), 
            BequestValue    = 0, 
            rho             = .8,
            error_checks    = "on"):
        super(ETP, self).__init__()
        self.init_wealth            = init_wealth
        self.income_vec             = income_vec
        self.horizon                = int(horizon)
        self.R                      = R
        self.delta                  = delta
        self.BequestValue           = BequestValue
        self.rho                    = rho
        self.consumption_path       = 0
        self.analytic_consumption   = 0
        self.error_checks           = error_checks
        
        if self.error_checks == "on":
            if len(self.income_vec) != self.horizon:
                raise ErrorCalls.IncomeVecError()
            if self.rho < 0:
                raise ErrorCalls.UtilityError()
            if self.rho > 1:
                raise ErrorCalls.UtilityError()
            if init_wealth < 0:
                raise ErrorCalls.InitWealthError()
            if horizon < 0:
                raise ErrorCalls.HorizonError()
    
    def utility(self, c): 
        if self.rho == 1:
            if c == 0:
                return -999999
            else:
                return np.log(c)
        else:
            if c == 0:
                return 0
            else:
                return (c ** (1 - self.rho)) / (1 - self.rho )

    ## Obtains analytic solution. Does not require running Bellman Grid Solve beforehand.
    def analytic_solution(self):
        ## Assumes no income.
        self.analytic_consumption = np.zeros(self.horizon)
        temp = 0
        for j in range(self.horizon):
            temp = temp + (self.R ** (- (j + 1)) * (self.delta * self.R) ** (j / self.rho))
        self.analytic_consumption[0] = self.init_wealth / temp
        for i in range(1, self.horizon):
            self.analytic_consumption[i] = self.analytic_consumption[i - 1] * (self.delta * self.R) ** (1 / self.rho)
        return self.analytic_consumption
        
    def print_parameters(self):
        init_wealth     = 'Initial Wealth = ' + str(self.init_wealth) + "; " 
        income_vec      = 'Income = ' + str(self.income_vec) + "; " 
        horizon         = 'Horizon = ' + str(self.horizon) + "; " 
        R               = 'Interest = ' + str(self.R) + "; " 
        delta           = 'Discount Factor = ' + str(self.delta) + "; " 
        rho             = 'Risk Aversion = ' + str(self.rho)
        text            = init_wealth + income_vec + horizon + R + delta + rho
        return text
        