/**********************************************************
 *
 * DTA_TO_TXT.ADO: Save a dta file to text
 *
 * By Matthew Gentzkow
 * based in part on appendfile.ado
 *
 **********************************************************/

program define dta_to_txt

	version 10
	syntax [varlist] [if] [in], SAVing(str) [DTA(str) REPlace APPend Title(str) Comma DELIMiter(str) NONames NOLabel NOQuote]
	
	tempfile temp
	tempname tmp sav

	if "`replace'"=="replace" & "`append'"=="append" {
		di as error "Cannot specify both append and replace options"
		exit 198
	}

	preserve

	if "`dta'"!="" {
		confirm file "`dta'"
		use "`dta'", clear
	}
	outsheet `varlist' using "`temp'" `if' `in', `comma' delim(`delimiter') `nonames' `nolabel' `noquote'
	
	file open `tmp' using "`temp'", read

	if "`replace'"=="replace" {
		file open `sav' using "`saving'", write replace
	}
	else if "`append'"=="append" {
		file open `sav' using "`saving'", write append
	}
	else {
		file open `sav' using "`saving'", write
	}

	if "`title'"!="" {
		file write `sav' `"`title'"'_n		
	}

	file read `tmp' line
	while r(eof)==0 {
		file write `sav' `"`line'"'_n
		file read `tmp' line
	}
	file close `tmp'
	file close `sav'

	restore

end

