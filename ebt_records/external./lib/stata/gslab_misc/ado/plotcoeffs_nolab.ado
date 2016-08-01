/**********************************************************
 *
 * PLOTCOEFFS_NOLAB.ADO: Plot coefficients after
 *   a regression. (No labels)
 *
 * Date: March, 2008
 * Creator: MG
 *
 **********************************************************/

cap program drop plotcoeffs_nolab

program define plotcoeffs_nolab

	version 10
	syntax varlist(ts), [bar *]

	tempvar name value stderr order
	tempname lab

	quietly gen `name' = ""
	quietly gen `value' = .
	quietly gen `stderr' = .
	quietly gen `order' = _n
	*label define `lab' 0 "xx"

	local n = 1
	foreach V of varlist `varlist' {
		quietly replace `name' = "`V'" in `n'
		quietly replace `value' = _b[`V'] in `n'
		quietly replace `stderr' = _se[`V'] in `n'
		*label define `lab' `n' "`V'", modify
		local n = `n'+1
	}

/*
	if option label() was supplied
	local n = 1
	foreach L of `labellist' {
		quietly replace `name' = "`L'" in `n'
		local n = `n'+1
	}
*/

	local max = `n'-1

	if "`options'"=="" {
		local options = "scheme(s1mono) yline(0, lcolor(gs12)) ytitle(Coefficient)"
	}

	if "`bar'"=="bar" {
		graph bar `value', over(`name', sort(`order')) `options' scale(1)
	}

	else {
		*label values `order' `lab'
		display "`xlabel'"
		serrbar `value' `stderr' `order' if `order'<=`max',  xlabel(none) xtitle(Variable) `options' scale(2)
	}

end

