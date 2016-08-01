*! $Id: personal/m/mat2txt2.ado, by Keith Kranker <keith.kranker@gmail.com> on 2012/01/07 18:15:06 (revision ef3e55439b13 by user keith) $
*! Export a matrix to text file.
*
* This program is an update/modification of mat2txt.ado by Ben Jann and M Blasnik (v 1.1.2)
* 
* Changes from the original program are additions to the base program or cosmetic changes: {break}
* (1) Updated syntax to {it:mat2txt2 matname using ... , options }{break}
* (2) Allow multiple matrices. Allow e() and r() matrices. {break}
* (3) Replace cells equal to .z with empty cells {break}
* (4) Options to choose file delimiter. 
* (5) Matnames and Timestamp options {break}
* (6) Allow user to click on a link to view or open the output file.{break}
* (7) Handle option (Version 1.1+) {break}
* (8) Clean option (Verson 1.2+) {break}
* (9) Label option (Verson 1.3+){break}
* (10) Default delimiter is "_tab"  (previously ",") (Version 1.3+)  {break}
* (11) Filestamp option (Verson 1.4+) {break}
* (12) Rowclean, colclean, rowlabel, and collabel options (Verson 1.5+) {break}
*!
*! By Keith Kranker
*! Last updated: $Date$


program define mat2txt2

version 9.2
syntax anything [using] [ ,             ///  Main Directive
    REPlace APPend Handle(name)         ///  Append or replace output file
    TITle(str) Matnames NOTe(str) INTro ///  Add titles or notes to output file
    TIMestamp  FILEstamp                ///  Filename and/or a timestamp to the output file
    COLLabel ROWLabel                   ///  Attempt to replace column and row labels with a variable label
    Label                               ///  Identical to specifying both collabel and rowlabel 
    COLCLean ROWCLean                   ///  Suppress the display of matrix row and column names
    CLean                               ///  Identical to specifying both colclean and rowclean
    Tab COMma DELimit(str)              ///  Specify delimiter for file; specify output format
    Format(str)                         ///  Format numerical output
    ]

// Set up formats
if "`format'"=="" local format "%9.0g"
if strpos("`format'","c") != 0 & ("`tab'"!="tab") & ("`delimit'"!="") {
	di as error "Cannot use tab delimiter and a comma format at the same time."
	error 198
	}
local formatn: word count `format'
local matrixn: word count `anything'
tempname tempmatrix

// Set up delimiter
if "`tab'"=="tab" {
	if (`"`delimit'"'!="")  di as error "Potential conflict between -tab- and -delimit(`delimit')- options." _n "The option -delimit(`delimit')- was ignored."	
	if (`"`comma'"'!="")  di as error "Potential conflict between -tab- and -comma- options." _n "The option -comma- was ignored."	
	local delimit = "_tab"
	}
else if "`comma'"=="comma" {
	if (`"`delimit'"'!="")  di as error "Potential conflict between -comma- and -delimit(`delimit')- options." _n "The option -delimit(`delimit')- was ignored."	
	local delimit = `"",""'
	}
else if `"`delimit'"'=="" {
	local delimit = "_tab"  // Comma separated by default"
	}
else {
	local delimit = `""`delimit'""' //   Add a quotes to delimiter macro
	}

if `"`using'"' != "" & `"`handle'"' != "" {
	// Check that USING and HANDLE options are not both selected
	noisily di as error "You cannot specify both the -using- and -handle- options at the same time."
	error 198
}

if !missing("`label'") {
	// label is the same as calling rowlabel and collabel
	local rowlabel "rowlabel"
	local collabel "collabel"
}
if !missing("`clean'") {
	// clean is the same as calling rowclean and colclean
	local rowclean "rowclean"
	local colclean "colclean"
}

if (!missing("`rowlabel'") & !missing("`rowclean'")) | (!missing("`collabel'") & !missing("`colclean'")) {
	// Check that LABEL and CLEAN options are not both selected
	noisily di as error "You cannot specify options for  [row|col|.] -label- and -clean- at the same time."
	error 198
}


if `"`using'"' != "" {
	// USING option -- Begin writing file contents
	tempname myfile
	file open `myfile' `using' , write text `append' `replace'
	
	* FILEstamp Option
	if `"`filestamp'"'!=""  {
		// Filename at top of page
		local file_clean = subinstr(`"`using'"',"using","",1)
		cap local file_clean = `file_clean'
		while regexm( `"`file_clean'"', ".+[\\\/](.*[a-zA-Z0-9]+\..*[a-zA-Z0-9])+.*" ) {
			local file_clean = regexs(1) 
			}
		file write `myfile' `"`file_clean'"' _n _n 
		}
	}
else if "`handle'" != ""  {
	// HANDLE option -- point file writing to file already open
	local myfile `"`handle'"'
	}
else {
	noisily di as err "You must specifiy the -using- or -handle- option."
	error 198
}
	
* Title Option
if `"`title'"'!=""  {
	file write `myfile' `""`title'""' _n // Insert title at top of page
	}

// Loop through each matrix listed in `anything', printing contents to file.
local i = 0
while "`anything'"!="" {
	local i = `i'+1
	gettoken matrix anything : anything
	
	if "`matnames'"=="matnames" file write `myfile' `"`matrix'"' _n _n  // Option to write matrix name
	
	// IF matrix is a ereturn or return matrix (i.e. the matrix name contains parenthesis), then use a temporary matrix
	if regexm("`matrix'", "(\(|\))") {
		matrix `tempmatrix' = `matrix'
		local matrix "`tempmatrix'"
		}
	
	local nrows=rowsof(`matrix')
	local ncols=colsof(`matrix')
	QuotedFullnames `matrix' row
	QuotedFullnames `matrix' col

	// Write header row of table
	if missing("`colclean'") {
		file write `myfile'  `delimit'
		foreach col_name of local colnames {
			if !missing("`collabel'") & length(trim(`"`col_name'"'))  { 
				* Attempt to get see if column name is a varable, and (if it is) replace varname with the variable's label 
				local col_label `"`col_name'"'
				// di as txt  `"`col_name' --> STEP1 --> `col_label' "'
				cap confirm var `col_name', exact
				if !_rc {
					local col_var_label : var label `col_name'
					if length(`"`col_var_label'"') local col_label = subinstr(`"`col_var_label'"',`"`delimit'"',"_",.)
					// di as txt `"`col_name' --> STEP2 --> `col_label' "'
				}
				file write `myfile' `"`col_label'"' `delimit'   // col label
			} // end label option
			else {		
				file write `myfile' `"`col_name'"' `delimit'		// Column label
				}
		}
		file write `myfile' _n
	}
 
 
	// Loop through rows
	forvalues r=1/`nrows' {
		local row_name: word `r' of `rownames'
		if ("`rowclean'"=="")  {
			if !missing("`rowlabel'") & length(trim(`"`row_name'"'))  { 
				* Attempt to get see if rowumn name is a varable, and (if it is) replace varname with the variable's label 
				local row_label `"`row_name'"'
				// di as txt  `"`row_name' --> STEP1 --> `row_label' "'
				cap confirm var `row_name', exact
				if !_rc {
					local row_var_label : var label `row_name'
					if length(`"`row_var_label'"') local row_label = subinstr(`"`row_var_label'"',`"`delimit'"',"_",.)
					// di as txt `"`row_name' --> STEP2 --> `row_label' "'
				}
				file write `myfile' `"`row_label'"' `delimit'   // Row label
			} // end label option
			else {
				file write `myfile' `"`row_name'"' `delimit'  // Row label
				}
		}  
		
		// loop through columns
		forvalues c=1/`ncols' {
			cap macro drop cell
			cap macro drop cell_2
			cap macro drop fmtcell

			if `c'<=`formatn' & `formatn'>1  local fmt: word `c' of `format'
			else local fmt: word 1 of `format'
									
			local cell = (`matrix'[`r',`c'])
			
			if `cell' != .z {
				local fmtcell "`fmt'"
				local cell_2 = `"(`cell')"'
				}
			else {
				local fmtcell ""
				local cell_2 = ""
				}

			file write `myfile' `fmtcell' `cell_2' `delimit'
			
		}  // end loop through columns
		
		file write `myfile' _n  // Go to new line 
		
	}  // end loop through rows
	
	file write `myfile' _n 
	
}	// end loop through matrices


// Insert note and timestamp
if `"`note'"'!="" {
	file write `myfile' `""`note'""' _n   // Insert note at bottom of page
	}
if "`timestamp'"=="timestamp" {
	file write `myfile' _n `"$S_DATE $S_TIME"' _n
	}
file write `myfile' _n
	
if `"`using'"'!="" {
	// For USING option, close the file  and provide links to output
	file close `myfile'

	gettoken ucmd filename : using 
	local         filename `filename'

	di as txt "Open output file: " `"{stata `"shellout using "`filename'""'}"'
	di as txt "View output file: " `"{view `""`filename'""':view "`filename'"}"'	
	}
else if `"`handle'"'!="" {
	// HANDLE option leaves the file open with a short note
	di as txt "Matrix written to file handle: " as res "`myfile'"
	}	

end


program define QuotedFullnames
	args matrix type
	tempname extract
	local one 1
	local i one
	local j one
	if "`type'"=="row" local i k
	if "`type'"=="col" local j k
	local K = `type'sof(`matrix')
	forv k = 1/`K' {
		mat `extract' = `matrix'[``i''..``i'',``j''..``j'']
		local name: `type'names `extract'
		local eq: `type'eq `extract'
		if `"`eq'"'=="_" local eq
		else local eq `"`eq':"'
		local names `"`names'`"`eq'`name'"' "'
	}
	c_local `type'names `"`names'"'
end
