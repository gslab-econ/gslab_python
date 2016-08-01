program def univstat
*! NJC 1.2.0 27 April 2000 
* NJC 1.1.0 13 December 1999 
* NJC 1.0.1 5 March 1999
* Fred Wolfe wants se as well
* NJC 1.0.0 17 January 1999
        version 6.0
        syntax varlist(min=1) [if] [in] [aweight fweight] /* 
	*/ [ , Matname(str) Stat(str) noHeader BY(varname) /*  
	*/ Generate(str) MISSing SEQuential * ]  
        local nvars : word count `varlist'

        if "`stat'" == "" { local stat "3" }
        local nstats : word count `stat'

        local stats "N sum_w mean Var min max p5 p10 p25 p50 p75 p90 p95"
        local stats "`stats' skewness kurtosis p1 p99 sum"

        local novar = 1
        local j = 1
        while `j' <= `nstats' {
                local st : word `j' of `stat'
                capture confirm integer number `st'
                if _rc == 0 {
                        if `st' < 1 | `st' > 18 {
                                di in r "invalid syntax"
                                exit 198
                        }
                        if `st' == 4 { local novar = 0 }
                        local stat`j' `st'
                }
                else {
                        if "`st'" == "n" | "`st'" == "N" {
                                local stat`j' 1
                        }
                        else if "`st'" == "sum_w" {
                                local stat`j' 2
                        }
                        else if "`st'" == "mean" {
                                local stat`j' 3
                        }
                        else if "`st'" == "var" | "`st'" == "Var" {
                                local novar 0
                                local stat`j' 4
                        }
                        else if "`st'" == "SD" | "`st'" == "sd" {
                                local novar 0
                                local stat`j' "sd"
                        }
                        else if "`st'" == "min" {
                                local stat`j' 5
                        }
                        else if "`st'" == "max" {
                                local stat`j' 6
                        }
                        else if "`st'" == "p1" {
                                local stat`j' 16
                        }
                        else if "`st'" == "p5" {
                                local stat`j' 7
                        }
                        else if "`st'" == "p10" {
                                local stat`j' 8
                        }
                        else if "`st'" == "p25" {
                                local stat`j' 9
                        }
                        else if "`st'" == "p50" /* 
			 */ | "`st'" == "med" | "`st'" == "median" {
                                local stat`j' 10
                        }
                        else if "`st'" == "p75" {
                                local stat`j' 11
                        }
                        else if "`st'" == "p90" {
                                local stat`j' 12
                        }
                        else if "`st'" == "p95" {
                                local stat`j' 13
                        }
                        else if "`st'" == "p99" {
                                local stat`j' 17
                        }
                        else if "`st'" == "skewness" | "`st'" == "skew" {
                                local stat`j' 14
                        }
                        else if "`st'" == "kurtosis" | "`st'" == "kurt" {
                                local stat`j' 15
                        }
                        else if "`st'" == "sum" {
                                local stat`j' 18
                        }
                        else if "`st'" == "se" | "`st'" == "SE" {
                                local novar 0
                                local stat`j' "se"
                        }
			else if "`st'" == "iqr" | "`st'" == "IQR" { 
				local stat`j' "iqr" 
			}
			else if "`st'" == "range" { 
				local stat`j' "range"
			}	
                        else {
                                di in r "invalid syntax"
                                exit 198
                        }
                }

                if "`stat`j''" == "sd" | "`stat`j''" == "se" /* 
		*/ | "`stat`j''" == "iqr" | "`stat`j''" == "range" {
                        local colname "`stat`j''"
                }
                else {
                        local colname : word `stat`j'' of `stats'
                        if `stat`j'' >= 7 & `stat`j'' < 18 {
                                local detail "detail"
                        }
                }
                local cnames "`cnames' `colname'"
                local j = `j' + 1
        }
	
	if "`by'" != "" { 
		if `nvars' > 1 { 
			di in r "incorrect syntax" 
			exit 198 
		}
		if "`generate'" != "" { local and "gen(`generate')" }
		local and "`and' `sequential' `missing'" 
		local nobreak "nobreak" 
	}
	 
	`nobreak' { 
	
	if "`by'" != "" { 
		qui separate `varlist' `if' `in', by(`by') `and' 
		local varlist "`r(varlist)'"
		local nvars : word count `varlist'
	}	
	
        if "`matname'" == "" {
                local header "noheader"
                tempname matname
        }
        mat `matname' = J(`nvars',`nstats',0)

        if "`detail'" == "" & `novar' { local monly "meanonly" }

        local i = 1
        while `i' <= `nvars' {
                local var : word `i' of `varlist'
                qui su `var' `if' `in' [`weight' `exp'], `detail' `monly'
                local j = 1
                while `j' <= `nstats' {
                        if "`stat`j''" == "sd" {
                                mat `matname'[`i',`j'] = sqrt(_result(4))
                        }
                        else if "`stat`j''" == "se" {
                                mat `matname'[`i',`j'] = /*
                                */ sqrt(_result(4) / _result(1))
                        }
			else if "`stat`j''" == "iqr" { 
				mat `matname'[`i',`j'] = /* 
				*/ _result(11) - _result(9) 
			} 	
			else if "`stat`j''" == "range" { 
				mat `matname'[`i',`j'] = /* 
				*/ _result(6) - _result(5)
			}
                        else mat `matname'[`i',`j'] = _result(`stat`j'')
                        local j = `j' + 1
                }
                local i = `i' + 1
        }

        mat rownames `matname' = `varlist'
        mat colnames `matname' = `cnames'
        mat li `matname', `options' `header'

	if "`by'" != "" { qui drop `varlist' } 

	} 
end

