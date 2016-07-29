##  Implements functions that are needed in CMD class, but do not solve problems
##  unique to CMD estimators.
##

import numpy as np

## checks whether a matrix A is positive semi-definite up to a certain tolerance
def isPSD(A, tol=1e-8):
    E,V = np.linalg.eigh(A)
    return np.all(E > -tol)