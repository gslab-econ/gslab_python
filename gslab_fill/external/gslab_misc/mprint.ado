**********************************************************
*
* mprint.ado
*
*  Report the results of a merge in a standard format
*   
*
**********************************************************


cap program drop mprint

program define mprint

version 11
syntax ,  mname(str) uname(str) keep(str) SAVing(str)  [ Title(str) REPlace APPend  ]

	* Preliminaries
	confirm numeric variable _merge
	local saving: subinstr local saving "." ".", count(local ext)
	if !`ext' local saving "`saving'.txt"
	tempname myfile

	file open `myfile' using "`saving'", write text `append' `replace'

	* write title/labels
	if "`title'"!="" {
		file write `myfile' `"`title'"' _n
	}
	*"
	file write `myfile' "`mname'" _tab
	file write `myfile' "`uname'" _tab
	file write `myfile' "`keep'" _tab
	
	* Merge rates
	quietly: count if _merge == 1	
	file write `myfile' "`r(N)'" _tab
	
	quietly: count if _merge == 2
	file write `myfile' "`r(N)'" _tab
	
	quietly: count if _merge == 3
	file write `myfile' "`r(N)'" _n

	file close `myfile'

end

