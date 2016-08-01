*! 1.0.0 NJC 23 April 2008 
program seqvar
	version 8 

	gettoken seqvar 0 : 0, parse("= ") 
	capture confirm numeric var `seqvar' 
	if _rc == 0 local exists 1 
	else { 
		capture confirm string var `seqvar' 
		if _rc == 0 { 
			di as err ///
			"{cmd:`seqvar'} exists, but as string variable"
			exit 108 
		} 
		capture confirm new var `seqvar' 
		if _rc { 
			if _rc != 110 error _rc 
			local exists 1 
		} 
		else local exists 0 
	} 

	gettoken eqs 0 : 0, parse("=") 
	if "`eqs'" != "=" { 
		di as err "= sign required" 
		exit 100 
	} 

	gettoken seq 0 : 0, parse(,) 
	numlist "`seq'", int  
		
	syntax [, replace] 
	if `exists' & "`replace'" == "" { 
		di as err ///
		"`seqvar' exists, but {cmd:replace} option not specified"
		exit 198 
	}
 
	local seq "`r(numlist)'" 
	local nseq : word count `seq' 
	tokenize "`seq'" 
	local n = min(_N, `nseq') 
	
	quietly { 
		if "`replace'" == "" gen long `seqvar' = . 
		else replace `seqvar' = . 

		forval i = 1/`n' { 
			replace `seqvar' = ``i'' in `i' 
		}
		
		compress `seqvar'  
	} 

	// explicit blank to suppress visible display 
	label var `seqvar' `" "' 
end

