* This is a version of the Stata command cf (in cf.ado)
* The only change is that the exit flag is always zero.
* This allows it to be run repeatedly in a script and
* not break if one of the files turns out to be different.

*! version 3.1.0  01dec2006
program define cf_mg, rclass
	version 8
	syntax varlist using/ [, Verbose All]

	local obs = _N
	local dif "0"
	local Nsum = 0
	if _caller() < 10 {
		if "`all'"!="" {
			local verbose "verbose"
		}
		local qv = cond("`verbose'"=="", "*", "noisily")
	}
	else {
		local qv = cond("`all'"=="", "*", "noisily")
	}
	quietly describe using `"`using'"'
	if (r(N) != _N) {
		di in gr "master has " ///
			in ye "`obs'" ///
			in gr " obs., using " ///
			in ye r(N)

		************************************************
		************************************************
		*** Changed from 'exit 9' to 'exit 0'
		************************************************
		************************************************
		exit 0
	}

	if "`varlist'" != "" {
		preserve
		keep `varlist'  /* reduce to a minimal set */

		local i 1
		foreach var of local varlist {
			capture confirm var `var'
			if !_rc {
				local abbrev`i' = abbrev("`var'", 16)
				tempname `i'
				rename `var' ``i''
			}
			
			local `++i'
		}

		tempfile tempcfm
		quietly save `"`tempcfm'"'

		qui use `"`using'"'
		/* note that the main and using data sets are switching roles. */

		/* Do a preliminary run-through to find minimal set of vars,
		i.e., the vars common to the two data sets.  */
		foreach var of local varlist {
			capture unab tmpname : `var'
			if !_rc & ("`tmpname'" == "`var'") {
				local comvars "`comvars' `var'"
			}
		}

		if "`comvars'" != "" {
			keep `comvars'  /* reduce to a minimal set */
			tempvar cf_merge
			quietly merge using `"`tempcfm'"', _merge(`cf_merge')
		}

		local i 1
		foreach var of local varlist {
			capture unab tmpname : `var'
			if _rc | ("`tmpname'" != "`var'") {
				di in gr %19s "`abbrev`i'':  " ///
					in ye "does not exist in using"
				local dif "9"
			}
			else {
				
				capture count if `var' != ``i''
				/* `var' is from the original using file.
				``i'' is from the original master file.
				(But the two have switched roles.) */
				if _rc {
					local tm : type ``i''
					local tu : type `var'
					di in gr %19s "`abbrev`i'':  " ///
						in ye "`tm'" ///
						in gr " in master but " ///
						in ye "`tu'" ///
						in gr " in using"
					local dif "9"
				}
				else if r(N)==0 {
					`qv' di in gr %19s "`abbrev`i'':  " "match"
				}
				else {
					di in gr %19s "`abbrev`i'':  " ///
						in ye r(N) ///
						in gr " mismatches"
					local Nsum = `Nsum' + r(N)
					if "`verbose'" != "" & _caller() >= 10 {
					local maxobslen = length("`=_N'")
					    forvalues j = 1/`=_N' {
						if `var'[`j'] != ``i''[`j'] {
						    di _col(20) ///
						       as txt "obs " ///
						       as res ///
						       %`maxobslen'.0f `j' ///
						       as txt ". " ///
						       as res ``i''[`j'] ///
						       as txt " in master; " ///
						       as res `var'[`j'] ///
						       as txt " in using"
						}
					    }
					}
					local dif "9"
				}
			}
			local `i++'
		}
		restore
	}
	return local Nsum = `Nsum'
	************************************************
	************************************************
	*** Changed from 'exit `dif'' to 'exit 0'
	************************************************
	************************************************
	exit 0
end

