*! version 1.0.3 TJS NJC 17sep2001 Added -verbose- option
*  version 1.0.2 TJS NJC  8jan1999 (1.0.1 in STB-41 dm53)
program define dups
  version 6.0
  syntax [varlist], [ DROP Expand(str) Key(str) Unique Terse Verbose Example]
 
* convert switches to logicals
  local drop    = "`drop'"    == "drop"
  local unique  = "`unique'"  == "unique"
  local terse   = "`terse'"   == "terse"
  local verbose = "`verbose'" == "verbose"
  local example = "`example'" == "example"
  
* if verbose, check for key()
  if `verbose' & "`key'" == "" {
     di in re "key() required when verbose requested"
     exit
  }   

* if requested, create expand variable (or error message)
  if `drop' {
    if "`expand'" == "" { local expand "_expand" }
    confirm new variable `expand'
  }

* if requested, do wildcard substitution of varlist for varlist2
  if "`key'" == "*" { local key "`varlist'" }
* if exists, unabbreviate key
  if "`key'" != ""  { 
     cap noi unab key: `key'
     if _rc {
        local oldrc = _rc
        di as err "   --- in key()"
        exit `oldrc'    
     }
  }
  
  tempvar recnum first ldup ldup1

* obtain existing sort order
  local sortby: sortedby
  quietly generate long `recnum' = _n

* reorder data and list grouping variables
  sort `varlist' `recnum'
  display _n in gr "group by:" in ye " `varlist'"

* obtain varnames for group and count
  Chkvname _group _grp group
  local group "`varname'"
  Chkvname _count _cnt count
  local count "`varname'"

* do calculations
  quietly generate long `group' = .
  quietly by `varlist': generate long `count' = _N
  quietly by `varlist': generate byte `first' = _n==1
  quietly count if `count' > 1 & `first'
  local ngrps = r(N)
  quietly count if `first'
  local uniq = r(N) - `ngrps'

  display _n in gr "groups formed: " in ye `ngrps' _c
  if ~`terse' { 
    display in gr " containing " in ye _N - `uniq' in gr " observations" 
    display in gr "unique observations: " in ye `uniq'
  } 

* if requested, display full information on duplicates
  if `ngrps' > 0 & ~`terse' {
    generate byte `ldup' = `count' > 1 & `first'
    gsort -`ldup' `varlist'
    quietly replace `group' = _n
    display _n _c in gr "groups of duplicate observations:"
    if ~`verbose' { list `group' `count' `key' if `ldup', noobs }
    *   if requested, display verbose details of groups 
    else {
       local nf = int(log10(_N)) + 2
       local nf1 = `nf' + 2
       tempvar dupgrp
       qui egen `dupgrp' = group(`varlist'), missing
       gsort `dupgrp' `recnum'
       local i = 1
       while `i' <= _N {
          if `first'[`i'] & `count'[`i'] > 1 { 
             tokenize `varlist'
             di _n in gr "-> `1' = " `1'[`i'] _c
             local j = 2
             while "``j''" != "" {
                di in gr ", ``j'' = " ``j''[`i'] _c
                local j = `j' + 1
             }
             tokenize `key'
             di _n in gr _d(`nf1') " " _c
             local j 1
             while "``j''" != "" {
                local vf: format ``j''
                _fmt `vf'
                if r(dash) { local dsh = "-" }
                else       { local dsh = "" }
                local skp = ""
                if r(skp)  { local skp = "_s(1)" }
                local mlngth = r(lngth)
                local alngth= length("``j''")
                if `alngth' <= `mlngth' - 1 { local vl = "``j''" }
                else { local vl = substr("``j''", 1, `mlngth' - 2) + "*" }
                di in gr `skp' %`dsh'`mlngth's "`vl'"  _c
                local j = `j' + 1
             }
          }
          local j 1
          if `count'[`i'] > 1 { 
             di _n in gr %`nf'.0f `recnum'[`i'] ". " _c
             while "``j''" != "" {
                local vf: format ``j''
                local skp = ""
                if substr("`vf'", 2, 1) == "-" { local skp = "_s(1)" }
                if substr("`vf'", 2, 1) == "d" { local skp = "_s(1)" }
                di in ye `skp' `vf' ``j''[`i'] _c
                local j = `j' + 1
             }
          }
          local i = `i' + 1
       }
       if `example' { di }
    }
    if `example' {
       display _n _c in gr "examples of duplicate observations:"
       sort `recnum'
       list `group' `count' `varlist' if `count' > 1 & `first'  
    }
  }

* if requested, display full information on unique observations
  if `unique' & ~`terse' {
    generate byte `ldup1' = `count' == 1 & `first'
    gsort -`ldup1' `varlist'
    quietly replace `group' = _n
    display _n _c in gr "unique observations:"
    list `group' `count' `key' if `ldup1', noobs
  }

* if requested, display terse output
  if `ngrps' > 0 & `terse' {
    display _n _n in gr "total observations:" in ye %5.0f _N
    display       in gr "  in duplicates    " in ye %5.0f _N - `uniq'
    display       in gr "  in unique        " in ye %5.0f `uniq'
  }

* if requested, drop duplicates
  if `drop' {
    nobreak {
      sort `varlist'
      display
      quietly by `varlist': generate long `expand' = _N     
      keep if `first'
      display _n in gr "observations remaining: " in ye _N
    }
  }

* restore prior sort order
  sort `sortby' `recnum'
  drop `group' `count'
end


program define Chkvname
* version 1.0.0 NJC 14aug1997
* version 1.0.1 TJS 15aug1997
* 1.0.2 NJC 14sep2001 
/* args:
         `1' -- name to try first
         `2' -- name to try second
         `3' -- generic name
*/
    version 6.0
    args first second generic 
    capture confirm variable `first'
    if _rc != 0 { c_local varname "`first'" }
    else {
        display _n in bl "warning: `first' already defined"
        capture confirm variable `second'
        if _rc != 0 { c_local varname "`second'" }
        else {
            display in bl "warning: `second' already defined"
            local varname : tempvar
            tempvar varname
            display in bl "   note: `generic' variable is now" in wh " `varname'"
            c_local varname "`varname'" 
        }
    }
end


program define _fmt, rclass
*  version 1.0.0  17sep2001  TJS
*  returns # of print characters from a format
version 6
local fmt `1'
* use format to define _skip() spacing for column headers
local skp = 0
local t = substr("`fmt'", 2, 1)
local dash = 0
if "`t'" == "-" {      /* left justified  */
   local dash = 1
   local t = substr("`fmt'", 3, 1)
   local skp = 1
}
if "`t'" == "d" {      /* date formats    */
   _dl `fmt'
   local vdig = r(lngth)
   local skp = 1
}
if "`t'" == "t" {      /* time-series     */
   _tl `fmt'
   local vdig = r(lngth)
}
if "`t'" != "t" & "`t'" != "d" {  
/* numeric & strings */
   local vdig = index("`fmt'", ".")
   if `vdig' == 0 { local vdig = length("`fmt'") }
   local vdig = real(substr("`fmt'", 2 + `dash', /*
                       */   `vdig' - 2 - `dash'))
}  
global S_1 = `vdig'
return scalar lngth = `vdig'
global S_2 = `skp'
return scalar skp = `skp'
global S_3 = `dash'
return scalar dash = `dash'
end


program define _dl, rclass
*  version 1.0.0  3jun1999  TJS
*  returns # of print characters from a date format
version 6
local fmt `1'
local t = substr("`fmt'", 2, 1)
local dash = 0  /* left justification ? */
if "`t'" == "-" { local dash = 1 } 
local len = length("`fmt'")

local i = 3 + `dash' 
local c 0
while `i' <= `len' {
   local k = substr("`fmt'", `i' ,1)
   if      "`k'" == "!" {
                          local c = `c' + 1
                          local i = `i' + 1
                        }
   else if "`k'" == "c" { local c = `c' + 2 }
   else if "`k'" == "C" { local c = `c' + 2 }
   else if "`k'" == "y" { local c = `c' + 2 }
   else if "`k'" == "Y" { local c = `c' + 2 }
   else if "`k'" == "m" { local c = `c' + 3 }
   else if "`k'" == "M" { local c = `c' + 9 }
   else if "`k'" == "l" { local c = `c' + 3 }
   else if "`k'" == "L" { local c = `c' + 9 }
   else if "`k'" == "n" { local c = `c' + 2 }
   else if "`k'" == "N" { local c = `c' + 2 }
   else if "`k'" == "d" { local c = `c' + 2 }
   else if "`k'" == "D" { local c = `c' + 2 }
   else if "`k'" == "j" { local c = `c' + 3 }
   else if "`k'" == "J" { local c = `c' + 3 }
   else if "`k'" == "w" { local c = `c' + 2 }
   else if "`k'" == "W" { local c = `c' + 2 }
   else                 { local c = `c' + 1 }
   local i = `i' + 1
}

if `c' == 0 { local c 9 }  /* handle default %d */

global S_1 = `c'
return scalar lngth = `c'
end


program define _tl, rclass
*  version 1.0.0  3jun1999  TJS
*  returns # of print characters from a time-series format
version 6
local fmt `1'
local t = substr("`fmt'", 2, 1)
local dash = 0  /* left justification ? */
if "`t'" == "-" { local dash = 1 }
local t = substr("`fmt'", 3 + `dash', 1)
local len = length("`fmt'")

local i = 4 + `dash' 
local c 0
while `i' <= `len' {
   local k = substr("`fmt'", `i' ,1)
   if      "`k'" == "!" {
                          local c = `c' + 1
                          local i = `i' + 1
                        }
   else if "`k'" == "c" { local c = `c' + 2 }
   else if "`k'" == "C" { local c = `c' + 2 }
   else if "`k'" == "y" { local c = `c' + 2 }
   else if "`k'" == "Y" { local c = `c' + 2 }
   else if "`k'" == "m" { local c = `c' + 3 }
   else if "`k'" == "M" { local c = `c' + 9 }
   else if "`k'" == "l" { local c = `c' + 3 }
   else if "`k'" == "L" { local c = `c' + 9 }
   else if "`k'" == "n" { local c = `c' + 2 }
   else if "`k'" == "N" { local c = `c' + 2 }
   else if "`k'" == "d" { local c = `c' + 2 }
   else if "`k'" == "D" { local c = `c' + 2 }
   else if "`k'" == "j" { local c = `c' + 3 }
   else if "`k'" == "J" { local c = `c' + 3 }
   else if "`k'" == "w" { local c = `c' + 2 }
   else if "`k'" == "W" { local c = `c' + 2 }
   else                 { local c = `c' + 1 }
   local i = `i' + 1
}

if `c' == 0 {  /* handle default %t_ formats */
   if "`t'" == "d" { local c 9 }
   if "`t'" == "w" { local c 7 }
   if "`t'" == "m" { local c 7 }
   if "`t'" == "q" { local c 6 }
   if "`t'" == "h" { local c 6 }
   if "`t'" == "y" { local c 4 }
   if "`t'" == "g" { local c 9 }
}

global S_1 = `c'
return scalar lngth = `c'
end
