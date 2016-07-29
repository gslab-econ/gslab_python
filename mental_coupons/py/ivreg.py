import numpy as np
import scipy.linalg as alg

def tsls(endog=None, inst=None, depvar=None, exog=None):
    Z = np.hstack([exog, inst])
    X_HAT = Z.dot(alg.solve(Z.T.dot(Z), Z.T.dot(endog)))
    X = np.hstack([endog, exog])
    X_SS = np.hstack([X_HAT, exog]) 
    beta = alg.solve(X_SS.T.dot(X_SS), X_SS.T.dot(depvar))

    eps = depvar-X.dot(beta)
    dof = X_SS.shape[0] - X_SS.shape[1]
    sse = eps.T.dot(eps)[0,0]
    V = (sse/dof)*alg.inv(X_SS.T.dot(X_SS))

    return (beta, V, dof)