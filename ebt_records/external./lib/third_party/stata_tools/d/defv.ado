*!  Version 1.1.3 <06Mar1999>  STB-51 dm50.1
program define defv
*!  Define (generate or replace) variables and record their definition
*!  Syntax:
*!    . defv [by varlist:] [type] newvar [: lblname] = exp [if exp] [in range]
*!    . defv [by varlist:] oldvar = exp [if exp] [in range] [, nopromote]
*!    . defv oldvar ?
**  Author:  John R. Gleason (loesljrg@accucom.net)

   version 6.0

   global d_V "note"
*  to record definitions so that they are distinct from notes,
*  remove the asterisk (*) from the next line:
*   global d_V "defV"

   if `"`1'"' == "?" {
      which defv
      exit
   }
   if `"`2'"' == "?" {
      xx `1'
      exit
   }

   tokenize `"`0'"', parse(":")
   if "`2'" == ":" {
      local 0 `"`3'"'
      local B `1'`2'
   }
   local eq = index(`"`0'"', "=")
   if substr(`"`0'"', `eq'-1, 1) == " " { local eq = `eq' - 1 }
   local sp = index(`"`0'"', " ")
   if `sp' >= `eq'  { local sp 1 }
   local V = trim(substr(`"`0'"', `sp', `eq'-`sp'))

   local op "`B' generate"
   qui capture confirm new var `V'
   if _rc == 110 {
      local op "`B' replace"
      local j : char `V'[${d_V}0]
   }
   else if _rc { error _rc }
   local j = cond("`j'" == "", 1, `j'+1)

   nobreak {
      `op' `0'
      char `V'[${d_V}0] `j'
      char `V'[${d_V}`j'] `op' `0'
   }
end



program define xx
   local varlist "req ex"
   parse `"`*'"'

   local j : char `1'[${d_V}0]
   if "`j'" != "" {
      di in ye "`1':"
      local i 1
      while `i' <= `j' {
         local b : char `1'[${d_V}`i']
         if `"`b'"' != "" { di in gr %4.0g "  `i'.", `"`b'"' }
         local i = `i' + 1
      }
   }
end
