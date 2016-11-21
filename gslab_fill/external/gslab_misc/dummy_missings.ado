/***************************************************************
 *
 * DUMMY_MISSINGS.ADO: Create dummy variables for missing values
 *   in a set of variables; recode missing values of those
 *   variables to user-specified value (e.g., -1); return a local
 *   variable with a list of the missing variable dummy names.
 *
 *   Missval must be specified.  Prefix is optional, and its
 *   default value is "mis_".  Prompt "display "`r(newdummies)'""
 *   in order to view a list of the missing variable dummy names.
 *   
 *   Date: 7/30/09
 *   Creators: Pat DeJarnette, Yao Lu
 *
 **************************************************************/

program define dummy_missings, rclass
 
	version 10
	syntax varlist, missval(integer) [prefix(string)]
	
	if "`prefix'" == "" {
		local prefix "mis_"
	}
	
	quietly: describe, varlist
	local temp "`r(varlist)'"
	foreach value of local temp {
		foreach var of varlist `varlist' {
			if "`value'" == "`prefix'`var'" {
				display "ERROR: Variable `prefix'`var' already exists, but dummy_missings wants to define it. Change prefix or drop `prefix'`var'."
				exit(-2)
			}
		}
	}
	
	local local ""
	mvencode `varlist', mv(`missval')
	foreach var of varlist `varlist' {
		gen `prefix'`var' = `var'==`missval'
		local local "`local' `prefix'`var'"
	}

	return local newdummies "`local'"
		
end
