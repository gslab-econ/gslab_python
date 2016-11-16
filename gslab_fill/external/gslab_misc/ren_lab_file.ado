/**********************************************************
 *
 * REN_LAB_FILE.ADO: Rename and re-label variables
 *  using input from a text file.
 *
 * Date: 7/08
 * Creator: MG
 *
 **********************************************************/

cap program drop ren_lab_file

program define ren_lab_file

	version 10
	syntax using/ [, rename label]
	
	tempname rlf
	file open `rlf' using "`using'", read

	file read `rlf' line
	while r(eof)==0 {

		local line = subinstr(`"`line'"',char(9)," ",.) /* tabs to spaces */
		local varname: word 1 of `line'

		* rename only
		if strlen("`rename'") & ~strlen("`label'") {
			local newname : word 2 of `line'
			if strlen("`varname'") & strlen("`newname'") {
				rename `varname' `newname'
			}
		}

		* label only
		if ~strlen("`rename'") & strlen("`label'") {
			local newlab : word 2 of `line'
			if strlen("`varname'") & strlen("`newlab'") {
				label var `varname' "`newlab'"
			}
		}

		* both
		if strlen("`rename'") & strlen("`label'") {
			local newname : word 2 of `line'
			local newlab : word 3 of `line'
			if strlen("`varname'") & strlen("`newname'") & strlen("`newlab'") {
				rename `varname' `newname'
				label var `newname' "`newlab'"
			}
		}

		file read `rlf' line
	}

	file close `rlf'

end

