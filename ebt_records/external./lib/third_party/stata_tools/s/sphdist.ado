*! version 1.1.0 June 19, 2000 @ 14:07:03
*! computes distances on a sphere
program define sphdist
version 6.0

	syntax [if] [in], lat1(varlist max=3) lon1(varlist max=3) lat2(varlist max=3) lon2(varlist max=3) gen(str) [ew1(varname) sn1(varname) ew2(varname) sn2(varname) radians radius(real 0) units(str) thin float double]

	local gencnt : word count `gen'
	if `gencnt'>1 {
		display in red "Only 1 variable may be generated!"
		exit 198
		}
	confirm new var `gen'

	if "`float'"!="" {
		if "`double'"!="" {
			display in red "Pick either float or double, if you like, but not both!"
			exit 198
			}
		}

 	if "`radians'"=="" {
		local max 3
		}
	else {
		local max 1
		}

	if `radius'<0 {
		display in red "who ever heard of a negative radius?"
		exit 198
		}

	local theVar "lat1 lon1 lat2 lon2"
	parse "`theVar'", parse(" ")
	local cnt 1
	while "``cnt''"!="" {
		local numvar : word count ```cnt'''

		if `numvar'>`max' {
			/* could be bad grammar in the future, but right now `max' can only be 1 here */
			display in red "You specified `numvar' variables for the option ``cnt'', but only `max' is allowed!"
				exit 198
			}
		local cnt = `cnt' + 1
		}

	if "`ew'"!="" {
		capture assert `ew'==1 | `ew'==-1 | `ew'==.
		if _rc {
			display in red "The ew variable `ew' must contain -1s, missing values, or 1s *only*"
			exit 666
			}
		}
	if "`sn'"!="" {
		capture assert `sn'==1 | `sn'==-1 | `sn'==.
		if _rc {
			display in red "The sn variable `sn' must contain -1s, missing values, or 1s *only*"
			exit 666
			}
		}

	/* done with the easy error checking */
	marksample useme
	
	tempname rad
	if `radius'==0 {
		if "`units'"=="" {
			local units "km"						 /* rah rah metric */
			}
		else {
			if !("`units'"=="km" | "`units'"=="mi" | "`units'"=="naut" | "`units'"=="erca") {
				display in red "Units must be km, mi, or naut!"
				exit 198
				}
			}

		if "`units'"=="km" {
			scalar `rad' = 20000/_pi
			}
		else {
			if "`units'"=="mi" | "`units'"=="erca" {
				scalar `rad' = 20000*100000/(2.54*12*5280*_pi)
				if "`units'"== "erca" {
					scalar `rad' = `rad'*sqrt(640)
					local units "ercas"
					}
				else {
					local units "miles"
					}
				}
			else {						/* nautical miles */
				scalar `rad' = 10800/_pi
				local units "nautical miles"
				}
			}
		}
	else {
		scalar `rad' = `radius'				 /* yes, this is a waste of computing */
		}

	capture n {
		if "`radians'"=="" {
			/* thin included 'cuz conversion required 4 doubles */
			if "`thin'"!="" {
				preserve
				}

			/* convert to radians */
			local gvar "latr1 lonr1 latr2 lonr2"
			tempvar `gvar'
			local sgnVars "sn1 ew1 sn2 ew2" /* names of sign variables */
			parse "`theVar'", parse(" ")
			local cnt 1
			while "``cnt''"!="" {
				local genVar : word `cnt' of `gvar'
				local sgnVar : word `cnt' of `sgnVars'
				deg2rad  ```cnt''' if `useme', gen(``genVar'') `float' `double'
				if "``sgnVar''"!="" {
					quietly replace ``genVar'' = ``genVar''*``sgnVar'' if `useme'
					}
				if "`thin'"!="" {
					sdrop ```cnt'''
					}
				local cnt = `cnt' + 1
				}
			
			local lat1 "`latr1'"
			local lat2 "`latr2'"
			local lon1 "`lonr1'"
			local lon2 "`lonr2'"
			}

		/* need to find cosine of angle, and then convert to get arctan */
		tempvar costhet
		/* local costhet "costhet" */
		gen double `costhet' = sin(`lat1')*sin(`lat2')+ cos(`lat1')*cos(`lat2')*cos(`lon2'-`lon1')
#delimit ;
		gen `gen' =
		  cond((`costhet'==1) | (`lat1'==`lat2' & `lon1'==`lon2'),0,
		  cond(`costhet'==-1,_pi,
		  (_pi/2 - atan(`costhet'/sqrt(1-`costhet'*`costhet')))
		  )) * `rad' if `useme';
#delimit cr
		if "`units'"!="" {
			local units " in `units'"
			}
		label var `gen' "Distance`units'"
		}	/* end capture */
	local rc = _rc
	if "`thin'"!="" {
		if !`rc' {
			restore, not
			}
		}
	exit `rc'
end
