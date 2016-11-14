/**********************************************************
 *
 * LOADGLOB.ADO: Define global variables based on an
 *	input file. Each line of file is assumed to have
 *	the name of the global variable followed by a space
 *	followed by the value of the global variable. Lines
 *	beginning with * are treated as comments. Script also
 *	ignores any lines in the file that do not have at least
 *	two words (defined as blocks of text separated by a
 *	space). Note that strings enclosed in double quotes
 *	count as one word.  Nested quotes are recognized.
 *
 **********************************************************/

program define loadglob

	version 10
	syntax using/

	cap file close IN
	file open IN using `using', read
	file read IN line
	while r(eof)==0 {

		* if line does not begin with "*" & line has exactly 2 "words"
		if regexm(`"`line'"',"^\*.*")==0 & wordcount(`"`line'"')>=2 {
			local lname : word 1 of `line'
			local lval : word 2 of `line'
			global `lname' = `"`lval'"'
		}
		file read IN line
	}
	file close IN
	
end

