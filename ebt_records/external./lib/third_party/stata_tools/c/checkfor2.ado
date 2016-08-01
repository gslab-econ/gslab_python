*!Data management utility: check for existence of variables in a dataset.
*!Version 1.1 by Amadou B. DIALLO.
*!This version 1.2 . Updated by Amadou B. DIALLO and Jean-Benoit HARDOUIN.
*!Authors: Amadou Bassirou DIALLO (Poverty Division, World Bank) and Jean-Benoit HARDOUIN (Regional Health Observatory of Orléans).

program checkfor2 , rclass
version 8
syntax anything [if] [in] [, noList Tolerance(real 0) TAble noSUm GENMiss(namelist min=1 max=1) MISsing(string)]

marksample touse
tempname rat
local av
local unav
local manymissings
local avnum

quietly count if `touse'
local tot = r(N)

qui isvar `anything'
local badlist `r(badlist)'
local varlist `r(varlist)'

di _n
if "`table'"!="" {
   if "`badlist'"!="" {
      di _col(4) in green "{hline 39}"
      di _col(4)in green "Unavailable variables: " 
      foreach i of local badlist {
        di _col(4) in ye "`i'" 
      }
      di _col(4) in green "{hline 39}"
      di
   }
   di _col(4) in green "{hline 39}"
   display _col(4) in gr "Existing" _col(15) in gr "Rate of"
   display _col(4) in gr "Variable"  _col(14) "missings" _col(26) "Type" _col(34) "Available"
   di _col(4) in green "{hline 39}"
}

tokenize `varlist'
local nbvar : word count `varlist'

forvalues i=1/`nbvar' {
   capture assert missing(``i'')  if `touse'
      local ty: type ``i''
      local tty = substr("`ty'", 1, 3)
      if !_rc { 
             if "`table'"=="" {
                 display in ye "``i''" in gr " is empty in the database." in ye " ``i''" in gr " is not added to the available list."
             }
             else {
                 display _col(4) in gr "`=abbrev("``i''",8)'" _col(15) in ye "100.00%"  _col(26) "`ty'"
             }
             local manymissings `manymissings' ``i''
      }
      else { 
             if "`table'"=="" {
                display in ye "``i''" in gr " exists and is not empty."
             }
             *Consider type
             if "`tty'" == "str" {
               qui count if (``i'' == ""|``i''=="`missing'") & `touse'
               local num = r(N)
               scalar `rat' = (`num'/`tot')*100
              }
             else {
               local avnum `avnum' ``i''
               capture confirm number `missing'
               if _rc!=0 {
                  quietly count if ``i'' >= . & `touse'
               }
               else  {
                  quietly count if (``i'' >= .|``i''==`missing') & `touse'
               }
               local num = r(N)
               scalar `rat' = (`num'/`tot')*100
              }
              if "`table'"=="" {
                  display in ye "``i''" in gr " has " in ye r(N) in gr " missings."
                  display in gr "Ratio number of missings of" in ye " ``i''" in gr " to total number of observations: " in ye %6.2f `rat' "%"
               }

               if `rat' <= `tolerance' {
                  local av `av' ``i''
                  if "`table'"=="" {
                     display in ye "``i''" in gr " is added to the available list."
                  }
                  else {
                     display _col(4) in gr "`=abbrev("``i''",8)'" in ye _col(15) %6.2f `rat' "%" _col(26) "`ty'" _col(34) "X"
                  }
               }
               else {
                  local manymissings `manymissings' ``i''
                  if "`table'"=="" {
                     display in ye "``i''" in gr " has too many missings, compared to the tolerance level."
                     display in ye "``i''" in gr " is not added to the available list."
                  }
                  else {
                     display _col(4) in gr "`=abbrev("``i''",8)'" _col(15) in ye %6.2f `rat' "%" _col(26) "`ty'"
                  }
               }
      }
      if "`table'"=="" {
          di
      }
}

if "`table'"!="" {
   di _col(4) in green "{hline 39}"
}

return local available `av'
return local unavailable `badlist'
return local manymissings `manymissings'

if "`avnum'" ~= ""&"`sum'"=="" {
   display _newline
   display in ye _col(14) "Unweighted summary statistics for available variables:" _n
   capture confirm number `missing'
   if _rc!=0 {
      summarize `avnum'  if `touse'
   }
   else {
      foreach i of local avnum {
         summarize `i'  if `touse'&`i'!=`missing'
      }
   }
}

if "`list'"== "" {
   display _newline
   display in ye _d(97) "_"
   display _newline
   if "`badlist'"~="" {
      display in gr "Unavailable variables: " in ye _col(45) "`badlist'" _n
   }
   if "`av'"~="" {
      display in gr "Available variables: " in ye _col(45) "`av'" _n
   }
   if "`manymissings'"~="" {
      display in gr "Available variables but with too missings: " in ye _col(45) "`manymissings'" _n
   }
   display in ye _d(97) "_"
}

if "`genmiss'" !="" {
   capture confirm variable `genmiss'
   if _rc!=0 {
      qui gen `genmiss' = 0
      local nbav : word count `av'
      tokenize `av'
      forvalues i=1/`nbav' {
          local ty: type ``i''
          local tty = substr("`ty'", 1, 3)
          if "`tty'" == "str" {
            qui replace `genmiss'=`genmiss'+1 if ``i''=="."
          }
          else {
            qui replace `genmiss'=`genmiss'+1 if ``i''>=.
          }
      }
   }
   else {
      di in green "The variable" in ye " `genmiss' " in green "already exists".
   }
}

end
