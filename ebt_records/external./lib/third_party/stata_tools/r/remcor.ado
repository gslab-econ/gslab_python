*! version 2.0.0 26jul2001   (TSJ-2: st0005)
program define remcor
	version 6.0
	* takes b and transform set of r.effs at same level using choleski
	* returns bi where the r.effs are independent and correlation equations
	* have been removed
	* also takes exponential of sd parameters
	* and evaluates contributions to linear predictor that don't change
	args b

	tempname b2 s1 cov t r d dd u denom mean mzps
	tempvar junk
	gen double `junk'=0
	global HG_error=0

	disp  "*********in remcor:"

	/* fixed effects $HG_xb1, $HG_xb2 etc. (tempnames stored in global macros-list) */
	disp "fixed parameters: "
	matrix list `b'
	if $HG_const==1{
		matrix `b2' = `b'*M_T' + M_a
		matrix coleq `b2' = $HG_cole
		matrix colnames `b2' = $HG_coln
		matrix list `b2'
	}
	else{
     		matrix `b2' = `b'
	}
	local nffold=0
	local ff = 1
	local nxt = 1
	while(`ff' <= $HG_tpff){
		matrix `b2' = `b2'[1, `nxt'...]
		local np = M_nffc[1, `ff'] - `nffold'
		disp "np = " `np'
		if `np'>0{
			local nxt = `np' + 1
			local nffold = M_nffc[1,`ff']
			matrix `s1' = `b2'[1,1..`np']
			matrix list `s1'
			disp "tempname: ${HG_xb`ff'}"
			matrix score double ${HG_xb`ff'} = `s1' /* nontemp */
		}
		else{
			qui gen double ${HG_xb`ff'} = 0
		}
		disp ${HG_xb`ff'}[$which]
		local ff=`ff'+1
	}
	if "$HG_off"~=""{qui replace $HG_xb1=$HG_xb1+$HG_off}
	disp "HG_xb1 = " $HG_xb1[$which]

	/* random effects */
/* level 1 */
	local np = M_nbrf[1,1]
	if `np'>0{
		matrix `b2' = `b2'[1, `nxt'...]
		local nxt = 1
		matrix `s1' = `b2'[1,1..`np']
		matrix list `s1'
		matrix score double $HG_s1 = `s1'
		qui replace $HG_s1=exp($HG_s1)		
		disp "s1 = $HG_s1 = " $HG_s1[$which]
		local nxt = `nxt' + `np'
	}
	local lev = 2
	local rf = 2
	local nrfold = M_nrfc[2,1]
	
/* MASS POINTS */
if($HG_free){
	while(`lev'<=$HG_tplv&`rf'<=$HG_tprf){
		local j1 = M_nrfc[2, `lev']
		local nrf = `j1' - `nrfold'
		local nip = M_nip[1, `lev']
		scalar `denom' = 1 /* =exp(0) */
		matrix M_zps`lev' = J(1,`nip',`denom')
		local k = 1
		disp "`nip' integration points at level `lev'"
		local nloc = `nip'
		if $HG_cip|`nip'>1{ local nloc = `nloc'-1}
		while `k' <= `nloc' {
			local j = `nrfold'+1
			while `j'<=`j1'{
				disp "level `lev', class `k' and random effect `j'"
				disp " nxt = " `nxt'
				matrix `b2' = `b2'[1, `nxt'...]
				matrix list `b2'
				local nxt = 1
				if `k'==1{
					/* linear predictors come before first masspoint */
					local np = M_nbrf[1,`j']-1
					if `np'>0 {
						disp "extracting coefficients for r.eff"
						matrix `s1' = `b2'[1,1..`np']
						matrix score double ${HG_s`j'} = `s1'
						disp "HG_s`j' = ${HG_s`j'} = " ${HG_s`j'}[$which]
						local nxt = `nxt' + `np'
					}
					/* first coeff fixed at one */
					matrix `s1' = (1)
					local lab: colnames `b2'
					local lab: word `nxt' of `lab'
					matrix colnames `s1'=`lab'
					matrix list `s1'
					capture drop `junk'
					matrix score double `junk' = `s1'
					if `np'>0{
						qui replace ${HG_s`j'}=${HG_s`j'}+`junk'
					}
					else{
						qui gen double ${HG_s`j'}=`junk'
					}
					matrix list `s1'
					disp "HG_s`j' = ${HG_s`j'} = " ${HG_s`j'}[$which]
					disp "making M_zlc`j'"
					matrix M_zlc`j' = J(1,`nip',0)
				}
				matrix M_zlc`j'[1,`k'] = `b2'[1,`nxt']
				local nxt = `nxt' + 1
				local j = `j' + 1
			}
			if `k'<`nip'{
				scalar `mzps' = exp(`b2'[1,`nxt'])
				if `mzps' == . {
					global HG_error=1
					exit
				}
				matrix M_zps`lev'[1,`k'] = `mzps'
				local nxt = `nxt' + 1
				scalar `denom' = `denom' + M_zps`lev'[1,`k']
			}
			local k = `k' + 1
		}

		local k = 1
		while `k' <= `nip'{
			scalar `mzps' = M_zps`lev'[1,`k']
			matrix M_zps`lev'[1,`k'] = `mzps'/`denom'
			local k = `k' + 1
		}
		local j = `nrfold' + 1
		while `j' <= `j1'{ /* define last location */
			if $HG_cip == 1{
				matrix `mean' = M_zps`lev'*M_zlc`j'' /* mean of all but last point */
				scalar `mzps' = M_zps`lev'[1,`nip']
				matrix M_zlc`j'[1,`nip'] = -`mean'[1,1]/`mzps'
			}
			else if `nip'>1{
				matrix M_zlc`j'[1,`nip'] = `b2'[1,`nxt']
				local nxt = `nxt' + 1
			}
			disp "M_zlc`j'"
			matrix list M_zlc`j'
			local j = `j' + 1
		}
		disp "M_zpz`lev'"
		matrix list M_zps`lev'
		local nrfold = `j1'
		local lev = `lev' + 1
	}
}/*endif HG_free */
else{
/* ST. DEVS */
	disp "random parameters: "
	if $HG_tprf>1{matrix CHmat = J($HG_tprf-1,$HG_tprf-1,0)}
	while(`lev'<=$HG_tplv&`rf'<=$HG_tprf){
		local np = M_nbrf[1,`rf']
		disp "np = " `np'
		local nrf = M_nrfc[2, `lev'] - `nrfold'
		matrix `t' = J(`nrf',`nrf',0)
		local i = 1
		while (`i' <= `nrf'){ 
			disp " nxt = " `nxt'
			matrix `b2' = `b2'[1, `nxt'...]
			local nxt = 1
			matrix list `b2'
			local np = M_nbrf[1, `rf'] - 1
			disp `np' " loadings at random effect " `rf' ", level " `lev'
			if `np'>0{
				matrix `s1' = `b2'[1,1..`np']
/*
				* fudge: exponentiate s1
				local ij = 1
				while `ij'<=`np'{
					matrix `s1'[1,`ij'] = exp(`s1'[1,`ij'])
					local ij = `ij' + 1
				}
				* end fudge
*/

				matrix list `s1'
				matrix score double ${HG_s`rf'} = `s1'
				local nxt = `nxt' + `np'
			}
			/* first (single non-) loading fixed at one, label in st. dev */
			matrix `s1' = (1)
			local lab: colnames `b2'
			local lab: word `nxt' of `lab'
			matrix colnames `s1' = `lab'
			capture drop `junk'
			matrix score double `junk' = `s1'
			if `np'>0{
				qui replace ${HG_s`rf'} = ${HG_s`rf'} + `junk'
			}
			else{
				matrix score double ${HG_s`rf'} = `s1'
			}

			disp "HG_s`rf' = ${HG_s`rf'} = " ${HG_s`rf'}[$which]
			* extract standard deviation
			* fudge: take exponential
			* matrix `t'[`i',`i'] = exp(`b2'[1, `nxt'])
			matrix `t'[`i',`i'] = `b2'[1, `nxt']
			matrix CHmat[`rf'-1,`rf'-1]=`t'[`i',`i']
			local nxt = `nxt' + 1
			local i = `i' + 1
			local rf = `rf' + 1
		}
		if (`nrf'>1&$HG_cor==1){ /* deal with correlations */
			/* extract correlation parameters */
			local i = 2
			while (`i' <= `nrf'){
				local k = `i' + `nrfold' - 1	
				local j = 1
				while (`j' < `i'){
					local l = `j' + `nrfold' - 1
					disp "i = " `i' " j = " `j' " nxt = " `nxt'
					matrix `t'[`i',`j'] = `b2'[1,`nxt']
					matrix CHmat[`k',`l'] =  `t'[`i',`j']
					local j = `j' + 1
					local nxt = `nxt' + 1
				}
				local i = `i' + 1
			}
		}
		matrix list `t'
		matrix M_chol = `t'
		/* unpacked parameters */
		local nrfold = M_nrfc[2,`lev']
		local lev = `lev' + 1
	} /* loop through levels */
}/*endelse HG_free */
local nrfold = M_nrfc[2,1]
/* use B-matrix */
if $HG_tprf>1&$HG_bmat==1{
	disp "dealing with B-matrix"
	local i = 1
	matrix Bmat = J($HG_tprf-1,$HG_tprf-1,0)
	while `i'<$HG_tprf{
		local j = 1
		while `j' < $HG_tprf{
			if M_b[`i',`j']>0{
				matrix Bmat[`i',`j']=`b2'[1,`nxt']
				local nxt = `nxt' + 1
			}
			local j = `j' + 1
		}
		local i = `i' + 1
	}
	matrix list Bmat

/* only works if B-matrix is upper diagonal */
	local i=2
	while `i'<$HG_tprf{
		local k = `i' + `nrfold'
		local j = 1
		disp "making s`k'"
		while `j'<`i'{
			local l = `j' + `nrfold'
			qui replace ${HG_s`k'} = ${HG_s`k'} + Bmat[`j',`i']*${HG_s`l'}
			disp "     adding Bmat[`j',`i']s`l'"
			local j = `j' + 1
		}
		local i =  `i' + 1
	}
}

/* deal with geqs */


if $HG_ngeqs>0{
disp "dealing with geqs"
	local i = 1
	while `i'<=$HG_ngeqs{
		local k = M_ngeqs[1,`i']
		local n = M_ngeqs[2,`i']
		disp "random effect `k' has `n' covariates"
		local nxt2 = `nxt'+`n'-1
		matrix `s1' = `b2'[1,`nxt'..`nxt2']
		matrix list `s1'
		local nxt = `nxt2' + 1
		capture drop `junk'
		matrix score double `junk' = `s1'
		disp "multiply " `junk'[$which] " by HG_s`k' and add to HG_xb1"
		qui replace $HG_xb1 = $HG_xb1 + `junk'*${HG_s`k'}
		disp "HG_xb1:" $HG_xb1[$which]
		local i = `i' + 1
	}
}

/* use inter */

if $HG_inter~=0{
	local k = $HG_l + 1
	local j = $HG_r + 1
	disp "HG_s`k' = HG_s`k'*HG_s`j'
	qui replace ${HG_s`k'} = ${HG_s`k'}*${HG_s`j'}
}

/* use CHmat */
if $HG_free==0&$HG_tprf>1{
	disp "dealing with Cholesky matrix"
	matrix list CHmat
	local i = 1
	while (`i'<$HG_tprf){
		local k = `i' + `nrfold'
		qui replace `junk'=0
		local j = `i'
		disp "making s`k'"
		while `j'<$HG_tprf{
			local l = `j' + `nrfold'
			qui replace `junk' = `junk' + CHmat[`j',`i']*${HG_s`l'}
			disp "     adding CHmat[`j',`i']s`l'"
			local j = `j' + 1
		}
		qui replace ${HG_s`k'}=`junk'
		disp "s`k' = ${HG_s`k'} = " ${HG_s`k'}[$which]
		local i =  `i' + 1
	}
}

* label M_znow
local i=2
local lab 
while `i'<=$HG_tprf{
	local lab "`lab' ${HG_s`i'}"
	local i = `i' + 1
}
matrix colnames M_znow=`lab'
disp "M_znow:"
matrix list M_znow	
end

