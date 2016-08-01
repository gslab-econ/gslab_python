*! mixlbeta 1.0.1 18Oct2010
*! author arh

program define mixlbeta
	version 9.2

	syntax varlist [if] [in], SAVing(string) [NREP(integer 50) BURN(integer 15) REPLACE]

	if ("`e(cmd)'" != "mixlogit") error 301

	** Mark the prediction sample **
	marksample touse
	markout `touse' `e(depvar)' `e(indepvars)' `e(group)' `e(id)'

	** Mark groups with no chosen alternatives due to missing data **
	tempvar cho
	sort `e(group)'
	qui by `e(group)': egen `cho' = sum(`e(depvar)'*`touse') 
	qui replace `cho' = . if `cho' == 0  
	markout `touse' `cho'
	
	** Drop data not in prediction sample **
	preserve
	qui keep if `touse'

	** Generate individual id **
	if ("`e(id)'" != "") {
		tempvar nchoice pid
		sort `e(group)'
		by `e(group)': gen `nchoice' = cond(_n==_N,1,0)
		sort `e(id)'
		by `e(id)': egen `pid' = sum(`nchoice')		
		qui duplicates report `e(id)'
		local np = r(unique_value)
		mata: mixl_np = st_numscalar("r(unique_value)")
		mata: mixl_T = st_data(., st_local("pid"))
	}
	else {
		tempvar id
		clonevar `id' = `e(group)' 
		qui duplicates report `e(group)'
		local np = r(unique_value)
		mata: mixl_np = st_numscalar("r(unique_value)")
		mata: mixl_T = J(st_nobs(),1,1)
	}

	** Generate dummy for last obs for each decision-maker **
	tempvar last
	if ("`e(id)'" != "") {
		by `e(id)': gen `last' = cond(_n==_N,1,0)
	}
	else {
		by `e(group)': gen `last' = cond(_n==_N,1,0)
	}

	** Generate choice occasion id **
	tempvar csid
	sort `e(group)'
	by `e(group)': egen `csid' = sum(1)
	qui duplicates report `e(group)'
	local nobs = r(unique_value)

	** Sort data **
	sort `e(id)' `e(group)'

	** Set Mata matrices to be used in prediction routine **
	local rhs `e(indepvars)'
	local lhs `e(depvar)'
	if ("`e(id)'" != "") local id `e(id)'
	else local id `e(group)'
	mata: mixl_X = st_data(., tokens(st_local("rhs")))
	mata: mixl_Y = st_data(., st_local("lhs"))
	mata: mixl_CSID = st_data(., st_local("csid"))
	mata: mixl_ID = st_data(., st_local("id"), st_local("last"))

	** Create dataset containing beta estimates **
	drop _all
	qui set obs `np'
	qui gen double `id' = .
	foreach var of local rhs {
		qui gen double `var' = .
	} 
	mata: st_store(., st_local("id"), mixl_ID)
	mata: st_view(mixl_PB=., ., tokens(st_local("rhs")))
	
	tempname b
	matrix `b' = e(b)	
	mata: mixl_beta("`b'")

	keep `id' `varlist'

	if ("`replace'" != "") save "`saving'", replace
	else save "`saving'"
	
	** Restore data **
	restore
end

version 9.2
mata: 
function mixl_beta(string scalar B_s)
{
	external mixl_X
	external mixl_Y
	external mixl_T
	external mixl_CSID
	external mixl_PB
	external mixl_np

	np = mixl_np
	nrep = strtoreal(st_local("nrep"))
	kfix = st_numscalar("e(kfix)")
	krnd = st_numscalar("e(krnd)")
	krln = st_numscalar("e(krln)")
	burn = strtoreal(st_local("burn"))
	corr = st_numscalar("e(corr)")

	B = st_matrix(B_s)'

	kall = kfix + krnd

	if (kfix > 0) {
		MFIX = B[|1,1\kfix,1|]
		MFIX = MFIX :* J(kfix,nrep,1)	
	}

	MRND = B[|(kfix+1),1\kall,1|]

	if (corr == 1) {
		ncho = st_numscalar("e(k_aux)")
		SRND = invvech(B[|(kall+1),1\(kall+ncho),1|]) :* lowertriangle(J(krnd,krnd,1))
	}
	else {
		SRND = diag(B[|(kall+1),1\(kfix+2*krnd),1|])
	}

	P = J(np,1,0)

	i = 1
	for (n=1; n<=np; n++) {
		ERR = invnormal(halton(nrep,krnd,(1+burn+nrep*(n-1)))')
		if (kfix > 0) BETA = MFIX \ (MRND :+ (SRND*ERR))
		else BETA = MRND :+ (SRND*ERR)
		if (krln > 0) {
			if ((kall-krln) > 0) { 
				BETA = BETA[|1,1\(kall-krln),nrep|]\exp(BETA[|(kall-krln+1),1\kall,nrep|])
			}
			else {
				BETA = exp(BETA)
			}
		}
		R = J(1,nrep,1)

		t = 1
		nc = mixl_T[i,1]
		for (t=1; t<=nc; t++) {
			YMAT = mixl_Y[|i,1\(i+mixl_CSID[i,1]-1),cols(mixl_Y)|]
			XMAT = mixl_X[|i,1\(i+mixl_CSID[i,1]-1),cols(mixl_X)|]
			EV = exp(XMAT*BETA)
			EV = (EV :/ colsum(EV))	
			R = R :* colsum(YMAT :* EV)
			i = i + mixl_CSID[i,1]
		}
		P[n,1] = mean(R',1)
		mixl_PB[n,.] = mean((R :* BETA)',1) / P[n,1]
	}	
}
end	

exit

