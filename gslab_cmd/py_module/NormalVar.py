

## Note that Q function does not have a leading negative as some references do.
##
## paramfunction takes the parameters of interest (mean, variance) of a normal random variable
## and converts them to first and second moments
##
## self.stats should be the first and second sample moments (uncentered).

from __future__ import division
import numpy as np
from CMD import *

class CMD_normalvar(CMD):
    
    def paramfunction(self, params):  
        firstmoment  = params[0]
        secondmoment = firstmoment ** 2 + params[1]
        return np.matrix([[firstmoment], [secondmoment]])







