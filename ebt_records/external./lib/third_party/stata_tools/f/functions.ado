*!version 3.1  12Mar2014

capture mata mata drop rdvce()
mata
real matrix rdvce(real matrix X, real matrix y, real matrix z, real scalar p, real scalar h, real scalar matches, string vce, string kernel)
{
m = matches+1
n = length(X)
p1 = p+1
if (vce=="resid") {
XX       = J(n,p1,.)
mu0_phat_y = J(n,1, .)
mu0_phat_z = J(n,1, .)
sigma    = J(n,1, .)
	for (k=1; k<=n; k++) {
		cutoff = J(n,1, X[k])
		cutoff1 = X[k]
		for (j=1; j<=p1; j++) {
			XX[.,j] = (X-cutoff):^(j-1)
		}
	W = kweight(X,cutoff1,h,"kernel")
	m_p_y = invsym(cross(XX,W,XX))*cross(XX,W,y)
	m_p_z = invsym(cross(XX,W,XX))*cross(XX,W,z)
	mu0_phat_y[k] = m_p_y[1]
	mu0_phat_z[k] = m_p_z[1]
	sigma[k] = (y[k] - mu0_phat_y[k])*(z[k] - mu0_phat_z[k])
	}
}
else  {
v = w = 0
y_match_avg = J(n, 1, .)
z_match_avg = J(n, 1, .)
for (k=1; k<=n; k++) {
	diffx = abs(X :- X[k,1])
	match = minindex(diffx, m, v, w)
	ind=v[2::length(v),.]
	y_match_avg[k,1] = mean(y[ind])
	z_match_avg[k,1] = mean(z[ind])
	}
sigma = (m/(m+1))*(y :- y_match_avg):*(z :- z_match_avg)
}

return(sigma)
}
mata mosave rdvce(), replace
end



capture mata mata drop kweight()
mata
real matrix kweight(real matrix X, real scalar c, real scalar h, string kernel)
{
u = (X:-c)/h
	if (kernel=="epanechnikov" | kernel=="epa") {
	w = (0.75:*(1:-u:^2):*(abs(u):<=1))/h
	}
	else if (kernel=="uniform" | kernel=="uni") {
	w = (0.5:*(abs(u):<=1))/h
	}
	else {
	w = ((1:-abs(u)):*(abs(u):<=1))/h
	}
	
return(w)	
}
mata mosave kweight(), replace
end



capture mata mata drop bwconst()
mata
real matrix bwconst(real scalar p, real scalar v, string kernel)
{
n_sim = 10000
rseed(13579)
u_sim = runiform(n_sim,1)
p1 = p+1
Gamma_p  = J(p1,p1, .)
Omega_pq = J(p1,1, .)
Phi_p    = J(p1,p1, .)
if (kernel=="epanechnikov" | kernel=="epa") {
K = (0.75*(1:-u_sim:^2):*(abs(u_sim):<=1))
}
else if (kernel=="uniform" | kernel=="uni") {
K = (0.5:*(abs(u_sim):<=1))
}
else  {
K = ((1:-abs(u_sim)):*(abs(u_sim):<=1))
}
for (i=1; i<=p1; i++) {
	Omega_pq[i] = mean(K:*(u_sim:^(p1)):*(u_sim:^(i-1)))
	for (j=1; j<=p1; j++) {
	Gamma_p[i,j] = mean(K:*(u_sim:^(i-1)):*(u_sim:^(j-1)))
	Phi_p[i,j] = mean((K:^2):*(u_sim:^(i-1)):*(u_sim:^(j-1)))
	}
}
B_const = invsym(Gamma_p)*Omega_pq
V_const = invsym(Gamma_p)*Phi_p*invsym(Gamma_p)
C1 = B_const[v+1,1]
C2 = V_const[v+1,v+1]
return(C1,C2)
}
mata mosave bwconst(), replace
end


*******************************************
capture mata mata drop regconst()
mata
real matrix regconst(real scalar d, real scalar h)
{
d2 = 2*d+1
d1 = d+1
mu = J(d2, 1, 0)
mu[1] = 1
XX = J(d1,d1,0)
for (j=2; j<=d2; j++) {
i = j-1
	if (mod(j,2)==1) {
		mu[j] = (1/(i+1))*(h/2)^i
	}
}
for (j=1; j<=d1; j++) {
	XX[j,.] = mu[j::j+d]'
}
invXX =invsym(XX)
return(invXX)
}
mata mosave regconst(), replace
end


*******************************************
capture mata mata drop cvplot()
mata
void cvplot(
 real colvector y,
 real colvector x,
 | string scalar opts)
{
	real scalar n, N, Y, X

	n = rows(y)
	if (rows(x)!=n) _error(3200)
	N = st_nobs()
	if (N<n) st_addobs(n-N)
	st_store((1,n), Y=st_addvar("double", st_tempname()), y)
	st_store((1,n), X=st_addvar("double", st_tempname()), x)
	stata("twoway scatter " + st_varname(Y) + " " +
	 st_varname(X) + ", " + opts)
	if (N<n) st_dropobsin((N+1,n))
	st_dropvar((Y,X))
}
mata mosave cvplot(), replace
end

