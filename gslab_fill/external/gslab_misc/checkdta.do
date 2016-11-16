**********************************************************
*
* Checkdta Report
*
* Create file, checkdta.log, that allows users to check
* whether Stata datasets have actually changed after
* make.bat is re-run, and checkdtaprops that checks if
* the data set has a valid key.
**********************************************************

*************************************************************************
* MAXMEM:  Estimate the amount of memory CHECKDTA will require. 
*		   It is called by CHECKDTA
* 
* Inputs:  List of files and file size in ..\temp\dirlog.txt
* 	       produced by the command "dir /s ..\output\*.dta > ..\temp\dirlog.txt"
*
* Outputs: Estimate of memory CHECKDTA requries. Saved in r(maxfsize)
*
**********************************************************
clear all
program define maxmem, rclass

	version 10
	local maxfsize 0
	
	local dirlist "..\temp\dirlog.txt"

	* read directory data from temporary file
	tempname fh
	
	file open `fh' using "`dirlist'", text read
	file read `fh' line
	
	local nfiles = 0
	
	* Find the maximum file save 
	while r(eof)==0  {

		if `"`line'"' ~= "" & substr(`"`line'"',1,1) ~= " " {

			if "`c(os)'" == "Windows" {
				local fsize : word 4 of `line'
				local fsize = subinstr("`fsize'",",","",.)
				local fsize = int(`fsize')	
				if (`fsize' > `maxfsize') {
				local maxfsize "`fsize'"
				}
			}
			local fsizes "`fsizes' `fsize'"

		}

		file read `fh' line
	
	}

	file close `fh'
	
	* Estimate memory required to run checkdta
	local maxfsize = subinstr("`maxfsize'",",","",.)
	local maxfsize = int(`maxfsize')
	local maxfsize = round(`maxfsize'*0.0009765625,0.1)
	local maxfsize = int(1.2* `maxfsize')+200
	return local maxfsize = `maxfsize'
end

**********************************************************
* RUNCHECKS: Performs checks on an output dta file
*			 It is called by CHECKDTA
*
* Inputs:    Path to a dta file
*		     Estimate of memory required to run
*
* Outputs:   Prints results of checks to checkdta and checkdtaprops
*
**********************************************************
program define runchecks
	
	quietly: version 10
	syntax using/, memory(real)
	
	* Set preliminaries
	quietly: set linesize 255
	
	* Print file name to each log
	foreach logfile in checkdta checkdtaprops{
		quietly: cap log using "../output/`logfile'.log", append text
		display ""
		display ""
		display ""
		display ""
		display "============================================="
		display "File: `using'"
		display "============================================="
		quietly cap log close  _all
	}
	clear
	* Open each file and run most memory intensive command, 
	* increasing memory allocated to Stata if necessary
	quietly{
		capture use "`using'", clear
		count
		if r(N) !=0 {
			desc , varlist
			local var=word(r(varlist),1)
			capture noisily unique `var'
		}
		while r(N) == 0 | _rc!=0{
			clear
			local memory = round(`memory'*1.25)
			set mem `memory'
			capture use "`using'"
			capture unique _all	
			count
			if r(N)!=0{
				desc , varlist
				local var=word(r(varlist),1)
				capture noisily unique `var'
			}
		}
	}
	
	* Log Checkdta calculations
	quietly: cap log using "../output/checkdta.log", append text 
	datasignature
	sum
	quietly: cap log close  _all
	
	* Check if data are sorted and if the sort variables form a valid key
	* Save to checkdtaprops.log
	quietly: cap log using "../output/checkdtaprops.log", append text
	quietly describe , varlist
	local sortlist = r(sortlist)
	if "`sortlist'"=="."{
		di as error "WARNING: empty sortlist" 
	}
	else{
		* Parse Key and check if it has missing values depending on type of variable
		local missingcount=0
		foreach var in `sortlist'{
			local type: type `var'
			if strpos("`type'","str")>0{
				quietly count if `var'==""
			}
			else{
				quietly count if `var'==.
			}
			if r(N)>0{
				di as error "WARNING: A variable in your sortlist, `var', has one or more missing values"
			}
			
			local missingcount = r(N) + `missingcount'
		}
		* If it has no missing values, check if it has a unique key
		if `missingcount'==0{
			quietly unique `sortlist'
			if r(N)!=r(sum){
				di as error "WARNING: the elements of sortlist do not uniquely identify the observations in the dataset."
			}
			else{
				di "Sortlist forms a key"
			}
		}
	}
	
	clear
	quietly: cap log close  _all
end

**********************************************************
* CHECKDTA: Creates list of DTA files to check and loops over it
*           Calls programs that estimate memory required and perform checks
*
* Inputs:   Files saved in "../output/" folder
*			MAXMEM program
*			RUNCHECKS program
*			List of files in ..\temp\filelist.txt
* 	       	produced by the command "dir /s /b ..\output\*.dta >..\temp\filelist.txt"
*
* Outputs:  Information printed to checkdta.log and checkdtaprops.log
*
**********************************************************
program define checkdta

	version 10
	syntax [, startfolder(string)]

	* Set Preliminaries
	quietly: set linesize 255
	quietly: cap log close
	set more off
	if "`startfolder'" == "" {
		local startfolder "..\output"
	}
	
	quietly: cap log using "../output/checkdta.log", replace text
	* Print checkdta Log Header
	display "=========================================================="
	display "Checkdta.ado Report:  
	display "For every .dta file in ../output, checkdta.ado opens the file,"
	display "runs datasignature and sum, and outputs to this log."
	display ""
	display "Start folder: `startfolder'"
	display "=========================================================="
	display ""
	display ""
	quietly: cap log close _all

	quietly: cap log using "../output/checkdtaprops.log", replace text
	* Print checkdtaprops Log Header
	display "=========================================================="
	display "Checkdtaprops.ado Report:  
	display "For every .dta file in ../output, checkdta.ado opens the file,"
	display "runs checks if it is sorted, checks if the sort variables,"
	display "form a valid key, and outputs to this log."
	display ""
	display "Start folder: `startfolder'"
	display "=========================================================="
	display ""
	display ""
	quietly: cap log close  _all
		
	* Estimate memory requirments using MAXMEM program, and set memory with return value
	* Also pass return value to a local so RUNCHECKS program will accept it
	maxmem
	clear
	set mem `r(maxfsize)'
	local maxfsize = `r(maxfsize)'

	* Loop over list dta files saved by make.bat
	file open filelist using "..\temp\filelist.txt", text read
	file read filelist line
	while r(eof)==0  {
		if `"`line'"' != ""{
			* Convert Absolute Path to Relative Path
			local outputpath: pwd
			local outputpath = substr("`outputpath'",1,length(`"`outputpath'"')- strpos(reverse(`"`outputpath'"'),"\"))
			local relativepath = subinstr(`"`line'"',"`outputpath'","..",1)
			
			* Run checks on file
			runchecks using "`relativepath'", memory(`maxfsize')
		}
		* Move on to next line
		file read filelist line
	}
	file close filelist
	quietly: log close _all
end
checkdta
