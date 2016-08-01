*! version 1.0.0 24May2009 roywada@hotmail.com
*! calculates RMSE (Root MSE)

program define rmse, rclass
	version 7.0
	syntax varlist(min=2 numeric) [if] [in] [, ESTimates df_m(numlist max=1 integer) raw]
	
	if "`raw'"=="raw" {
		* do not subtract one
		local _one 0
	}
	else {
		local _one 1
	}
	
	if "`estimates'"=="estimates" {
		if "`df_m'"~="" {
			noi di in red "cannot specify both {opt est:imates} and {opt df_m}"
			exit 198
		}
		else {
			* adjust if statement
			if "`if'"=="" {
				local if `"if e(sample)==1"'
			}
			else {
				local if `"`if' & e(sample)==1"'
			}
		}
	}
	
	tempvar touse
	mark `touse' `if' `in'
	
	gettoken primary secondary : varlist
	local thisMany : word count `secondary'
	
	forval num=1/`thisMany' {
		local thisVar : word `num' of `secondary'
		tempvar resid2
		qui gen double `resid2'=(`primary'-`thisVar')^2 if `touse'==1
		qui sum `resid2'  if `touse'==1, meanonly
		
		if "`estimates'"=="estimates" {
			* current regression
			if `thisMany'>1 {
				di "`thisVar'" _col(15) _c
			}
			di (r(mean)*e(N)/(e(N)-e(df_m)-`_one'))^.5
			return local `thisVar' `=(r(mean)*e(N)/(e(N)-e(df_m)-`_one'))^.5'
		}
		else {
			if "`df_m'"~= "" {
				* hand adjusted
			}
			else {
				* no adjustment
				local df_m 0
			}
			
			if `thisMany'>1 {
				di "`thisVar'" _col(15) _c
			}
			
			di (r(mean)*r(N)/(r(N)-`df_m'-`_one'))^.5
			return local `thisVar' `=(r(mean)*r(N)/(r(N)-`df_m'-`_one'))^.5'
			
		}
		drop `resid2'
	}
end
exit


