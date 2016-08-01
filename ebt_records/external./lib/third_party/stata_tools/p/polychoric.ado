*! Polychoric correlations -- v.1.5, by Stas Kolenikov
program define polychoric, rclass
   version 8.2

   #delimit ;
   syntax varlist(min=2 numeric) [if] [in] [aw fw pw /],
      [pca pw VERBose NOLOG SCore(str) dots IMissing NSCore(int 0) noINIT GRID(passthru) *]
   ;
   #delimit cr
   * PCA to perform PCA
   * pw for pairwise correlations
   * verbose to output the correlation type, rho, s.e., and goodness of fit if applicable
   * NOLOG
   * score to generate scores from PCA
   * dots to entertain the user with % signs
   * imissing to believe that the missing of an ordinal variables should be imputed zero

   if "`imissing'" == "" {
     local imissing not
   }

   if "`score'"=="" & `nscore'>0 {
     di as err "cannot specify nscore without score"
     exit 198
   }
*   else local nscore=5

   * this is a bit weird: what if the user specifies -score-
   * without the name of the new variable? Then it gets into `options'

   if index("`options'","score") {
      di as err "must specify new variable prefix with -score-"
      exit 198
   }

   if `:word count `varlist'' == 2{
      local verbose verbose
   }

   tempvar w1
   if "`weight'" ~= "" {
     qui g double `w1' = `exp'
     local www [`weight'=`w1']
   }
   else {
     qui g double `w1' = 1
     local www [pw=`w1']
     local exp `w1'
   }
   * that way, we always have weights

   if "`score'"~="" {
     confirm new var `score'1
   }

   if "`pw'"==""{
      marksample touse
   }
   else {
      marksample touse, novar
   }

   tokenize `varlist'
   local nvar: word count `varlist'
   tempname corrmat

   mat `corrmat' = J(`nvar',`nvar',.)
   forvalues i=1/`nvar' {
     mat `corrmat'[`i',`i']=1
   }

   mat rown `corrmat' = `varlist'
   mat coln `corrmat' = `varlist'

*   compress `varlist'

   local i=1
   local ndots = `nvar'*(`nvar'-1)/2
   local idots 0
   while "``i''"~="" {
      local j = `i'+1
      while "``j''"~="" {
          polych1 ``i'' ``j'' `www' if `touse' , `options' `init' `grid'
          if "`dots'"~="" {
             if int(`idots'/`ndots'*10)-int(`++idots'/`ndots'*10)~=0 {
                di as text int(10*`idots'/`ndots') "0%" _c
             }
             else {
                di as text "." _c
             }
          }
          mat `corrmat'[`i',`j']=r(rho)
          mat `corrmat'[`j',`i']=r(rho)
          if "`verbose'"=="verbose" {
             di _n ///
                as text "Variables :  " as res "``i'' ``j''" _n ///
                as text "Type :       " as res r(type) _n       ///
                as text "Rho        = " as res r(rho) _n        ///
                as text "S.e.       = " as res r(se_rho)
             if "`r(type)'" == "polychoric" {
                di    as text "Goodness of fit tests:" _n     ///
                   as text "Pearson G2 = " as res r(G2) ///
                   as text ", Prob( >chi2(" as res r(dfG2) as text")) = " as res r(pG2) _n ///
                   as text "LR X2      = " as res r(X2)      ///
                   as text ", Prob( >chi2(" as res r(dfX2) as text")) = " as res r(pX2)
             }
                       }
          local `j++'
      }
      local i=`i'+1
      tokenize `varlist'
   }

   return add

   if "`verbose'" == "" {
      di as text _n "Polychoric correlation matrix"
      mat li `corrmat', noheader
   }

   if "`pca'"~="" {
      return clear
      polypca `corrmat' `touse' `www' `imissing' `nscore' `score'
      return add
/*
      if "`score'"~="" {
        cap noi sum `score'*
      }
*/
   }
   return matrix R `corrmat'

end

prog def polypca, rclass
   * perform PCA with the estimated matrix

   args corrmat touse www imissing nscore score
   * the correlation matrix

   * parse the weights
   tokenize `www' , parse(" [=]")
   * should become `1' == [, `2' == weight type, `3' == "=", `4' == exp, `5' == ]
   local exp `4'

   tempname X V value
   if `nscore'==0 local nscore .

   mat symeigen `X' `V' = `corrmat'
   * `V' are the eigenvalues, `X' are the eigenvectors

   local nvar = colsof(`corrmat')
   local p = min(`nvar',`nscore')
   di _n as text "Principal component analysis" _n(2) " k  {c |}  Eigenvalues  {c |}  Proportion explained  {c |}  Cum. explained"
   di as text "{dup 4:{c -}}{c +}{dup 15:{c -}}{c +}{dup 24:{c -}}{c +}{dup 18:{c -}}"
   local sum=0
   forvalues i=1/`nvar' {
      return scalar lambda`i' = `V'[1,`i']
      local sum = `sum'+return(lambda`i')
      #delimit ;
      di as res "  "`i' as text " {c |}   "
         as res %9.6f `V'[1,`i'] _col(21) as text "{c |}   "
         as res %9.6f `V'[1,`i']/`nvar' _col(46) as text "{c |}   "
         as res %8.6f `sum'/`nvar'
      ;
      #delimit cr
   }

   if "`score'"~= "" {

* set trace on

      local varlist : rownames `X'
      tempvar tt ii
**      mat li `X'
      di as text _n _col(15) "{bf: Scoring coefficients}"  _n(2) ///
        "    Variable    {c |}  Coeff. 1  {c |}  Coeff. 2  {c |}  Coeff. 3 " ///
        _n "{dup 54:{c -}}" _c
      qui foreach x of varlist `varlist' {
         noi di _n as res " `x'" _col(16) _c
         * is it continuous or discrete?
         cap drop `tt'
         cap drop __tt`x'
*         cap confirm byte var `x'
*   need to properly determine if continuous or discrete

         cap inspect `x'
         if r(N_unique)>9 {
            * continuous
            * egen __tt`x' = std(`x') if `touse'
            sum `x' [iw=`exp']
            g double __tt`x' = (`x'-r(mean))/r(sd) if `touse'
            forvalues i=1/3 {
               noi di as text " {c |} " as res %9.6f /* sqrt(`V'[1,`i'])* */`X'[rownumb(`X',"`x'"),`i'] " " _c
            }
         }
         else {
  /*
          cap tab `x' if `touse'
          if r(r) > 10 | _rc == 134 {
            * quasi-continuous
            * egen __tt`x' = std(`x') if `touse'
            sum `x' [iw=`exp']
            g double __tt`x' = (`x'-r(mean))/r(sd) if `touse'
            forvalues i=1/3 {
               noi di as text " {c |} " as res %9.6f `X'[rownumb(`X',"`x'"),`i'] " " _c
            }
          }
          else {
  */
            * discrete; make it a centered categorized normal
**            noi di as text " : ordinal" _c
            local ncat = r(N_unique)
            sum `exp', mean
            local N = r(sum)
            sort `touse' `x'
            cap drop `ii'
            egen byte `ii' = group(`x') if `touse'
            local p0 = 0.1/`N'
            local t0 = invnorm(`p0')
**            noi di `t0'
            forvalues k=1/`ncat' {
               sum `exp' if `ii'<=`k' , mean
               local p`k' = (r(sum)-0.5)/`N'
               local t`k' = invnorm(`p`k'')
**               noi di `t`k''
            }
            local p`ncat' = (`N'-0.1)/`N'
            local t`ncat' = invnorm(`p`ncat'')
**            noi di `t`ncat''
            gen double __tt`x' = 0 if `touse'
            forvalues k=1/`ncat' {
               local k1 = `k'-1
               scalar `value' = ( exp(-.5*`t`k1''*`t`k1'') - exp(-.5*`t`k''*`t`k'') ) ///
                         /(sqrt(2*_pi)*(norm(`t`k'')-norm(`t`k1'') ) )
               replace __tt`x' = `value' if `touse' & `ii'==`k'
               * need to determine what was the original category
               sum `x' if `ii'==`k'
               noi di _n _col(14) as res %-2.0f r(mean) _c
               forvalues i=1/3 {
                 noi di as text " {c |} " as res %9.6f /* sqrt(`V'[1,`i'])* */ `X'[rownumb(`X',"`x'"),`i']*`value' " " _c
               }
            }
            if "`imissing'" == "imissing" {
               replace _tt`x' = 0 if `touse' & mi(`x')
            }
**          }
         }
      }
      di

      nobreak {
        qui forvalues i=1/`p' {
           * we'll score `p' components prefixed by `score'
           gen double `score'`i'=0 if `touse'
           foreach x of varlist `varlist' {
              replace `score'`i' = `score'`i' + /* sqrt(`V'[1,`i'])* */ `X'[rownumb(`X',"`x'"),`i']*__tt`x' if `touse'
           }
        }
      }
   }

   return matrix eigenvalues `V'
   return matrix eigenvectors `X'

   polyquit

end

prog def polych1, rclass

  syntax varlist(numeric min=2 max=2) if [aw fw pw /] [, noINIT GRID(passthru) * ]

*** !!! какие-то глюки с score nscore

  local www [`weight'=`exp']

  marksample touse

  local x1 `1'
  local x2 `2'

  forvalues i = 1/2 {

     cap inspect `x`i''
     if r(N_unique)==1 {
        di as err "Warning: no variability in `x`i'', correlation is not defined"
        return scalar type Undefined
        return scalar N=r(N)
        return scalar se_rho = .
        return scalar rho = .
     }
     else if r(N_unique)>9 {
        local call `call'c
     }
     else {
        local call `call'd
     }
  }

  if "`call'"=="cc" {

     * both are continuous
**     qui corr `x1' `x2' `www' if `touse'
     tempname A
     qui mat accum `A' = `x1' `x2' `www' if `touse' , nocons dev
     return scalar sum_w = r(N)
     qui count if !mi(`x1') & !mi(`x2') & !mi(`exp')
     return scalar N=r(N)
     mat `A' = corr(`A')
     return scalar rho = `A'[1,2]
     return local type Pearson
     return scalar se_rho = sqrt( (1-return(rho)*return(rho))/(return(N)-2) )
     exit
  }

  if "`call'"=="dc" {
     * the first variable has to be continuous, and the second, discrete
     local call cd `x2' `x1' `www' if `touse'
     return local type polyserial
  }

  if "`call'"=="cd" {
     * the first variable has to be continuous, and the second, discrete
     local call cd `x1' `x2' `www' if `touse'
     return local type polyserial
  }

  if "`call'"=="dd" {
     * the first variable has to be continuous, and the second, discrete
     local call dd `x2' `x1' `www' if `touse'
     return local type polychoric
  }

  cap noi corr`call' , `init' `options' `grid'
***********
*  set trace off

  if _rc==1 {
     polyquit
     exit 1
  }

  return add

end

prog def corrdd, rclass sort

    * the module to compute the polychoric correlation

****************
*    set tracedepth 2
*    set trace on

    syntax varlist(numeric min=2 max=2) if [aw fw pw /], [ * noINIT ITERate(int 50) SEArch(str) GRID(int 0) ]

    cap confirm integer number `search'
    if !_rc {
       local searchstr search(quietly) repeat(`search')
    }
    else {
    if "`search'" == "" {
       local searchstr search(off)
    }
    else {
       local searchstr search(`search')
    }
    }

    marksample touse
    * compute the thresholds

    tempvar x1 x2

    cap drop __POLY*
    eret clear
    ret clear

    qui forvalues k = 1/2 {
       sort `touse' ``k''
       egen `x`k'' = group(``k'') if `touse'
       tab `x`k''
       local r`k' = r(r)
       sum `exp' if `touse', meanonly
       local N = r(sum)
       return scalar sum_w = `N'
       return scalar N = r(N)
       gen __POLY`k'hi = .
       gen __POLY`k'lo = .
       forvalues h = 1/`r`k'' {
          * create the variables: upper threshold - lower threshold
          local h1 = `h'-1
          sum `exp' if `x`k''<=`h' & `touse', meanonly
          replace __POLY`k'hi = cond(`h'==`r`k'',10,invnorm( (r(sum)-.5)/`N' ) ) if `x`k'' == `h' & `touse'
          sum `exp' if `x`k'' <= `h1' & `touse', meanonly
          replace __POLY`k'lo = cond(`h'==1,-10,invnorm( (r(sum)-.5)/`N' ) ) if `x`k'' == `h' & `touse'
       }
    }
    qui corr `1' `2' if `touse'

    local mcorr = r(rho)
    local mcorr = sign(`mcorr')*min(0.9, (1+abs(`mcorr'))/2)
    if "`init'" == "noinit" {
        local initstr init(_cons = `mcorr')
    }
    else {
        local initstr
    }

    * shouldn't -collapse- come somewhere here so that we don't have
    * to compute a complicated bivariate distribution for too many observations?
    *
    * needed further: __POLY([1|2][hi|lo]&pi); sum of weights; `touse'
    * no, for some reason, it did not work: the s.e.s are wrong

    qui gen double __POLYpi = .

    preserve
    qui keep if `touse'

    cap ml model lf polych_ll (rho: `touse' =) if `touse' /// [fw=`counts']
       [`weight' = `exp'] ///
       , maximize `options' search(off) bounds(rho: -1 1) init(_cons = 0) iter(0) nolog

    if _rc==1 {
       polyquit
       exit 1
    }
    local ll0c = e(ll)

    cap noi ml model lf polych_ll (rho: `touse' =) if `touse' /// [fw=`counts']
       [`weight' = `exp'] ///
       , maximize `options' `searchstr' bounds(rho: -1 1) ///
         `initstr' iter(`iterate') nolog

    local rc=_rc
    if `rc'==1 {
       polyquit
       exit 1
    }
    else if `rc' | e(converged)==0 {
       if `grid' > 0 {
         * do grid search until it converges
         di as text "Performing grid search " _c
         forvalues k=1/`grid' {
           local rho = - ln(`k')/ln(`grid'+0.2)
           cap ml model lf polych_ll (rho: `touse' =) if `touse' /// [fw=`counts']
             [`weight' = `exp'] ///
             , maximize `options' search(off) difficult iter(`iterate') nolog init(`rho')
           if e(converged) {
              di as res "+"
              continue, break
           }
           else di as res "." _c
           local rho = ln(`k')/ln(`grid'+0.2)
           cap ml model lf polych_ll (rho: `touse' =) if `touse' /// [fw=`counts']
             [`weight' = `exp'] ///
             , maximize `options' search(off) difficult iter(`iterate') nolog init(`rho')
           if e(converged) {
              di as res "+"
              continue, break
           }
           else di as res "." _c
         }
       }
       else {
         * rely on Stata's random search
         cap noi ml model lf polych_ll (rho: `touse' =) if `touse' /// [fw=`counts']
         [`weight' = `exp'] ///
         , maximize `options' search(quietly) repeat(100) difficult bounds(rho: -1 1) ///
           iter(`iterate') nolog
       }
    }

    if e(converged) {
       return scalar rho = _b[_cons]
       return scalar se_rho = _se[_cons]

       * tests
       * null hypothesis: no structure
       local df0 = `r1'*`r2' - `r1' - `r2'
       if `df0' > 0 {

          collapse (sum) `exp' (mean) `touse' (mean) __POLY* if `touse', by(`x1' `x2')

          tempvar ll pp

          tempvar counts
          qui g `ll'  = sum( `exp'*ln(`exp'/`N') )
          local ll0 = `ll'[_N]

          * Likelihood ratio
          return scalar G2 = 2*(`ll0'-e(ll))
          return scalar dfG2 = `df0'
          return scalar pG2 = chi2tail(`df0',return(G2))

          * Pearson chi-square

          qui g double `pp' = sum( ((`exp'/`N'-__POLYpi)^2)/__POLYpi )
          return scalar X2 = `pp'[_N]*`N'
          return scalar dfX2 = `df0'
          return scalar pX2 = chi2tail(`df0',return(X2))
       }

       restore

       * no correlation
       return scalar LR0 = -2*(`ll0c'-e(ll))
       return scalar pLR0 = chi2tail(1,return(LR0))
    }
    else {
       * lack of convergence
       return scalar rho = .
       return scalar se_rho = .
    }

    polyquit

end

prog def corrcd, rclass

    * the module to compute the polyserial correlation

    syntax varlist(numeric min=2 max=2) if [aw fw pw /], [ * ITERate(int 50) noINIT SEArch(str) ]
    * the first variable is continuous, the second is discrete

    cap confirm integer number `search'
    if !_rc {
       local searchstr search(quietly) repeat(`search')
    }
    else {
    if "`search'" == "" {
       local searchstr search(off)
    }
    else {
       local searchstr search(`search')
    }
    }

    marksample touse

    * thresholds for the discrete part

    tempvar x1 x2

    cap drop __POLY*
    ret clear

    qui{
       * egen `x1' = std(`1') if `touse'
       sum `1' [iw=`exp']
       g double `x1' = (`1'-r(mean))/r(sd) if `touse'

       sort `touse' `2' `1'
       egen `x2' = group(`2') if `touse'
       tab `x2' if `touse'
       local r2 = r(r)
       sum `exp' if `touse', mean
       local N = r(sum)
       return scalar N = r(N)
       return scalar sum_w = `N'
       gen __POLY2hi = .
       gen __POLY2lo = .
       forvalues h = 1/`r2' {
          * create the variables: upper threshold - lower threshold
          local h1 = `h'-1
          sum `exp' if `x2'<=`h' & `touse'
          replace __POLY2hi = cond(`h'==`r2',10,invnorm( (r(sum)-.5)/`N' ) ) if `x2' == `h' & `touse'
          sum `exp' if `x2' <= `h1' & `touse'
          replace __POLY2lo = cond(`h'==1,-10,invnorm( (r(sum)-.5)/`N' ) ) if `x2' == `h' & `touse'
       }
       spearman `1' `2' if `touse'
       local mcorr = r(rho)
    }

    if "`init'" == "noinit" {
        local initstr init(_cons = `mcorr')
    }
    else {
        local initstr init(_cons = 0)
    }

    eret clear

    cap ml model lf polyser_ll (rho: `x1' =) if `touse' [`weight'=`exp'] , ///
       maximize `options' search(off) bounds(rho: -1 1) init(_cons = 0) iter(0) nolog

    if _rc==1 {
       polyquit
       exit 1
    }
    local ll0c = e(ll)

    cap noi ml model lf polyser_ll (rho: `x1' =) if `touse' [`weight'=`exp'] , ///
       maximize `options' `searchstr' bounds(rho: -1 1) `initstr' nolog iter(`iterate')

    local rc=_rc
    if `rc'==1 {
       polyquit
       exit 1
    }
    if `rc' {
       cap noi ml model lf polyser_ll (rho: `x1' =) if `touse' [`weight'=`exp'] , ///
       maximize `options' `bounds(rho: -1 1) nolog iter(`iterate') ///
       search(quietly) repeat(10)
    }

    * return the correlation coefficient

    return scalar rho = _b[_cons]
    return scalar se_rho = _se[_cons]

    * no correlation
    return scalar LR0 = -2*(`ll0c'-e(ll))
    return scalar pLR0 = chi2tail(1,return(LR0))

end

pro def polyquit
    cap drop __POLY*
end

exit

History:
v.1.1    -- Aug 2003
            The basic development of everything
v.1.2    -- November 2003
         -- weights accomodated
         -- imissing option
v.1.3    -- February 2004
         -- polychoricpca as a separate command
         -- nscore option added -- changed the order of arguments in polychoric.polypca
v.1.3.2  -- -inspect- is used to count the number of categories in place
            of -tab-; no need to -compress-
v.1.3.3  -- iterate, search, and other stuff to failsafe convergence
v.1.3.4  -- init string changed, score option clarified
v.1.4    -- weights dealt with properly
v.1.4.1  -- April 27, 2004
         -- bug with PCA fixed (categorical variables not recognized properly)
v.1.4.2  -- output the original category numbers
v.1.4.3  -- the default matrix is filled with missing values rather than zeroes
v.1.5    -- some attempts to improve stability
