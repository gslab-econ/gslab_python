program def split, rclass
*! NJC 1.1.0 4 March 2002 
* NJC 1.0.0 19 February 2002 
	version 7 
	syntax varname(str) [if] [in] /*
	*/ [, Generate(str) noTrim Parse(str asis) DESTRING /*  
 	*/ force float Ignore(string) percent Limit(numlist int >0) ]
	
	* observations to use 
	marksample touse, strok
	qui count if `touse'
	if r(N) == 0 { error 2000 }

	* parsing on spaces by default, otherwise words of -parse()- 
	if `"`parse'"' == `""' { 
		local parse `"" ""'
		local trm "trim" 
	}
	local nparse : word count `parse'
	tokenize `"`parse'"' 
	
	* set up variables 
	* vw = variable worked on 
	* tp = position of this parse string 
	* mp = minimum position of parse string(s) 
	* pl = parse string length
	qui { 
		tempvar vw tp mp pl 
		gen int `tp' = 0
		gen int `mp' = 0 
		gen int `pl' = 0 

		gen str1 `vw' = "" 
	        if "`trim'" == "" {
        	        replace `vw' = trim(`varlist') if `touse'
	        }
        	else replace `vw' = `varlist' if `touse'
	} 	

	* initialise macros for main loop 
	if "`generate'" == "" { local generate "`varlist'" } 
        local j = 0
        local go = 1
	if "`limit'" == "" { local limit . } 

	* main loop: try to chop at parse strings 
        qui while `go' & `j' < `limit' {
		replace `mp' = .
		replace `pl' = 0 
		forval i = 1 / `nparse' { 
		        replace `tp' = index(`vw', `"``i''"')
			replace `mp' = min(`tp', `mp') if `tp'
			replace `pl' = length(`"``i''"') if `mp' == `tp' 
        	}
	        local j = `j' + 1
		tempvar part`j' 
                gen str1 `part`j'' = ""
                replace `part`j'' = substr(`vw', 1, `mp'-1) if `mp' < . 
                replace `vw' = `trm'(substr(`vw', `mp'+`pl', .)) if `mp' < . 
		replace `part`j'' = `vw' if `mp' == . 
                replace `vw' = "" if `mp' == . 
                local newvars "`newvars'`generate'`j' "
                capture assert `vw' == ""
                local go = _rc
        }

	* are new variable names OK? 
	* it is late in the day to check for possibly fatal error, 
	* but only now do we know which new variables needed 
	capture confirm new var `newvars'
	if _rc { 
		di as err "invalid stub `generate'" 
		exit _rc 
	} 

	* -generate- new variables 
	qui forval i = 1 / `j' { 
		gen str1 `generate'`i' = "" 
		replace `generate'`i' = `part`i'' 
	}
	
	* say what we have -generated- 
	return local varlist "`newvars'"
	return local nvars "`j'"
	local s = cond(`j' > 1, "s", "") 
	if "`destring'" != "" { 
		di as res "variable`s' born as string: " _c 
	} 	
	else di as res "variable`s' created as string: " _c 
	ds `newvars' 

	* -destring- if desired 
	if "`destring'" != "" { 
		if `"`ignore'"' != "" { 
			local ignore `"ignore(`ignore')"' 
		}	
		destring `newvars', replace `force' `float' `ignore' `percent'
	}	
end

