program define strparse, rclass
*! 2.1.0 MB/NJC 26 July 2000 
* 2.0.0 M Blasnik and NJ Cox 2 July 1999
version 6.0
syntax varlist(max=1 string) [if] [in] , Generate(str) [noTrim Parse(str)]

if trim(`"`parse'"') == `""' { 
	local parse " "
	local trm "trim" 
}

local plen = length(`"`parse'"')

tempvar orig ndx
marksample touse, strok

quietly {
        count if `touse'
        if r(N) == 0 {
                di in r "no observations"
                exit 2000
        }

        /* 
	   check `generate'1-`generate'9 do not exist 
	
	   this may -- exceptionally -- not check for 
	   variables that are needed -- `generate'10 on 

	   this may -- commonly -- check for variables
	   that are not needed 

	   short of doing everything twice, how else 
	   do we know exact # of variables needed? 
	*/    
        local i=1
        while `i' < 10 {
                confirm new var `generate'`i'
                local i = `i' + 1
        }

        local typ: type `varlist'
        if "`trim'" == "" {
                gen `typ' `orig' = trim(`varlist') if `touse'
        }
        else gen `typ' `orig' = `varlist' if `touse'

        gen byte `ndx' = index(`orig', `"`parse'"')
        count if `ndx'
        if r(N) == 0 {
                noi di in  bl "Warning: parsing character not found"
        }

        local i = 0
        local go = 1
        while `go' {
	        local i = `i' + 1
                gen str1 `generate'`i' = ""
                replace `generate'`i' = substr(`orig', 1, `ndx'-1) if `ndx'
                replace `orig' = `trm'(substr(`orig', `ndx'+`plen', .)) if `ndx'
		replace `generate'`i' = `orig' if `ndx' == 0 
                replace `orig' = "" if `ndx' == 0 
                label var `generate'`i' "word `i' of `varlist'"
                local newvars "`newvars' `generate'`i'"
                cap assert `orig' == ""
                if _rc != 0 { replace `ndx' = index(`orig', `"`parse'"') }
                else local go = 0
        }

	local Nvar : word count `newvars' 
        return local Nvar = `Nvar'
        return local varlist "`newvars'"
}

local s = cond(`i' > 1, "s", "")
di in g "new variable`s' created: `newvars'"

end

