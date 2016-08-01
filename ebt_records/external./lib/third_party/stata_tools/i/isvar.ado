*! NJC 1.0.0 20 Sept 2005 
program isvar, rclass  
	version 8 
	syntax anything 
	
	foreach v of local anything { 
		capture unab V : `v' 
		if _rc == 0 local varlist `varlist' `V' 
		else        local badlist `badlist' `v' 
	}

	di 

	if "`varlist'" != "" { 
		local n : word count `varlist' 
		local what = plural(`n', "variable") 
		di as txt "{p}`what': " as res "`varlist'{p_end}" 
		return local varlist "`varlist'" 
	}	
	
	if "`badlist'" != "" {
		local n : word count `badlist' 
		local what = plural(`n', "not variable") 
		di as txt "{p}`what': " as res "`badlist'{p_end}" 
		return local badlist "`badlist'" 
	}	
end 
