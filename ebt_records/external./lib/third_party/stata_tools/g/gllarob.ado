*! version 2.2.5 SRH 7 Sept 2011
program define gllarob, eclass
    version 6.0

    syntax [,CLuster(varname) DOts First Macs SCorefil(string) temp noROb]

    tempname Vr b V
    matrix `V' = e(V)
    matrix `b' = e(b)

/* first: have not computed robust se before */
/* macs: macros are already there */
/* rob: do not compute/report robust ses */

*disp in re "first = `first' and mac= `macs' "

/* sort out depvar */
    local depv "`e(depvar)'"    
    global ML_y1 "`depv'"

    
/* sort out scorefil */

    if "`scorefil'"~=""{
        if "`e(scorefil)'"~=""{
            disp in re "There is already a score file `e(scorefil)', option ignored"
            local score
        }
        else{
            * check if file can be opened
            capture postfile junk a using "`scorefil'"
            if _rc~=0{
                disp in re "cannot open `scorefil'.dta for writing"
                exit 198
            }
            postclose junk
            local score "`scorefil'"
        }
    
    }
/* sort out first and calc */
    if "`first'"~=""{
        local first = 1
        local calc = 1
        
    }
    else{
        local first = 0
    }

    local robu = 1
    if "`rob'"~=""{
        local robu = 0
    }
    if `first' == 0 {
        global HG_const = e(const)
        matrix `V' = e(Vs)
        local robclus  "`e(robclus)'"
        local calc = 0
        * disp "`robclus' == `cluster' ?"
        capture matrix `Vr' = e(Vr)
            if _rc>0|"`robclus'"~="`cluster'"{
            local calc = 1
        }
        if "`score'"~=""{
            local calc = 1
        }
    }
    * disp "first = "  `first' " and calc = " `calc'
    *if `first'==0& `calc' {
    if "`macs'"==""& `calc' {
        if "`cluster'"~=""{
            qui count if `cluster'==.&e(sample)
            if r(N)>0{
                disp in re "`cluster' has missing values in the estimation sample"
                exit(198)
            }
        }
        preserve
        qui keep if e(sample)
/* set all global macros needed by gllam_ll */
        setmacs 
/* sort out temporary variables */
/* sort out weight */
        local weight "`e(weight)'"
        global HG_weigh "`e(weight)'"
        local pweight "`e(pweight)'"
*10/29/06
        local numlv: word count `e(clus)'
        tempvar wt
        quietly gen double `wt'=1
*End 10/29/06
        local i = 1
        while `i'<= `numlv'{ /* 10/29/06 not $HG_tplv{ because wrong for init option */
            tempvar wt`i'
            qui gen double `wt`i''=1
            global HG_wt`i' "`wt`i''"
            capture confirm variable `weight'`i'
            if _rc==0 {
                qui replace `wt`i'' = `wt`i'' * `weight'`i'
            }
            capture confirm variable `pweight'`i'
            if _rc==0{
                qui replace `wt`i'' = `wt`i'' * `pweight'`i'
            }
*10/29/06
            qui replace `wt' = `wt'*`wt`i''
            local i = `i'+1
        }
*10/29/06
        if `e(init)'{
            qui replace `wt1' = `wt'
        }

/* sort out level 1 clus variable */
        local clus `e(clus)'
        global HG_clus `clus'
        tempvar id
        if $HG_exp~=1&$HG_comp==0{
            gen long `id'=_n
            if $HG_tplv == 1{
                global HG_clus "`id'"
            }
            else{
                tokenize "`clus'"
                local l= $HG_tplv
                local `l' "`id'"
                global HG_clus "`*'"
            }
        }
        * disp in re "HG_tplv = " $HG_tplv " and HG_clus: $HG_clus" 
/* sort out denom */
        local denom "`e(denom)'"
        if "`denom'"~=""{
            capture confirm variable `denom'
            if _rc>0{
                tempvar den
                qui gen byte `den'=1
                global HG_denom "`den'"
            }
            else{
                global HG_denom `denom'
            }
        }

/* sort out HG_ind */
        capture confirm variable $HG_ind
        if _rc>0{
            tempname junk
            global HG_ind "`junk'"
            gen byte $HG_ind=1
        }

/* sort out HG_lvolo (from gllapred) */
        if $HG_nolog>0{
            tempname junk
            global HG_lvolo "`junk'"
            qui gen byte $HG_lvolo = 0
            local no = 1
            if "$HG_lv"==""{
                local olog = M_olog[1,`no']
                qui replace $HG_lvolo = 1       
            }
            else{
                while `no'<=$HG_nolog{
                    local olog = M_olog[1,`no']
                    qui replace $HG_lvolo = 1 if $HG_lv == `olog'
                    local no = `no' + 1
                }
            }
        }
        
/** (from gllapred) **/  
        if $HG_mlog>0{
            if $HG_nolog==0{
                tempname junk
                global HG_lvolo "`junk'"
                qui gen byte $HG_lvolo = 0
            }
            if "$HG_lv"~=""{ /* more than one link */
                qui replace $HG_lvolo = 1 if $HG_lv == $HG_mlog
            }
            else{
                qui replace $HG_lvolo = 1
            }
        }



/* sort out constraints */
        if $HG_const {
            * disp "constraints used"
            matrix `b' = `b'*M_T
            matrix `V' = M_T'*`V'*M_T
            *matrix junk = M_T*`V'*M_T'
            * matrix list junk
        }

        tempname junk
        capture matrix `junk' = inv(`V')
        if _rc>0{
            disp in re "parameter covariance matrix not invertible"
            exit(198)
        }  

/* set up HG_MU, HG_SD and HG_Cij */
        local rf = 1
        while `rf'<=$HG_tprf{
            tempname junk
            global HG_MU`rf' "`junk'"
            tempname junk
            global HG_SD`rf' "`junk'"
            gen double ${HG_MU`rf'}=0
            gen double ${HG_SD`rf'}=1
            local rf2 = `rf' + 1
            while `rf2' < $HG_tprf {
                tempname junk
                global HG_C`rf2'`rf' "`junk'"
                gen double ${HG_C`rf2'`rf'}=0
                local rf2 = `rf2' + 1
            }
            local rf = `rf' + 1
        }
    } 

/* endif set-up macros and variables */

/* compute scores and/or robust standard errors */
    if `calc'{ 
        *set trace on
        tempvar tpwt
        gen int `tpwt' = 1
        global HG_tpwt "`tpwt'"
        local weight "$HG_weigh"
* 10/20/06
        if $HG_init{
            local numlv: word count `e(clus)'
            local i = 1
            while `i'<=`numlv'{
                capture confirm variable `weight'`i'
                if _rc==0{
                    qui replace `tpwt' = `tpwt'*`weight'`i'
                }
                local i = `i' + 1
            }
        }
        else{
            local l = $HG_tplv
            capture confirm variable `weight'`l'
            if _rc==0 {
                /* there are frequency weights at the top level */
                qui replace `tpwt' = `tpwt' * `weight'`l'
            }
        }
        *summ `tpwt'
        * disp "before comprob, HG_const = " $HG_const " and first = " `first'
        noi cap noi comprob3 "`b'" "`V'" "`cluster'" "`score'" "`dots'" `robu'
        if _rc>0{
            disp in re "something went wrong in comprob3"
            delmacs
            exit 198
        }
        matrix `Vr' = `V'
    }

/* post results */
    *disp in re "temp = `temp' score = `score' "
    if "`score'"~=""&"`temp'"==""{
        est local scorefil "`score'"
    }
    if `robu'{
        * disp "after comprob, HG_const = " $HG_const " and first = " `first'
        if $HG_const&`first' == 0{
            matrix `V' = `Vr'
            est matrix Vr  `V'
            tempname M_T
            matrix `M_T'=e(T)
            matrix `Vr' = `M_T'*`Vr'*`M_T''
            * matrix list `Vr'
        }
        else{
            matrix `V' = `Vr'
            est matrix Vr  `V'
            * matrix list e(Vr)
        }
        estimates repost V = `Vr'
        est local robclus "`cluster'"
    }
    if `first' == 0&`calc'{
        delmacs
    }

end


program define comprob3
version 6.0
args coeffs var cluster score dots rob
*set trace on
    *disp in re "in comprob3: dots=`dots', score = `score', rob=`rob' "
    if "`cluster'"~=""{
        local cluster cluster(`cluster')
    }
    *disp "cluster is `cluster'"
    *matrix list `coeffs'

    tempvar where last
    local l = $HG_tplv
    local weight "$HG_tpwt"

    if $HG_tplv>1{
        local top: word 1 of $HG_clus
    }
    else{
        local k: word count $HG_clus
        local top: word `k' of $HG_clus
    }
    sort `top' $HG_ind
    qui by `top': gen byte `last' = _n==_N
    qui by `top': gen int `where' = _n==1
    qui replace `where' = sum(`where')
    local n = colsof(`coeffs')

/* compute scores */
if "`e(scorefil)'"==""{
    *disp "Computing scores"
    tempname b1 lnf 
    tempname S g fm fp fm0 S0 h Sgoal0 Sgoal1 Sming
    tempvar llp llm lls  done dfvar ok goal0 goal1 mingoal

/* sort out adapt */
    local adapt = 0
    if $HG_adapt==1{
        local adapt = 1
    }
    if `adapt'{
        tempname llast lnf
        global HG_adapt=1
        noi gllam_ll 1 `coeffs' "`lnf'" "junk" "junk" 1
        disp in gre "Non-adaptive log-likelihood: " in ye `lnf'
        scalar `llast' = 0
        local i = 1
                qui `noi' disp in gr "Updating posterior means and variances"
                qui `noi' disp in gr "log-likelihood: "
        while abs((`llast'-`lnf')/`lnf')>1e-8&`i'<60{
                scalar `llast' = `lnf'
                qui gllam_ll 1 "`coeffs'" "`lnf'" "junk" "junk" 1
                disp in ye %10.4f `lnf' " " _c
                        if mod(`i',6)==0 {disp " " }
                local i = `i' + 1
        }
    }

    qui gen double `llm'=.
    qui gen double `llp'=.
    qui gen double `lls'=.
    gllam_ll 1 `coeffs' "`lnf'" "junk" "junk" 3 "`lls'"
    * with mlogit link, all but last lls are missing:
    sort `top' `last'
    qui by `top': replace `lls' = `lls'[_N]

    if abs((`lnf'-`e(ll)')/`e(ll)')>1e-5{
        disp in re "can't get correct log-likelihood: " `lnf' " should be " `e(ll)'
        exit 198
    }

    *disp in re "got the right likelihood: " `e(ll)'
    
    qui count if `last'>0
    local N = r(N)

    
    local l 1e-8
    local u 1e-7
    local m 1e-10
    local epsf 1e-3
    local j = 1
    * disp "N = " `N'
    
    * CHANGED TO VARIABLES         
    gen double `goal0' = (abs(`lls')+`l')*`l'
    gen double `goal1' = (abs(`lls')+`u')*`u'
    gen double `mingoal' = (abs(`lls')+`m')*`m'

    qui gen byte `done' = 0
    qui gen byte `ok' = 0
    qui gen double `dfvar' = 0

    local ds
    local ss

    local i = 1
    while `i'<=`n'{ /* loop over parameters */
        * if "`dots'"~=""{ noi disp in gr "." _c}
*JUNK
        * disp in re " "
        * disp in re "parameter " `i'
        scalar `S' = 1 /* ML_d0_S[1,`i'] */
        scalar `h' = (abs(`coeffs'[1,`i'])+`epsf')*`epsf'
        matrix `b1' = `coeffs'

/* find zero derivatives */
       
        matrix `b1'[1,`i'] = `coeffs'[1,`i']+500*`h'*`S'
*JUNK
*        noi matrix list `b1'
        gllam_ll 1 `b1' "`lnf'" "junk" "junk" 3 "`llp'"
        
        matrix `b1'[1,`i'] = `coeffs'[1,`i']-500*`h'*`S'
*JUNK
*        noi matrix list `b1'
        gllam_ll 1 `b1' "`lnf'" "junk" "junk" 3 "`llm'"
        
        qui replace `done' = abs(`llp' - `llm')<`goal0' /* derivative is zero */
        sort `top' `last'
        qui by `top': replace `done' = `done'[_N]
        
*JUNK
*        disp in re "non-zero derivatives for following clusters (showing lls llm llp and goal0) step = " 1000*`h'*`S'
*        noi list `top' `lls' `llm' `llp' `goal0' if `last'==1&`done'==0
        
        tempvar d`i'
        qui gen double `d`i''= 0 if `done' == 1&`last'==1
        local ds "`ds' `d`i''"

        if "`score'"~=""{
            tempvar s`i'
            qui gen double `s`i''= 0 if `done' == 1&`last'==1
            local ss "`ss' `s`i''"
        }

        qui count if `done'==0&`last'==1
        local num = r(N)
    
        while `num'>0{
            **disp "`num' clusters left to do"
            scalar `S' = 1 /* ML_d0_S[1,`i'] */
            if "`dots'"~=""{ noi disp in ye "." _c}
            sort `done' `where'
            local nxt = `where'[1]
            scalar `lnf' = `lls'[1]
  
            scalar `Sgoal0' = (abs(scalar(`lnf'))+`l')*`l'
            scalar `Sgoal1' = (abs(scalar(`lnf'))+`u')*`u'
            scalar `Sming' = (abs(scalar(`lnf'))+`m')*`m'
            
            preserve

            ***disp in re " "
*JUNK
*            disp in re "sorting out cluster `nxt': `top' = " `top'[1]
            qui keep if `where' == `nxt'

*JUNK            
*            if `nxt'==241{disp in re "lnf = " `lnf' " goal0 = " `Sgoal0' " goal1 = " `Sgoal1'}
            * disp in re "got here!"
            GetStep `coeffs' `h' `S' `i' `Sgoal0' `Sgoal1' `Sming' `lnf' /* "`coeffs'" */
*JUNK
*            if `nxt'==241{ disp in re "after GetStep: S = " `S'  " h = " `h'}

            restore
            matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
            gllam_ll 1 `b1' "`lnf'" "junk" "junk" 3 "`llm'"
            matrix `b1'[1,`i'] = `coeffs'[1,`i']+`h'*`S'
            gllam_ll 1 `b1' "`lnf'" "junk" "junk" 3 "`llp'"
            qui replace `dfvar' = abs(`lls'-`llm')
            qui replace `ok' = `goal0'<`dfvar'&`dfvar'<`goal1'
*JUNK
*            if `nxt'==241{
*                disp in re "goal0 = " `Sgoal0' " goal1 = " `Sgoal1'
*                noi list `goal0' `goal1' if `where'==`nxt'
*                disp in re "llm llp lls"
*                noi list `llm' `llp' `lls' if `where'==`nxt'
*            }
            * first derivatives
            qui replace `d`i'' = (`llp' - `llm')/(2*`h'*`S'*`weight') if `ok' == 1&`last'==1
            if "`score'"~=""{
                * second derivatives
                qui replace `s`i'' = (`llp' + `llm' -2*`lls' )/(`h'*`S'*`h'*`S'*`weight') /*
                */ if `ok' == 1&`last'==1
            }
            qui replace `done' = 1 if `ok'==1
            sort `top' `last'
            qui by `top': replace `done' = `done'[_N]
            
*JUNK?
            * if program didn't crash, derivative for `nxt' is valid:
            qui replace `done' = 1 if `where'==`nxt'
/*
            qui summ `done' if `where' == `nxt', meanonly
            if abs(r(mean)-1)>1e-3{
                disp in re "Problem with derivative for parameter `i', cluster `nxt'" 
            }
*/
            qui count if `done'==0&`last'==1
            local num = r(N)
        }
        *summ `d`i''
        local i = `i'+1
    }
*set trace on
    if "`score'"~=""{
        preserve
        format `ds' `ss' %16.11g
        qui outfile `top' `ds' `ss' if `last'==1 using "`score'.dta", replace
        local tp `top'
        if $HG_tplv==1{
            local tp __idno
        }
        qui infile `tp' double (d1-d`n' s1-s`n') using "`score'.dta", clear
        qui sort `tp'
        qui save "`score'", replace
        restore
    }
} /*endif*/
/* compute robust ses */
    if `rob'{
        local es
        local dds
        local i = 1
        while `i'<=`n'{
            local dds "`dds' d`i'"
            local es "`es' e`i'"
            local i = `i' + 1
        }
        * disp " "
        local eqs: coleq(`var')
        local rown: rownames(`var')
        local coln: colnames(`var')
        * matrix list `var'
        matrix coleq `var' = `es'
        matrix roweq `var' = `es'
        matrix colnames `var' = _cons
        matrix rownames `var' = _cons

        if "`e(scorefil)'"~=""{
            preserve
            local tp `top'
            if $HG_tplv == 1{
                rename $HG_clus __idno
                local tp __idno
            }
            sort `tp' `last'
            merge `tp' using `e(scorefil)'
            noi _robust `dds' [fweight=`weight'] if `last'>0, `cluster' variance(`var')
            restore
        }
        else{
            * matrix list `var'
            *disp "before _robust, _rc = " _rc
            *corr `ds', cov
            * disp "_robust `ds' [fweight=`weight'] if `last'>0, `cluster' variance(`var')"
            noi _robust `ds' [fweight=`weight'] if `last'>0, `cluster' variance(`var')
            *disp "after _robust, _rc = " _rc
            * matrix list `var'
        }

        * disp "setting equation names"
        matrix coleq `var' = `eqs'
        matrix roweq `var' = `eqs'
        matrix colnames `var' = `coln'
        matrix rownames `var' = `rown'
        * matrix list `var'
    }
    exit(0)
end

program define GetStep
    version 6.0

    args a h S i goal0 goal1 mingoal lnf /* coeffs */

    ***disp in re "In GetStep: h = " `h' " S = " `S' " i = " `i' " goal0 = " `goal0' 
    ***disp in re "goal0 = " `goal1' " mingoal = " `mingoal' " lnf = " `lnf' 
    tempname b1 S0 fm0 fp fm coeffs
    matrix `coeffs' = `a'
    matrix `b1' = `coeffs'
    * matrix list `coeffs'
    ***disp in re " "

/***** from here, stolen from ml_adj */
    matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
    gllam_ll 1 `b1' "`fm'" 
    ***disp in re "in iteration 0, lnf = " `lnf' " and fm = " `fm' 

/* Save initial values of S and fm. */

    scalar `S0' = `S'
    scalar `fm0' = `fm'

    if `fm'==.{
        * disp in re "calling MisStep now"
        * disp in re "step before: " `S'
        MisStep `coeffs' `h' `S' `i' `lnf'
        * disp in re "step before: " `S'
        exit
    }

/* Compute df.  We want goal0 <= df <= goal1. */

    local df = abs(scalar(`lnf')-`fm')

    local Sold1 0
    local dfold1 0
    local iter 1

    local itmax = 20

    while (`df'<`goal0' | `df'>`goal1') & `iter'<=`itmax' {

        GetS `mingoal' `goal0' `goal1' `S' `df' /* interpolate ...
        */ `Sold1' `dfold1' `Sold2' `dfold2'
        local Sold2 `Sold1'
        local dfold2 `dfold1'
        local Sold1 = `S'
        local dfold1 `df'

        scalar `S' = r(S)

        matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
*JUNK
*        noi disp in re "changing paramter by " `h'*`S' " to " `b1'[1,`i']
        gllam_ll 1 `b1' "`fm'" 
*JUNK
*        disp in re "in iteration `iter', S= " `S' " fm = " `fm'

        if `fm'==. {
            * disp in re "calling MisStep now"
            * disp in re "step before: " `S'
            MisStep `coeffs' `h' `S' `i' `lnf'
            * disp in re "step after: " `S'
            exit
        }

        local df = abs(scalar(`lnf')-`fm')
        local iter = `iter' + 1
    }

    if `df'<`goal0' | `df'>`goal1' { /* did not meet goal */
        scalar `S' = `S0'    /* go back to initial values */
        scalar `fm' = `fm0'  /* guaranteed to be nonmissing */
    }

    matrix `b1'[1,`i'] = `coeffs'[1,`i']+`h'*`S'
    gllam_ll 1 `b1' "`fp'" 

    if `fp'==. {
        * disp in re "calling MisStep now"
        * disp in re "step before: " `S'
        MisStep `coeffs' `h' `S' `i' `lnf'
        * disp in re "step after: " `S'
        exit
    }

    if `df'<`goal0' | `df'>`goal1' { /* did not meet goal; we redo
                    stepsize adjustment looking at
                    both sides; starting values are
                    guaranteed to be nonmissing
                 */
*JUNK
*        disp in re  "calling TwoStep now, lnf = " `lnf' 
*        disp in re "lnf = " `lnf' " fm = " `fm' " df  = " `df' 
        * disp in re "step before: " `S'
        TwoStep `fp' `fm' `coeffs' `h' `S' `i' `lnf'
        * disp in re "step after: " `S'

    }
/***** up to here, stolen from ml_adj */
end

program define GetS, rclass
* stolen from ml_adj
    args mingoal goal0 goal1 S df Sold1 dfold1 Sold2 dfold2

    if `df' < `mingoal' {
    /* di "GetS: below mingoal, doubling S --> 2*S" */  /* diag */
        return scalar S = 2*`S'
        exit
    }

/* Interpolate to get f(newS)=mgoal.

   When `Sold2' and `dfold2' are empty (on the first iteration), we do
   linear interpolation of f(S)=df, f(0)=0.

   Thereafter, we do quadratic interpolation with the current and previous
   two positions.
*/
    tempname newS
    local mgoal = (`goal0' + `goal1')/2

    Intpol `newS' `mgoal' `S' `df' `Sold1' `dfold1' `Sold2' `dfold2'

    if `newS'==. | `newS'<=0  | (`df'>`goal1' & `newS'>`S') /*
    */                        | (`df'<`goal0' & `newS'<`S') {

        return scalar S = `S'*cond(`df'<`goal0',2,.5)
    }
    else    return scalar S = `newS'
end


program define Intpol
* stolen from ml_adj
    args y x y0 x0 y1 x1 y2 x2

    if "`y2'"=="" { local linear 1 }
    else if `y2'==. | `x2'==. { local linear 1 }

    if "`linear'"!="" {
        scalar `y' = ((`y1')-(`y0'))*((`x')-(`x0'))/((`x1')-(`x0')) /*
        */           + (`y0')
        exit
    }

    scalar `y' = /*
*/   (`y0')*((`x')-(`x1'))*((`x')-(`x2'))/(((`x0')-(`x1'))*((`x0')-(`x2'))) /*
*/ + (`y1')*((`x')-(`x0'))*((`x')-(`x2'))/(((`x1')-(`x0'))*((`x1')-(`x2'))) /*
*/ + (`y2')*((`x')-(`x0'))*((`x')-(`x1'))/(((`x2')-(`x0'))*((`x2')-(`x1')))
end




program define MisStep  /* This routine is called if missing values were
               encountered in GetStep.
            */

    /* di "in MisStep!"  */                 /* diag */
    *args h S caller i fpout fmout x0
    args coeffs h S i lnf
    *macro shift 7
    *local list "`*'"

    local itmax 50

    tempname fm fp b1
    scalar `fm' = .
    scalar `fp' = .
    local iter 1
    while (`fm'==. | `fp'==.) & `iter'<=`itmax' {
        scalar `S' = `S'/2

        matrix `b1' = `coeffs'
        matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
        gllam_ll 1 `b1' "`fm'" 

        if `fm'!=. {
            matrix `b1'[1,`i'] = `coeffs'[1,`i']+`h'*`S'
            gllam_ll 1 `b1' "`fp'" 
        }

        local iter = `iter' + 1
    }

    if `fm'==. | `fp'==. {
        di as err "could not calculate numerical derivatives" _n /*
        */ "discontinuous region with missing values encountered"
        exit 430
    }

    TwoStep `fp' `fm' `coeffs' `h' `S' `i' `lnf'
end

program define TwoStep  /* This routine is called if

                (1) goal was not reached, or

                (2) missing values were encountered
                    and MisStep then found nonmissing
                    values.

               Note: Input is guaranteed to be nonmissing
                     on both sides.
            */

    /* di "in two-step"  */                 /* diag */
    *args fp fm h S caller i fpout fmout x0
    args fp fm coeffs h S i lnf
    *macro shift 9
    *local list "`*'"

    tempname bestS b1

    local ep0   1e-8
    local ep1   1e-7
    local epmin 1e-12
    local itmax 40

    local goal0   = (abs(scalar(`lnf'))+`ep0')*`ep0'
    local goal1   = (abs(scalar(`lnf'))+`ep1')*`ep1'
    local mingoal = (abs(scalar(`lnf'))+`epmin')*`epmin'

    local df = (abs(scalar(`lnf')-`fp')+abs(scalar(`lnf')-`fm'))/2
    local bestdf `df'
    scalar `bestS' = `S'
    local Sold1 0
    local dfold1 0
    local iter 1

    while (`df'<`goal0' | `df'>`goal1') & `iter'<=`itmax' {

*di "TwoStep   iter = `iter'   df = " %12.4e `df' "   S = "  %12.3e `S'

        GetS `mingoal' `goal0' `goal1' `S' `df' /* interpolate ...
        */ `Sold1' `dfold1' `Sold2' `dfold2'

        local Sold2 `Sold1'
        local dfold2 `dfold1'
        local Sold1 = `S'
        local dfold1 `df'

        scalar `S' = r(S)

        matrix `b1' = `coeffs'
        matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
        gllam_ll 1 `b1' "`fm'" 

        *Lik`caller' -`h'*`S' `i' `fm' `fmout' `x0' `list'

        if `fm'!=. {
            matrix `b1'[1,`i'] = `coeffs'[1,`i']+`h'*`S'
            gllam_ll 1 `b1' "`fp'" 
            * Lik`caller' `h'*`S' `i' `fp' `fpout' `x0' `list'
        }
        if `fm'==. | `fp'==. {
            if `bestdf' >= `mingoal' { /* go with best value */
                scalar `S' = `bestS'

            matrix `b1' = `coeffs'
            matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
            gllam_ll 1 `b1' "`fm'" 
            matrix `b1'[1,`i'] = `coeffs'[1,`i']+`h'*`S'
            gllam_ll 1 `b1' "`fp'" 

                di as txt /*
                */ "numerical derivatives are approximate" /*
                */ _n "nearby values are missing"
                exit
            }

            di as err /*
            */ "could not calculate numerical derivatives" /*
            */ _n "missing values encountered"
            exit 430
        }

        local df = (abs(scalar(`lnf')-`fp')+abs(scalar(`lnf')-`fm'))/2

        if `df'>1.1*`bestdf' | (`df'>=0.9*`bestdf' & `S'<`bestS') {
            local bestdf `df'
            scalar `bestS' = `S'
        }

        local iter = `iter' + 1
    }

*JUNK
*disp in re "TwoStep   df = " %12.4e `df' "   S = "  %12.3e `S' " goal0 = " `goal0'  " goal1 = " `goal1' " lnf = " `lnf'

    if `df'<`goal0' | `df'>`goal1' { /* did not reach goal */

disp in re "TwoStep: did not reach goal"

        if `bestdf' >= `mingoal' { /* go with best value */
            scalar `S' = `bestS'

            matrix `b1' = `coeffs'
            matrix `b1'[1,`i'] = `coeffs'[1,`i']-`h'*`S'
            gllam_ll 1 `b1' "`fm'" 
            matrix `b1'[1,`i'] = `coeffs'[1,`i']+`h'*`S'
            gllam_ll 1 `b1' "`fp'" 

            di as txt "numerical derivatives are approximate" /*
            */ _n "flat or discontinuous region encountered"
        }
        else {
            di as err "could not calculate numerical derivatives" /*
            */ _n "flat or discontinuous region encountered"
            exit 430
        }
    }
end



program define setmacs
version 6.0
/* may not work for higher level models yet */
/* tplv */
    global HG_tplv = e(tplv)

/* link and family-related macros */
    global HG_famil "`e(famil)'"
    global HG_link "`e(link)'"
    global HG_linko "`e(linko)'"
    global HG_nolog = `e(nolog)'
    global HG_ethr = `e(ethr)'
    global HG_lv "`e(lv)'"
    global HG_fv "`e(fv)'"
    global HG_oth = e(oth)
    global HG_mlog = e(mlog)
    global HG_smlog = `e(smlog)'
    capture matrix M_resp=e(mresp)
    capture matrix M_respm=e(mrespm)
    capture matrix M_frld=e(frld)
    capture matrix M_olog=e(olog)
    capture matrix M_oth=e(moth)
    capture matrix ML_d0_S=e(do_S)
    global HG_exp = e(exp)
    global HG_expf = e(expf)
    global HG_ind = "`e(ind)'"
    global HG_init = e(init)
    global HG_lev1 = e(lev1)
    global HG_comp = e(comp)
    capture local coall "`e(coall)'"
    if $HG_comp~=0{
        local i = 1
        while `i'<=$HG_comp{
            local k: word `i' of `coall'
            global HG_co`i' `k'
            local i = `i' + 1
        }
    }

/* prior related global macros */
    global HP_prior = e(prior)
    if $HP_prior == 1{
            global HP_sprd = 1
            global HP_invga = e(invga)
            global HP_invwi = e(invwi)
            global HP_foldt = e(foldt)
            global HP_logno = e(logno)
            global HP_gamma = e(gamma)
            global HP_corre = e(corre)
            global HP_boxco = e(boxco)
            global HP_spect = e(spect)
            global HP_wisha = e(wisha)
            if $HP_invga==1{
                global shape = e(shape)
                global rate = e(rate)
            }
            if $HP_invwi==1{
                global df = e(df)
                matrix scale = e(scale)
            } 
            if $HP_foldt==1{
                global df = e(df)
                global scale = e(scale)
                global location = e(location)
            }
            if $HP_logno==1{
                global meanlog = e(meanlog)
                global sdlog = mean(sdlog)
            }
            if $HP_gamma==1{
                global HP_scale = e(scale)
                global HP_var = e(var)
                global HP_shape = e(shape)
            }
            if $HP_corre==1{
                global alpha = e(alpha)
                global beta = e(beta)
            }
            if $HP_boxco==1{
                global scale = e(scale)
                global lambda = e(lambda)
            }
            if $HP_spect==1{
                global alpha = e(alpha)
                global beta = e(beta)
            }
            if $HP_wisha==1{
                global wisha = e(wisha)
                global df = e(df)
                matrix scale =e(scale)
            }
            matrix M_nu = e(nu)
    }


/* set all other global macros */
    global HG_nats = `e(nats)'
    global HG_noC = `e(noC)'
    global HG_noC1 = `e(noC1)'
    global HG_adapt = `e(adapt)'
    global HG_tplv = e(tplv)
    global HG_tpff = `e(tpff)'
    global HG_tpi = `e(tpi)'
    global HG_free = e(free)
    global HG_mult = e(mult)
    global HG_lzpr lzprobg
    global HG_zip zipg
    if $HG_mult{
        global HG_lzpr lzprobm
    }
    else if $HG_free{
        global HG_lzpr lzprobf
        global HG_zip zipf
        matrix M_np=e(mnp)
    }
    global HG_cip = e(cip)
    global which = 4
    global HG_off "`e(offset)'"
    global HG_error = 0
    global HG_cor = `e(cor)'
    global HG_bmat = e(bmat)
    global HG_tprf = e(tprf)
    global HG_const = e(const)
    if $HG_const==1{
        matrix M_T = e(T)
        matrix M_a = e(a)
    }
    global HG_ngeqs = e(ngeqs)
    global HG_inter = e(inter)
    global HG_dots = 0
    matrix M_nbrf = e(nbrf)
    matrix M_nrfc = e(nrfc)
    matrix M_ip =  J(1,$HG_tprf+2,1)
    matrix M_nffc =  e(nffc)
    local tprf = $HG_tprf
    if `tprf'<2 { local tprf = 2 }
    matrix M_znow =J(1,`tprf'-1,1)
    matrix M_nip = e(nip)
    capture matrix M_ngeqs = e(mngeqs)
    capture matrix M_b=e(mb)
    *matrix M_chol = e(chol)
    local l = M_nrfc[1,1] + 1  /* loop */
    local k = M_nrfc[2,1] + 1  /* r. eff. */
    if $HG_tplv>1{
    while `l'<=M_nrfc[1,2]{
        while `k'<=M_nrfc[2,2]{
            * disp "loop " `l' " random effect " `k'
            local w = M_nip[2,`k']

            /* same loc and prob as before? */
            local found = 0
            local ii=M_nrfc[2,1] + 1
            while `ii'<`k'{
                if `w'==M_nip[2,`ii']{
                    local found = 1
                }
                local ii = `ii'+1
            }


            capture matrix M_zps`w' =e(zps`w')

            * disp "M_zlc`w'"
            matrix M_zlc`w'=e(zlc`w')
            local k = `k' + 1
        }
        local l = `l' + 1
    }
    }
end

program define delmacs
    version 6.0
/* deletes all global macros and matrices*/
    tempname var
    if "$HG_tplv"==""{
        * macros already gone
        exit
    }
    local nrfold = M_nrfc[2,1]
    local lev = 2
    while (`lev'<=$HG_tplv){
        local i2 = M_nrfc[2,`lev']
        local i1 = `nrfold'+1
        local i = `i1'
        local nrfold = M_nrfc[2,`lev']
        while `i' <= `i2'{
            local n = M_nip[2,`i']
            if `i' <= M_nrfc[1,`lev']{
                capture matrix drop M_zps`n'
            }
            capture matrix drop M_zlc`n'
            local i = `i' + 1
        }
        local lev = `lev' + 1
    }
    if $HG_free==0{
        capture matrix drop M_chol
    }
    matrix drop M_nrfc
    matrix drop M_nffc
    matrix drop M_nbrf
    matrix drop M_ip
    capture matrix drop M_b
    capture matrix drop M_resp
    capture matrix drop M_respm
    capture matrix drop M_frld
    matrix drop M_nip
    matrix drop M_znow
    capture matrix drop M_ngeqs
    capture matrix drop CHmat

    /* globals defined in gllam_ll */
    local i=1
    while (`i'<=$HG_tpff){
        global HG_xb`i'
        local i= `i'+1
    }
    local i = 1
    while (`i'<=$HG_tprf){
        global HG_s`i'
        local i= `i'+1
    }
    local i = 1
    while (`i'<=$HG_tplv){
        global HG_wt`i'
        local i = `i' + 1
    }
    global HG_nats
    global HG_noC
    global HG_noC1
    global HG_noC2
    global HG_adapt
    global HG_fixe
    global HG_lev1
    global HG_bmat
    global HG_tplv 
    global HG_tprf
    global HG_tpi
    global HG_tpff
    global HG_clus
    global HG_weigh
    global which   
    global HG_gauss 
    global HG_free
    global HG_famil 
    global HG_link 
    global HG_linko
    global HG_nolog
    global HG_lvolo
    global HG_oth
    global HG_mlog
    global HG_exp
    global HG_expf
    global HG_lv
    global HG_fv
    global HG_nump
    global HG_eqs
    global HG_obs
    global HG_off
    global HG_denom
    global HG_cor
    global HG_s1
    global HG_init
    global HG_ind
    global HG_const
    global HG_dots
    global HG_inter
    global HG_ngeqs
    global HG_tpwt
    global HG_ethr
    global HG_mult
    global HG_lzpr
    global HG_zip
    global HG_cip
    global HG_comp
    global HG_pwt
    global HG_befB
    global HG_smlog
    global HG_cn
    capture drop macro HG_co*
end
