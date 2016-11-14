/**********************************************************
 *
 * FILLBY.ADO: Fill in missing values of variable(s) X within
 *   groups defined by variable(s) Y. Fillby requires
 *   that there be at most one non-missing value of (each) X for
 *   each value of Y. It assigns this value to all observations
 *   with the same value of Y for which (each) X is missing.
 *
 *   If using the generate option, number of fields generated 
 *   must equal the number of variables in X.  There is a 
 *   1-to-1 correspondence in the ordering.
 *
 **********************************************************/
 
cap program drop fillby
 
program define fillby

	version 10
	syntax varlist [if] [in], by(varlist) [GENerate(namelist)] [replace]
	tempvar n

	gen `n' = _n

	
	local newby = ""
	foreach byvar in `by' {
		local newby = "`newby'" + "_`byvar'"
	}
	tempvar `newby'
	egen ``newby'' = group(`by')

	* check specified either generate() or replace
	if "`generate'"=="" & "`replace'"=="" {
		disp "ERROR: You must specify either generate() or replace"
		error -1
	}
	
	*Now it checks to make sure all the fill variables have only one non-missing value.
	*It also checks to make sure the number of generate() variables = number of fill variables.
	local i 0
	foreach var in `varlist' {
		tempvar ind error
		gen `ind' = missing(`var')
		sort `by' `ind'
		
		* check no more than one non-missing value of `varlist'
		* per value of `by'
		gen `error' = `var'!=`var'[_n-1] & ``newby''==``newby''[_n-1] & `ind'==0 & `ind'[_n-1]==0
		quietly sum `error'
		if `r(max)'==1 {
			disp "ERROR: There are multiple non-missing values of `var' within the groups defined by `by'"
			sort `n'
			error -1
		}
		drop `ind' `error'
		local i = `i'+1
	}
	if "`generate'"!="" {
		local j 0
		foreach gen in `generate' {
			if "`gen'" !=""{
				local j = `j' +1
			}
		}
		if "`i'" != "`j'" {
			disp "ERROR: Generate() is neither blank nor does it match the number of variables in varlist : `varlist'"
			disp "       Generate() has `j' variables while varlist has `i' variables."
			sort `n'
			error -1
		}
	}
	
	*Now that it has checked these things,
	*replace or generate as required. 
	local i 0
	foreach var in `varlist' {
		tempvar newind
		gen `newind' = missing(`var')
		sort `by' `newind'
		if "`generate'"!=""{
			local j 0
			local realgen ""
			
			foreach gen in `generate' {
				if "`j'"=="`i'"{
					local realgen ="`gen'"
				}
				local j = `j' +1
			}
			if "`realgen'"!="" { 
				quietly gen `realgen' = `var'
				quietly replace `realgen' = `realgen'[_n-1] if ``newby''==``newby''[_n-1]
			}
		}
		else if "`replace'"=="replace" {
			replace `var' = `var'[_n-1] if ``newby''==``newby''[_n-1]
		}

		drop `newind'
		local i = `i' +1
	}
	sort `n'
end

