*! Version 1.1.0 SPJ/NJC 11 December 2000   (STB-59: dm83)
program define rensfix
        version 6
        args suffix new junk
        if "`junk'" != "" { error 198 }

        unab 0 : _all
        syntax varlist
        tokenize `varlist'

        local loc = length("`suffix'")
        while "`1'" != "" {
                local loc2 = length("`1'") - `loc'
                local z = substr("`1'", `loc2' + 1, .)
                if "`z'"  == "`suffix'" {
                        local newn = substr("`1'", 1, `loc2') + "`new'"
			local oldlist "`oldlist' `1'" 
                        local newlist "`newlist' `newn'" 
                }
                mac shift
        }

	local 0 `newlist' 
	syntax newvarlist 
	tokenize `varlist'
	local nvars : word count `varlist' 
	
	nobreak { 
		local i = 1 
		while `i' <= `nvars' { 
			local oldn : word `i' of `oldlist' 
			rename `oldn' ``i'' 
			local i = `i' + 1
		} 
	} 	
end
