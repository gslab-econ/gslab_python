**********************************************************
*
* Leaveout.ado
*
* Create a new variable (newvarname in syntax) that has the
*   weighted average(s) excluding missings.
*
**********************************************************

cap program drop leaveout

program define leaveout

version 11
syntax  newvarname, variable(varname) [weight(varname) by(varlist) if(string)]
	confirm new variable `varlist'
	
	if "`if'" != "" {
	local if = "if " + "`if'" 
	}
	if "`weight'" == "" {
	local weight = 1 
	}
	
	egen _temporaryvar1 = sum(`weight'*`variable') `if', by(`by')
	egen _temporaryvar2 = sum(`weight'*(`variable'~=.)) `if', by(`by')
	gen `varlist' = (_temporaryvar1 -(`weight'*`variable'))/(_temporaryvar2-(`weight'*(`variable'~=.))) `if'

	drop _temporaryvar1 _temporaryvar2

end


