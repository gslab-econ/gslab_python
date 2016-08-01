*! NJC 1.2.0 22 November 2005 
*! NJC 1.1.0 21 November 2000 
program rowsort, sort 
	version 8 
	syntax varlist(numeric) [if] [in], Generate(str) /// 
	[ Missing(numlist max=1 int) Ascend Descend ] 

	quietly {
		marksample touse, novarlist 
		count if `touse' 
		if r(N) == 0 error 2000 
		local N = r(N) 
		
		if "`ascend'" != "" & "`descend'" != "" { 
			di as err "must choose either ascend or descend" 
			exit 198 
		} 	

		foreach v of local varlist { 
			capture assert `v' == int(`v') if `touse' 
			if _rc { 
				di as err "`v' bad: integer variables required"
				exit 498 
			} 	
		} 	

		local nvars : word count `varlist'
		local mylist "`varlist'" 
		local 0 "`generate'" 
		syntax newvarlist 
		local generate "`varlist'" 
		local ngen : word count `generate'
		
		if `nvars' != `ngen' { 
			di as err "`nvars' variables, but `ngen' new " ///
			plural(`ngen', "name") 
			exit 198 
		} 

		replace `touse' = -`touse' 
		sort `touse' 

		foreach g of local generate {
			gen `g' = . 
		} 	

		forval i = 1/`N' {
			local inobs 
			
			if "`missing'" != "" { 
				foreach v of local mylist { 
					local inval = `v'[`i'] 
					if mi(`inval') local inobs `inobs' `missing'
					else local inobs `inobs' `inval' 
				}
			}	
			else { 	
				foreach v of local mylist { 
					local inval = `v'[`i'] 
					local inobs `inobs' `inval'
				} 
			}
			
			numlist "`inobs'", missingok sort
			local nlist "`r(numlist)'" 

			if "`missing'" != "" { 
				local newlist 
				foreach n of local nlist { 
					if `n' == `missing' { 
						local newlist `newlist' .
					}	
					else local newlist `newlist' `n'
				}
				local nlist "`newlist'" 
			}
			
			tokenize "`nlist'" 
			
			if "`descend'" == "" { 
				forval j = 1/`nvars' { 
					local g : word `j' of `generate' 
					replace `g' = ``j'' in `i'
				} 
			} 
			else { 
				forval j = 1/`nvars' { 
					local J = `nvars' - `j' + 1 
					local g : word `j' of `generate' 
					replace `g' = ``J'' in `i' 
				} 	
			}	
		} 	
	}	
end 	
	
