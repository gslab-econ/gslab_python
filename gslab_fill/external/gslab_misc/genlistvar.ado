**********************************************************
*
* genlistvar.ado
*
* Create a new variable (newvarname in syntax) that is a list of 
*   all values of a given variable within specified (by) groups.
*
**********************************************************

cap program drop genlistvar

program define genlistvar

version 11
syntax  newvarname, variable(varname) by(varlist)

	* Preliminaries
	confirm new variable `varlist'
	tempvar j
	
	* Prepare variables for reshape
	so `by' `variable'	
	tostring `variable', force replace
	replace `variable' = "" if `variable' == "."
	egen `j' = seq(), by( `by' )
	quietly tab `j'
	local max_j = r(r)
	
	reshape wide `variable', i( `by' ) j( `j' )
	
	* Collect the new variable values in the single list variable
	gen `varlist' = ""
	forvalues index = 1/`max_j'{
		quietly replace `varlist' = `varlist'+`variable'`index'+";" if `variable'`index' !=""
		drop `variable'`index'
	}
	* Clean list variable of extra ";"
	replace `varlist' = regexr( `varlist',"\;*$","")
end

