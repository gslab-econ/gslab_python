*! 2.5.0  26feb2002
program define mmerge
	version 7
	
	capt noi mmerge_wrk `0'	
	local rc = _rc
	exit `rc'
end


program define mmerge_wrk, rclass
	
	syntax varlist using/ [, SImple TAble Type(str) UNMatched(str) /*
	  */ Missing(str) noSHow noLabel replace update _merge(str)    /*
	  */ UKeep(str) UDrop(str) UIF(str) UMatch(str) URename(str)   /*
	  */ UName(str) ULabel(str) ]

	if "`simple'" != "" {
		OptionNo `"`table'"'     "table not allowed with simple"
		OptionNo `"`type'"'      "type() not allowed with simple"
		OptionNo `"`unmatched'"' "unmatched() not allowed with simple"
		local type 1:1
		local unmatch both
	}
	else if "`table'" != "" {
		OptionNo `"`type'"'      "type() not allowed with table"
		OptionNo `"`unmatched'"' "unmatched() not allowed with table"
		local type n:1
		local unmatch master
	}
	else {
		EnumOpt `"`type'"'  "Auto 1:1 1:n n:1 n:n SPread"  "type"
		local type `r(option)'

		EnumOpt `"`unmatched'"'  "Both Master Using None"  "unmatched"
		local unmatch `r(option)'
	}

	EnumOpt `"`missing'"'  "None Value Nomatch"  "missing"
	local missing `r(option)'


	if `"`ukeep'"' != "" & `"`udrop'"' != "" {
		dis as err "options udrop() and ukeep() may not be combined"
		exit 198
	}
	if "`replace'" != "" & "`update'" == "" {
		dis as err "option replace can only be specified " /* 
		  */ "in combination with option update"
		exit 198
	}
	if `"`uname'"' != "" & `"`urename'"' != "" {
		dis as err "options uname() and urename() may not be combined"
		exit 198
	}

	if `"`_merge'"' == "" {
		local _merge _merge
	}


* prepare master

	cap drop `_merge'
	qui compress
	unab mmatch : `varlist'
	local nmmatch : word count `mmatch'

	* IsKey verifies that the key in the master is proper and 
	* leaves the data sorts on the match vars.
	IsKey "`mmatch'" "`missing'"
	local mkey   `r(iskey)'
	local merror `r(error)'

	if inlist("`type'", "1:1", "simple", "1:n") & `mkey' == 0 {
		dis as err "match-var in master should form a key"
		if "`merror'" == "dup" {
			dis as err "duplicate values in match-var(s)"
			ShowDup "`mmatch'"
			exit 4002
		}
		else {
			* merror == missing
			dis as err "missing values in match-var(s)"
			exit 4001
		}
	}

	qui descr, short
	local m_obs = r(N)
	local m_var = r(k)

	unab mvar : _all
	DropList "`mvar'" "`mmatch'"
	local mvar `r(list)' /* variables in master, excluding match vars */

	if "`missing'" == "nomatch" {
		/* algorithm note:
		   to avoid matching on missing values, I generate an extra
		   match variable (temovar missvar) that is 0 if non-missing, 
		   1 if missing in the master data and -1 in the using data
		*/
		tempvar missvar
		gen byte `missvar' = 1
		markout `missvar' `mmatch', strok
		qui replace `missvar' = 1 - `missvar'
		sort `mmatch' `missvar'
	}
	else 	sort `mmatch'


* prepare -using- file, store it as tempfile UseOk

	preserve
	
	* name for match vars in using data
	local Umatch = cond(`"`umatch'"'!="", `"`umatch'"', "`mmatch'")

	if `"`uif'"' != "" {
		local Uif `"if `uif'"'
	}

	if `"`udrop'"' == "" & `"`ukeep'"' == "" {
		qui use `Uif' using `"`using'"' , replace
		confirm var `Umatch' 
	}
	else if "`ukeep'" != "" {
		qui use `Uif' using `"`using'"' , replace
		keep `Umatch' `ukeep'
	}
	else {
		qui use in 1 using `"`using'"' , replace
		confirm var `Umatch'
		unab varuse : _all
		DropList "`varuse'" `"`udrop'"'
		keep `Umatch' `r(list)'
		unab varuse : _all
		qui use `varuse' `Uif' using `"`using'"' , replace
	}

	qui compress
	cap drop `_merge'

	* verify that umatch exist and is key in using data
	
	if `"`umatch'"' != "" {
		unab umatch : `umatch'
		local numatch : word count `umatch'
		if `nmmatch' != `numatch' {
			dis as err /*
			  */ "#match-variables in master and using data should be equal"
			exit 4003
		}
		local Umatch `umatch'
	}
	else {
		unab tmp : `mmatch'
		if "`tmp'" != "`mmatch'" {
			dis as err "match vars `mmatch' do not occur {it:as such} in using data"
			exit 4007
		}
	}

	IsKey `"`Umatch'"'  "`missing'"
	local ukey   `r(iskey)'
	local uerror `r(error)'

	if inlist("`type'", "1:1", "simple", "n:1") & `ukey'==0 {
		dis as err "match-var in using data should form a key"
		if "`uerror'" == "dup" {
			dis as err "duplicate values in match-var(s)"
			if "`type'" == "n:1" {
				dis as err "Maybe you matched up types n:1 and 1:n"
			}
			ShowDup `"`Umatch'"'
			exit 4002
		}
		else {
			* uerror == missing
			dis as err "error: missing values in match-var(s)"
			exit 4001
		}
	}

	* rename key variables in -using- to -mmatch-
	if `"`umatch'"' != "" {
		forvalues i = 1 / `nmmatch' {
			local v : word `i' of `mmatch'
			local u : word `i' of `umatch'
			RenameVar "`u'" "`v'"
		}
		sort `mmatch'
	}


	/* rename non-match variables and modify labels in using data
	   note that, at this point, the match-vars are in -mmatch-
	*/

	if `"`uname'"' != "" {
		PrefName `"`uname'"' "`mmatch'"
	}

	if `"`urename'"' != "" {
		Rename `"`urename'"'
	}

	if "`ulabel'" != "" {
		PrefLab `"`ulabel'"' "_all"
	}

	* statistics of the using data

	local fusing `"$S_FN"'
	qui descr, short
	local u_obs = r(N)
	local u_var = r(k)

	unab uvar : _all
	DropList "`uvar'" `"`mmatch'"'
	*DropList "`uvar'" `"`mvar' `mmatch'"'
	local uvar `r(list)'

	if "`missing'" == "nomatch" {
		confirm new var `missvar' 
		gen byte `missvar' = 1
		markout `missvar' `mmatch', strok
		* note: different coding as in master to prevent match
		qui replace `missvar' = -1 + `missvar'
		sort `mmatch' `missvar'
	}

	tempfile UseOk
	qui save `"`UseOk'"'

	* bring master is back in memory again
	restore
	

* verify consistency type() and (mkey,ukey)

	if "`type'" == "spread" & `mkey'+`ukey' == 0 {
		dis as err "matchvars should be key in master or using data"
		exit 4006
	}
	if "`type'" == "auto" & `mkey'+`ukey' == 0 {
		local type n:n
	}


* header describing files

	if "`show'" == "" {
	
		di
		dis "{txt}{hline 21}{c TT}{hline 57}"
		dis "{txt}{hi:merge specs}          {c |}"
		dis "{txt}       matching type {c |} {res}`type'"
		dis "{txt}  mv's on match vars {c |} {res}`missing'"
		dis "{txt}  unmatched obs from {c |} {res}`unmatch'"
		dis "{txt}{hline 21}{c +}{hline 57}"

	    * master
	    
		local fmaster `"$S_FN"'
		if `"`fmaster'"' == "" {
			local fmaster "<data in memory not named>"
		}
		else {
			* !! _shortenpath `"`fmaster'"', width(56)
			* !! local fmaster `"`r(pfilename)'"'
		}
		local mkeytxt = cond(`mkey',"(key)", "(not a key)")
	
		dis `"{txt}  {hi:master}        file {c |} {res}`fmaster'"'
		dis `"{txt}{ralign 20:obs} {c |} {res}"'  %6.0f `m_obs'
		dis `"{txt}{ralign 20:vars} {c |} {res}"' %6.0f `m_var'
		WrapTxt "match vars" `"`mmatch'"' "`mkeytxt'"
		dis "{txt}  {hline 19}{c +}{hline 57}"		  

	    * using
	    
		* !! _shortenpath `"`fusing'"', width(56)
		* !! local fusing `"`r(pfilename)'"'
		if `"`uif'"' != "" {
			local iftxt `"  (selection: `uif')"'
		}
		if `"`udrop'`ukeep'"' != "" {
			local vartxt `"  (selection via udrop/ukeep)"'
		}
		local ukeytxt =cond(`ukey',"(key)", "(not a key)")
		
		dis `"{txt}  {hi:using}         file {c |} {res}`fusing'"'
		dis `"{txt}{ralign 20:obs} {c |} {res}"' /*
		  */ %6.0f `u_obs' `"{txt}`iftxt'"'
		dis `"{txt}{ralign 20:vars} {c |} {res}"' /*
		  */ %6.0f `u_var' `"{txt}`vartxt'"'
		WrapTxt "match vars" `"`Umatch'"' "`ukeytxt'"

	    * common vars
	    
	    	GetCommon "`uvar'"
	    	local commonvar `r(common)'
	    	if "`commonvar'" != "" {
			dis "{txt}  {hline 19}{c +}{hline 57}"
			WrapTxt "common vars" "`commonvar'"
		}
		dis "{txt}{hline 21}{c +}{hline 57}"
	}


* actually merge -master- and -using- via internal command -merge- (fast) 
* or the ado-coded command -joinby- (slower)

	if "`type'" != "n:n" {
		if inlist("`unmatch'", "none", "master") { 
			local keep nokeep		
		}
		merge `mmatch' `missvar' using `"`UseOk'"' , /*
		  */ `label' `keep' `replace' `update' _merge(`_merge')
	}
	else {
		joinby `mmatch' `missvar' using `"`UseOk'"' , /*
		  */ `label' `keep' `replace' `update' _merge(`_merge') /*
		  */ unmatched(`unmatch')
	}
	
	if "`missvar'" != "" {
		drop `missvar'
	}
	nobreak DefLabel `_merge' `update'
		
	if "`missing'" != "value" {
		tempvar notmiss
		gen byte `notmiss' = 1
		markout `notmiss' `mmatch', strok
		qui replace `_merge' = - `_merge' /*
		  */ if (`_merge'==1 | `_merge'==2) & `notmiss'==0
	}
	
	if "`type'" == "simple" {
		cap assert `_merge' == 3
		if _rc {
			dis as err "unmatched obs not permitted with type==simple"
			tab `_merge'
			exit 4005
		}
	}
	
	if "`unmatch'" == "none" | "`unmatch'" == "using" {	
		cap drop if `_merge' == 1
	}
	
	
* report results

	if "`show'" == "" {
		qui descr
		dis `"{txt}{hi:result}          file {c |} {res}`fmaster'"'
		dis `"{txt}{ralign 20:obs} {c |} {res}"' %6.0f r(N)
		dis `"{txt}{ralign 20:vars} {c |} {res}"' %6.0f r(k) /*
		  */ "{txt}  (including `_merge')"
		
		MergeReport `_merge'
		dis "{txt}{hline 21}{c BT}{hline 57}"
	}
	

* return values

	return local  mfile   `fmaster'
	return local  mmatch  `mmatch'
	return scalar mvar    = `m_var'
	return scalar mobs    = `m_obs'
	return scalar mkey    = `mkey'

	return local  ufile   `fusing'
	return local  umatch  `Umatch'
	return scalar uvar    = `u_var'
	return scalar uobs    = `u_obs'
	return scalar ukey    = `ukey'

	return local  common  `uvar'
end


/* 
   ==========================================================================
   subroutines
   ==========================================================================
*/

/* OptionNo value text
   displays errror message -text- if value is defined
*/
program define OptionNo
	args value text
	
	if `"`value'"' != "" {
		dis as err `"`text'"'
		exit 198
	}
end


/* GetCommon "varlist"

   returns in r(common) the variables in -vlist- (expanded varlist) 
   that also occur (as such, ie, not abbreviated) in the data in memory.
*/
program define GetCommon, rclass
	args vlist

	foreach v of local vlist {
		local 0 `v'
		capture syntax varname 
		if !_rc & "`v'" == "`varlist'" {
			local common `common' `v'
		}
	}
	return local common `common'
end


/* WrapTxt htxt asres astxt

   Writes a hanging indent in columns 1..20, then a line, followed by asres 
   (wrapped if necessary) in columns 24..79 in -as res- style, followed by
   astxt (not wrapped) in -as txt- style.
   
   Assumptions |header|<=20, |astxt|<=56
*/
program define WrapTxt
	args htxt asres astxt
	
	if `"`astxt'"' == "" {
		local ip 1
		while 1 {
			local lpiece : piece `ip' 56 of `"`asres'"'	
			if `"`lpiece'"' != "" {
				dis `"{txt}{ralign 20:`htxt'} {c |} {res}`lpiece'"'
				local htxt
			}
			else 	exit
			local ip = `ip' + 1
		}	
	}
	
	* we now know that -asres- is non-empty
	dis `"{txt}{ralign 20:`htxt'} {c |} "' _c
	
	if length(`"`asres'"') <= 56 {
		if length(`"`asres'  `astxt'"') > 56 {
			dis `"{res}`asres'"'
			dis `"{txt}{col 21} {c |} `astxt'"'
		}
		else	di `"{res}`asres'  {txt}`astxt'"'
		exit
	}	

	* we now know that we have to wrap -asres-
	local lpiece1 : piece 1 56 of `"`asres'"'
	dis `"{res}`lpiece1'"'
	
	* one piece look-ahead in lpiece2
	local lpiece1 : piece 2 56 of `"`asres'"'
	local ip 3
	while 1 {
		local lpiece2 : piece `ip' 56 of `"`asres'"'	
		if `"`lpiece2'"' == "" { 
			if length(`"`lpiece1'  `astxt'"') > 56 {
				dis `"{txt}{col 21} {c |}{res} `lpiece1'"'
				dis `"{txt}{col 21} {c |}{txt} `astxt'"'
			}
			else	dis `"{txt}{col 21} {c |}{res} `lpiece1'  {txt}`astxt'"'
			continue, break
		}
		dis `"{txt}{col 21}{c |} {res}`lpiece1'"'
		
		local lpiece1 `"`lpiece2'"'
		local ip = `i'+1
	}
end


/* RenameVar u v

   renames u to v 
*/   
program define RenameVar			
	args u v
	
	if "`u'" == "`v'" { exit }
	cap rename `u' `v'
	if _rc {
		dis as err "failure renaming `u' to `v' in using data"
		exit 4004
	}
end	


/* Rename speclst

   renames variables according to a specification
     oldname newname \ oldname newname ...
*/
program define Rename
	args speclst
	
	gettoken r rest : speclst, parse("\")
	while `"`r'"' != "" {
		if `"`r'"' != "\" {
			local r1 : word 1 of `r'
			local r2 : word 2 of `r'
			RenameVar `r1' `r2'
		}
		gettoken r rest : rest, parse("\")
	}
end


/* PrefName str skiplst
   prefixes str to the names of all variables in the data,
   expect those in skiplst
*/
program define PrefName
	args str skiplst

	foreach v of varlist _all {
		local tmp : subinstr local skiplst "`v'" "", /*
		  */ word count(local nch)
		if `nch' == 0 {
			local nname = substr(`"`str'`v'"', 1, 32)
			RenameVar `v' `nname'
		}
	}
end


/* DropList list droplst
   returns in r(list) the input list, without the words in droplst
*/
program define DropList, rclass
	args list droplst

	tokenize "`droplst'"
	local i 1
	while "``i''" != "" & `"`list'"' != "" {
		local list : subinstr local list "``i''" "" , word all
		local i = `i'+1
	}
	return local list `list'
end


/* PrefLab name varlist
   prefixes "name: " to the variable labels of the vars in varlist
*/
program define PrefLab
	args name vlist

	foreach v of varlist `vlist' {
		local vl : var label `v'
		lab var `v' `"`name': `vl'"'
	}
end


/* ShowDup key
   list obs with duplicate key values
*/
program define ShowDup
	args key

	tempvar X
	sort `key'
	qui by `key' : gen `X' = cond(_N==1, 0, _n==1)
	qui by `key' : gen __FREQ = _N
	dis _n as txt "Non-unique key values"
	list `key' __FREQ if `X', noobs
end


/* IsKey varlist missing

   returns in r(iskey) whether varlist is a key.  If missing is -none-, 
   it is verified that the varlist is never missing.

   As a side-effect, the data are sorted on the varlist
*/
program define IsKey, rclass
	args varlist missing

	if "`missing'" == "none" {
		tempvar M
		gen byte `M' = 1
		markout `M' `varlist', strok
		capture assert `M'==1
		if _rc {
			return local iskey 0
			return local error missing
			exit
		}
	}

	capture bys `varlist' : assert _N==1
	if _rc {
		return local iskey 0
		return local error dup
	}
	else 	return local iskey 1
end


/* EnumOpt input spec optname

   returns in r(option) the parsed specification of option optname
*/  
program define EnumOpt, rclass
	args input spec optname

	if `"`spec'"' == "" | `"`optname'"' == "" {
		exit 198
	}

	tokenize `"`spec'"'
	if `"`1'"' == "." {
		* default is empty
		mac shift
	}
	else 	local dflt = lower(`"`1'"')

	if `"`input'"' == "" {
		return local option `dflt'
		exit
	}

	local len = length(`"`input'"')
	while `"`1'"' != "" {
		local l1 = lower(`"`1'"')
		if `"`l1'"' == `"`1'"' {
			* all lower-case values should match fully
			local lf = length(`"`1'"')
		}
		else {
			FirstLowerCase `"`1'"'
			local lf = `r(index)'-1
		}
		if `"`input'"' == substr(`"`l1'"', 1, max(`len',`lf')) {
			return local option `"`l1'"'
			exit
		}
		mac shift
	}
	dis as err `"`input' invalid for `optname'(`spec')"'
	exit 198
end


/* FirstLowerCase str
   returns in r(index) the index of the first lowercase char in str,
   or length(str)+1 otherwise
*/
program define FirstLowerCase, rclass
	args str

	local i 1
	while `i' <= length(`"`str'"') {
		local c = substr(`"`str'"', `i', 1)
		if "`c'" == upper("`c'") {
			local i = `i'+1
		}
		else {
			return local index `i'
			exit
		}
	}
	return local index `i'
end


/* DefLabel _merge update

   defines value labels for _merge, depending whether update-merging was
   specified. DefLabel takes care to ensure that the value label __MERGE
   does not exist, or was actually generated by mmerge, and hence may be
   overwritten (I used a signature method).
*/
program define DefLabel
	args _merge update

	cap label list __MERGE
	if !_rc {
		local lab : label __MERGE 9999
		if "`lab'" == "signature" {
			label drop __MERGE
		}
		else {
			dis as txt "(value label __MERGE for `_merge' already exists)"
			exit
		}
	}

	if "`update'" == "" {
		#del ;
		label def __MERGE
		    -1  "matchvar==missing in master data"
		     1  "only in master data"
		    -2  "matchvar==missing in using data"
		     2  "only in using data"
		     3  "both in master and using data"
 		  9999  "signature" ;
		#del cr
	}
	else {
		#del ;
		label def __MERGE
		    -1  "matchvar==missing in master data"
		     1  "only in master data"
		    -2  "matchvar==missing in using data"
		     2  "only in using data"
		     3  "in both, master agrees with using data"
		     4  "in both, missing in master data updated"
		     5  "in both, master disagrees with using data"
		  9999  "signature" ;
		#del cr
	}
	label val `_merge' __MERGE
end


/* MergeReport v

   writes a report on the _merge-variable v
*/   
program define MergeReport
	args v

	local abv = abbrev("`v'",16)
	
	local labv = 2 + max(length("`abv'"),10)
	local col  = 22-`labv'
	dis _col(`col') "{txt}{hline `labv'}{c +}{hline 57}"
	
	local first 1
	forvalues iv=-2/5 {
		qui count if `v'==`iv'
		local n = r(N)
		if `n' == 0 { continue }
		
		local lab : label (`v') `iv'
		if `first' {
			dis as txt "{ralign 20:`abv'}" _c
			local first 0
		}
		else	dis _col(21) _c
		
		dis "{txt} {c |}{res} " %6.0f `n' /*
		  */ "{txt}  {lalign 37:obs `lab'} {ralign 10:(code==`iv')}"
	}		
end

exit

error messages

  4001  improper key : missing values
  4002  improper key : duplicate values
  4003  number of key variables in master and using are not equal
  4004  impossible to rename in using data
  4005  unmatched obs not permiited with type==simple
  4006  matchvars should be key in master or using data
  4007  keyvars should be specified unabbreviately
          
