*nearmrg.ado - performs nearest match merges of nearvar within exact matches of optional varlist
*! version 2.1.1 E Booth Jan2011
** version 2.1.0 E Booth Oct2011
** version 2.0.1 M Blasnik Sep03 
** version 2.0.2 M Blasnik, K Smith Mar08
 

	
program define nearmrg
syntax [varlist(default=none)] using ,  ///
	Nearvar(varname numeric) [TYPE(str asis)] ///
	[LIMit(str asis) GENMATCH(str asis) LOWer UPper  ROundup   * ]
*--------------error checking
if !inlist(`"`type'"', "_n", "1:1", "m:1", "1:m", "m:m") {
	loc type "m:1"
	di in yellow `"Merge Type not or incorrectly specified. Type [m:1] assumed.  See {help merge} for more."'
	}
if `"`genmatch'"'!=`""' confirm new var `genmatch'
if `"`roundup'"'==`""' local eq = "="
if ((`"`lower'"'!=`""') + (`"`upper'"'!=`""') + (`"`roundup'"'!=`""'))>1 {
	di as err `"Cannot choose more than one of options {bf:roundup, lower, or upper}"'
	exit 198
 } //end.check.opts

*--------------specify varlist
local fullvars `"`varlist' `nearvar'"'
if `"`varlist'"' != `""' {
	local bycmd `"by `varlist': "'
}
**qui {
*--------------master/work dataset (order lookup)
tempvar order 
tempfile work
gen double `order'=_n

preserve
	keep `order' `fullvars' 
	save `work'
	*--------------using data
	use `fullvars' `using', clear
		*---error check: _dstr master data nearvar:
		 *cap confirm string var `nearvar'
		 *if _rc ==0  _dstr `nearvar' , `string' xx(`stringdate')
		 if mi(`nearvar') {
	 	  di as err `"`nearvar' contains non-numeric chars, cannot destring (if `nearvar' is a date, convert using time-date functions)"'
		  exit 198
		  }	
		*noi desc
	sort `fullvars'
	cap isid `fullvars'
	if _rc {
		di as err "Variables: `fullvars' not unique in using dataset"
		error 459
	}
	*--------------append master/work dataset to using
	append using `work'
	sort `fullvars'
	*--------------find nearest match first/last/merg/gen
	tempvar last next mrg gen
	clonevar `last'=`nearvar' if `order'==.
	clonevar `next'=`last'
	`bycmd' replace `last'=`last'[_n-1] if mi(`last')
	gsort `varlist' -`nearvar'
	`bycmd' replace `next'=`next'[_n-1] if mi(`next')
		//fix 'double' format condition//
			 cap confirm numeric var `nearvar'
			 noi di _rc
	
	if `"`lower'"' !=`""' gen double `gen'=cond(`nearvar'!=`next',`last',`next')
	if `"`upper'"' !=`""' gen double `gen'=cond(`nearvar'!=`last',`next',`last')
	if `"`upper'`lower'"' == `""' gen double `gen'=cond((`nearvar'-`last')<`eq'abs(`nearvar'-`next'),`last',`next')
	*----------------
	local tmpfmt: format `nearvar'
	format `gen' `tmpfmt'
	drop if `order'==.
	sort `order'
	keep `order' `gen'
	save `work', replace
	/* now get the matching values into original data */
restore

sort `order'
if `c(version)' <11 merge `order' using `work' , _merge(`mrg')
if `c(version)' >=11 merge `type' `order' using `work' , generate(`mrg')
cap drop `mrg'

/* now shuffle around the names to do the merge into the using dataset */
tempvar hold
rename `nearvar' `hold'
rename `gen' `nearvar'
sort `fullvars'
if `c(version)' <11 merge  `fullvars' `using' ,  `options'
if `c(version)' >=11 merge m:1 `fullvars' `using' ,  `options' 
rename `nearvar' `gen'
rename `hold' `nearvar'

*----------limit subprgm
	if `"`limit'"' != "" {
			tempvar diff
			gen `diff' =  abs(`gen' - `nearvar')
			keep if `diff'<=`limit'
		} //end.limit.subprgm
	

		if "`genmatch'"!="" {
			clonevar `genmatch'=`gen'
			local text `"`upper'`lower' "'
			if `"`fullvars'"' !="" local text2 ", matched on `varlist'"
			label var `genmatch' `"nearest `text'match to `nearvar' `text2'"'
		}  //end.genmatch.if
	
**} //end qui
end

*--destring subprgm--*
program define _dstr
syntax varlist, [string xx(str asis)]
if `"`string'"' != `""' & `"`stringdate'"' == ""  {
 cap confirm string var `varlist'
  if _rc!=0 	di as err `"`varlist' contains non-string variables"'
 cap confirm string var `varlist'
  if _rc==0  qui destring `varlist', replace force 
} //end string


end
	

/* NOTES
* v2.1.1  =  added limit to upper/lower match (e.g. within X number of days); updated to new merge syntax in Stata versions 11+; added TYPE option for merge type; added _dstr subprogram; (EAB)
* v2.1.0  - fixed double format for cond() statements; fixed string option; fixed merge syntax change; fixed stringdate format change; created new options (EAB)
* v2.0.2	- new variables now created in double precision.
*			- if genmatch() option specified, resulting variable is formatted to match nearvar.

*/
