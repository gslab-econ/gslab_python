*! 2.1.0 NJC 26 January 2011 
* 2.0.0 NJC 3 December 2006 
* 1.0.0 NJC 10 February 2003 
* all subsets of 1 ... k distinct selections from a list of k items 
program tuples
	version 8 
	syntax anything [, max(numlist max=1 int >0) asis DIsplay VARlist] 

	if "`varlist'" != "" & "`asis'" != "" { 
		di as err "varlist and asis options may not be combined"
		exit 198 
	}	

	if "`varlist'" == "" { 
		local capture "capture" 
	}	
	
	if "`asis'" == "" { 
		`capture' unab anything : `anything' 
	} 
	
	tokenize `"`anything'"'  
	local n : word count `anything' 

	if "`max'" == "" local max = `n' 
	else if `max' > `n' { 
		di "{p}{txt}maximum reset to number of items {res}`n'" 
		local max = `n' 
	} 
	
	if "`display'" == "" local qui "*" 
	local imax = 2^`n' - 1   
	local k = 0 
	forval I = 1/`max' { 
		forval i = 1/`imax' { 
			qui inbase 2 `i'
			local which `r(base)' 
			local nzeros = `n' - `: length local which' 
			local zeros : di _dup(`nzeros') "0" 
			local which `zeros'`which'  
			local which : subinstr local which "1" "1", ///
				all count(local n1) 
			if `n1' == `I' {
				local previous "`out'"  
				local out 
				forval j = 1 / `n' { 
					local char = substr("`which'",`j',1) 
					if `char' local out `out' ``j''  
				}
				c_local tuple`++k' `"`out'"'
				`qui' di as res "tuple`k': " as txt `"`out'"'  
			}	
			
		} 	
	}

	c_local ntuples `k' 

end 
