##  Implements functions that are needed in ConsumptionModel class, but do not solve problems
##  unique to consumption models.
##

import numpy as np

## Finds the location in the array that contains the value closest to x
def approxloc(x, array):
   return (np.abs(array - x)).argmin() 
        
