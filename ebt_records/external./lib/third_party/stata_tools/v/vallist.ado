*! vallist: list distinct values of a variable
*! version 3.1   PJoly   13apr2003
* v.3.1.0 PJoly   13apr2003   allow reverse w/o sort or freq
* v.3.0.0 PJoly   05apr2003   allow various options
* v.2.3.0 NJC 10 Feb 2002
* v.2.2.1 NJC 2 Oct 2001
* v.2.2.0 NJC 3 January 2001
* v.2.1.1 NJC 8 November 2000
* v.2.1.0 NJC 20 Dec 1999
* v.2.0.1 NJC 4 Nov 1998
* v.1.2.0 NJC 8 Oct 1998
program define vallist, rclass sortpreserve
      version 7.0
      syntax varname [if] [in] [, noLabels MISSing Sep(str) Max(int 0) /*
       */  sort freq REVerse Words Format(str) noTrim local(str) Quoted ]

      if "`sort'"!="" & "`freq'"!="" {
            di as err "may specify either sort or freq, not both"
            exit 198
      }
      local maxlen = cond(_caller( ) == 6, 7, 32)
      if length("`local'") > `maxlen' {
            di as err "local name must be <=`maxlen' characters"
            exit 198
      }

      marksample touse, novarlist
      if "`missing'" == "" { markout `touse' `varlist', strok }
      qui count if `touse'
      if `r(N)' == 0 { exit }

      local notint = 0
      cap conf string variable `varlist'
      local isstr = _rc != 7
      if !`isstr' {
            cap assert `varlist' == int(`varlist') if `touse'
            local notint = _rc
            if `notint' {
                  if "`format'" == "" { local fmt : format `varlist' }
                  else                { local fmt "`format'" }
             }
      }

      local lblname : value label `varlist'
      local lab = cond("`labels'"=="" & "`lblname'"!="",1,0)

      if "`format'" != "" {              /* try out format */
            if `isstr' | `lab' {  cap di `format' "abracadra"  }
            else               {  cap di `format' 123456       }
            if _rc { error 120 }
      }
      if     "`sep'" == "" { local sep " " }
      if "`reverse'" != "" { local minus "-" }

      qui {
            tempvar orig_n unique counter freqcy
            g double `orig_n' = `minus' _n
            bysort `touse' `varlist' (`orig_n'):      /*
                           */   g byte `unique' = 1  if _n==1 & `touse'
            su `unique', meanonly
            local nvals = r(sum)

            if "`sort'"!="" {
                  g long `counter' = `minus' sum(`unique') if `unique' <.
                  sort `counter'
            }
            else {
                  if "`freq'"!="" {
                        by `touse' `varlist':    /*
                           */     g long `freqcy' = `minus' -_N if `touse'
                        sort `unique' `freqcy'
                  }
                  else {
                        sort `unique' `orig_n'
                  }
            }
      }

      forv i = 1/`nvals' {
            if `isstr' & "`trim'" != "notrim" {
                               local val = trim(`varlist'[`i'])
            }
            else             {  local val `"`=`varlist'[`i']'"'    }
            if `notint'      {  local val = string(`val',"`fmt'")  }
            if "`val'" == "" {  local val "missing"                }

            if `lab' {
                  local val : label `lblname' `val'
                  if "`trim'" != "notrim" { local val = trim(`"`val'"') }
            }
            if `isstr' | `lab' {
                  if `max' {
                        local val = substr(`"`val'"',1,`max')
                  }
                  if "`words'" != "" {
                        local end = index(`"`val'"'," ") - 1
                        if `end' == -1 { local end "." }
                        local val = substr(`"`val'"',1,`end')
                  }
                  if "`format'" != "" {
                        local val : di `format' `"`val'"'
                  }
            }
            else {
                  if "`format'" != "" & !`notint' {
                        local val : di `format' `val'
                  }
            }

            if "`quoted'" == "" {
                  if `i' < `nvals' {
                        local vals `"`vals'`val'`sep'"'
                  }
                  else  local vals `"`vals'`val'"'
            }
            else {
                  if `i' < `nvals' {
                        local vals `"`vals'`"`val'"'`sep'"'
                  }
                  else  local vals `"`vals'`"`val'"'"'
            }
      }

      di as txt `"`vals'"'
      if "`local'" != "" { c_local `local' `"`vals'"' }
      ret local list `"`vals'"'
end

exit
