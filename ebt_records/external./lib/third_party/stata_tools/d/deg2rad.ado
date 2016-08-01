*! version 1.0.0 June 19, 2000 @ 13:37:25
*! converts degrees to radians
program define deg2rad
version 6.0

	syntax varlist(max=3) [if] [in], gen(str) [float double]
	marksample useme

	confirm new var `gen'

	if "`float'"!="" {
		if "`double'"!="" {
			display in red "Choose at most one of float or double!"
			exit 198
			}
		}
	
	local numvar : word count `varlist'
	parse "`varlist'", parse(" ")
	if `numvar'>=2 {
		local extra "+ `2'/60"
		}
	if `numvar'==3 {
		local extra "`extra' + `3'/3600"
		}

	gen `float' `double' `gen' = (`1' `extra')*_pi/180 if `useme'
end
