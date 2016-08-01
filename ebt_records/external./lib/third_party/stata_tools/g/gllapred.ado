*! version 2.3.8 SRH 7 Sept 2011
program define gllapred
    version 6.0

    if "`e(cmd)'" ~= "gllamm" { 
        di in red  "gllamm was not the last command"
        exit 301
    }

    *syntax anything(name=pref id="prefix for variable(s)") [if] [in]
    syntax newvarname [if] [in] /*
    */  [,XB U USTD P S LInpred MU ADapt LL FAC Deviance PEarson Anscombe COoksd SCorefil(string) /* DFBeta
    */ MArginal OUTcome(int -99) ABove(numlist integer) US(string) CORR noOFFset FSAMPLE ADOONLY FRom(string)]
    local nopt = ("`u'"~="") + ("`ustd'"~="") + ("`p'"~="") + ("`xb'"~="")  + ("`s'"~="") /*
        */ + ("`linpred'"~="") + ("`mu'"~="") + ("`ll'"~="") + ("`fac'"~="") /*
        */ + ("`deviance'"~="") + ("`pearson'"~="") + ("`anscombe'"~="")    /*
        */ + ("`dfbeta'"~="") + ("`cooksd'"~="")

    global HG_final = 0
    local pref `varlist'

    if `nopt'>1 { 
        disp in re "only one of these options allowed: xb, u, fac, linpred, mu, ll, p, s, deviance, pearson, anscombe, dfbeta"
        exit 198 
    }
** 11/4/06
    if "`corr'"~=""&"`u'"==""{
        disp in re "corr option allowed only with u option"
        exit 198
    }
    local tplv = e(tplv)
    local tprf = e(tprf)
    local vars
    if `nopt'==0 { 
            local xb "xb" 
    }
    if "`ustd'"~=""{
        local u "u"
    }
    if "`xb'"~=""|"`s'"~=""{
        local what = 0
        local vars `pref'
        if "`xb'"~=""{
            disp in gr "(xb will be stored in `pref')"
        }
        else{
            disp in gr "(s will be stored in `pref')"
        }
    }
    else if "`p'"~="" {
        if `tplv' < 2{
            disp in re "p option not valid for 1 level model"
            exit 198
        }
        local what = 2
        tempname mat
        matrix `mat'=e(nip)
        local nip = `mat'[1,2]
        local i = 1
        while `i'<=`nip'{
            local vars `vars' `pref'`i'
            local i = `i' + 1
        }
        disp in gr "(probabilities will be stored in `vars')"
        global HG_post = 1
    }
    else if "`ll'"~="" {
        local what = 4
        local vars `pref'
        disp in gr "(ll will be stored in `pref')"
        global HG_post = 1
        if "`fsample'"!=""{
            disp in gr "Note: conditional response probability/density set to 1""
            disp in gr "      for observartions with missing values"
            disp " "
        }
    }
    else if "`mu'"~=""{
        local what = 5
        local vars `pref'
        disp in gr "(mu will be stored in `pref')"
        global HG_post = 1
        if "`marginal'"~=""{
            global HG_post = 0
        }
    }
    else if "`deviance'"~=""|"`pearson'"~=""|"`anscombe'"~=""{
        local vars `pref'
        disp in gr "(residuals will be stored in `pref')"
        if "`pearson'"~="" {
            local what = 6
        }
        else if "`deviance'"~=""{
            local what = 7
        }
        else{
            local what = 8
        }
        global HG_post = 1
        if "`marginal'"~=""{
            global HG_post = 0
        }
    }
    else if "`u'"~=""|"`linpred'"~=""|"`fac'"~=""{
        local what = 1
        global HG_post = 1 /* added Jan 12 2008: signals that gllapred called gllam_ll */
        if `tplv' < 2{
            if "`u'"~=""|"`fac'"~=""{
                disp in re "u, and fac options not valid for 1-level model"
                exit 198
            }
            else if "`linpred'"~=""{
                disp in re "linpred option equivalent to xb for this model"
                local xb  "xb"
                local what = 0
            }
            * else if "`mu'"~=""?
        }
        if "`fac'"~=""{
            local i = 1
            while `i' < `tprf'{
                local vars `vars' `pref'm`i'
                local i = `i' + 1
            }
            disp in gr "(means will be stored in `vars')"
        }
        else if "`u'"~=""{
            local i = 1
            while `i' < `tprf'{
                local vars `vars' `pref'm`i' `pref's`i'
                local i = `i' + 1
            }
            disp in gr "(means and standard deviations will be stored in `vars')"
**11/4/06
            if "`corr'"~=""{
                local corvars
                local i = 1
                while `i' < `tprf'{
                    local rfs = 1
                    while `rfs' < `i'{
                        local vars `vars' `pref'c`i'`rfs'
                        local corvars `corvars' `pref'c`i'`rfs'
                        local rfs = `rfs' + 1
                    }
                    local i = `i' + 1
                }
                disp in gr "(correlations will be stored in `corvars')"                    
            }
        }
        else if "`linpred'"~=""{
            local vars `pref'
            disp in gr "(linear predictor will be stored in `pref')"
        }
    }
    else if "`dfbeta'"~=""{
        local k = e(k)
        local i = 1
        while `i'<= `k'{
            local vars `vars' `pref'`i'
            local i = `i' + 1
        }
        disp in gr "(dfbetas will be stored in `vars')"
    }
    else if "`cooksd'"~=""{
        local vars `vars' `pref'
        disp in gr "(Cook's D will be stored in `vars')"
    }
    if "`offset'"~=""{
        if "`linpred'"==""&"`xb'"==""&"`mu'"==""{
            disp in re "nooffset option only allowed with xb, mu or linpred options"
            exit 198
        }
    }

    if "`us'"~="" {
        if `what'<5{
            disp in re "us() option only valid with mu, pearson, deviance or anscombe"
            exit 198
        }
    }

/* check if variables already exist */

    confirm new var `vars'

/* restrict to estimation sample */

    tempvar idno
    gen long `idno' = _n
    preserve
    if "`fsample'"==""{
        qui keep if e(sample)
    }

/* interpret if and in */
    marksample touse, novarlist 
    qui count if `touse'
    if _result(1) < 1 {
        di in red "insufficient observations"
        exit 2001
    }
    qui keep if `touse'

    tempfile file

/* influence statistics (don't need macros) */
    
    if "`dfbeta'"~=""|"`cooksd'"~=""{
        *disp in re "`e(scorefil)'"
        if "`e(scorefil)'"~=""{
            local fil2 "`e(scorefil)'"
        }
        else if "`scorefil'"~=""{
            local fil2 "`scorefil'"
        }
        else{
            tempfile fil2
        }

        if "`e(scorefil)'"==""{
            if "`scorefil'"~=""{
                gllarob, scorefil(`fil2') norob
            }
            else{
                gllarob, scorefil(`fil2') temp norob
            }
        }
        local clus `e(clus)'
        if `e(tplv)'==1{
            local top `idno'
        }
        else{
            local top: word 1 of `clus'
        }
        sort `top'
        qui save "`file'", replace
        tempname H d junk junk1
        matrix `H' = e(Vs)

        if `e(const)' {
            * disp "constraints used"
            * matrix `b' = `b'*M_T
            matrix `H' = M_T'*`H'*M_T
        }

        capture matrix `H' = inv(`H')
        if _rc>0{
            disp in re "parameter covariance matrix not invertible"
            exit(198)
        }
        use `fil2', clear
        tempvar cons
        qui gen byte `cons' = 1
        local k = colsof(`H')
        local N = _N
        matrix `d' = vecdiag(`H')
        matrix `d' = diag(`d')
        matrix `junk' = `d'*`d''
        scalar `junk1' = trace(`junk')
        scalar `junk1' = sqrt(`junk1')
        matrix `d' = `d'/`N'
        matrix `H' = `H'*(`N'-1)/`N' + `d'
        if "`dfbeta'"~=""{
            tempname Hi covi dbi sumi
            local j = 1
            while `j'<=`k'{
                qui gen `pref'`j' = .
                local j = `j' + 1
            }
            qui gen `pref'0 = .
            local i = 1
            while `i'<=`N'{
                mkmat s1-s`k' if _n==`i', matrix(`Hi')
                matrix `Hi' = diag(`Hi')
                matrix `junk' = `Hi' + `d'
                matrix `junk' = `junk'*`junk''
                matrix `junk' = trace(`junk')
                qui replace `pref'0 = 100*sqrt(`junk'[1,1])/`junk1' in `i'
                matrix `covi' = `H' + `Hi'
                *if `i'==49{matrix list `covi'}
                matrix vecaccum `sumi' = `cons' d1-d`k' if _n~=`i', nocons
                *if `i'==49{matrix list `sumi'}
                matrix `dbi' = inv(`covi')*`sumi''
                matrix `Hi' = e(Vs)
                local j = 1
                while `j'<=`k'{
                    qui replace `pref'`j' = `dbi'[`j',1]/sqrt(`Hi'[`j',`j']) in `i'
                    local j = `j' + 1
                }
                local i = `i' + 1
            }
            local vars `vars' `pref'0
        }
        else{ /* Cook's D */
            *disp in re "calculating cook's d"
            matrix `H' = inv(`H')
            tempname scorei ci
            qui gen `pref' = .
            local i = 1
            while `i'<=`N'{
                mkmat d1-d`k' if _n==`i', matrix(`scorei')
                *matrix list `scorei'
                matrix `ci' = 2*`scorei'*`H'*`scorei''
                *matrix list `ci'
                qui replace `pref' = `ci'[1,1] in `i'
                local i = `i' + 1
            }
        }
        if `e(tplv)'==1{
            rename __idno `top'
        }
        keep `top' `vars'
        sort `top' 
        tempvar mrge
        merge `top' using "`file'", _merge(`mrge')
        qui drop `mrge'
        sort `idno'
    }
    else{

/* set all global macros needed by gllam_ll */
    setmacs `what'

    if "`offset'"~=""{ /* nooffset not specified: will subtract HG_offs=HG_off */
        global HG_offs $HG_off
    }
    else{
        tempvar offs
        global HG_offs `offs'
        gen `offs'=0
    }
    

/* deal with outcome() and above() */
    if `what'>=5&$HG_nolog>0{ /* mu or residuals */
        if "`above'"==""{
            disp in re "must specify above() option for ordinal responses"
            exit 198
        }
        else{   
            matrix M_above = J(1,$HG_nolog,0)
            local num: word count `above'
            if `num'>1&`num'~=$HG_nolog{
                disp in re "wrong length of numlist in above() option"
                exit 198
            }
            local no = 1
            local k = 1
            while `no' <= $HG_nolog{
                if `num'>1{
                    local k = `no'
                }
                local ab: word `k' of `above'
                * disp in re "`no'th ordinal response, above = `ab'"
                local n=M_nresp[1,`no']
                local i = 1
                local found = 0
                while `i'<= `n'&`found'==0{
                    if M_resp[`i',`no']==`ab'{
                        local found=`i'
                        matrix M_above[1,`no']=`i'
                    }
                    local i = `i' + 1
                }
                if `found'==0{
                    disp in re "`ab' not a category for `no'th ordinal response"
                    exit 198
                }
                else if `found' == `n'{
                    disp in re "`ab' is highest category for `no'th ordinal response"
                    exit 198
                }
                local no = `no' + 1
            }
        }
        * noi matrix list M_above
    }
    if `what'>=5&$HG_mlog>0{ /* mu or residuals */
        if `outcome'==-99&$HG_exp==0{
            disp in re "must specify outcome() option for nominal responses unless data in expanded form"
            exit 198
        }
        if $HG_exp==0{
            local n=rowsof(M_respm)
            local found = 0
            local i = 1
            while `i'<= `n'&`found'==0{
                if M_respm[`i',1]==`outcome'{
                    local found=`i'
                }
                local i = `i' + 1
            }
            if `found'==0{
                disp in re "`outcome not a category of the nominal response'"
                exit 198
            }
            global HG_outc=`outcome'
        }
    }

    if "`adoonly'"!="" {
        global HG_noC = 1
        global HG_noC1 = 1
    }

    *disp "HG_free = " $HG_free

    tempname b
    matrix `b'=e(b)

/* deal with from */
    if "`from'"~=""{
        capture qui matrix list `from'
        local rc=_rc
        if `rc'>1{
            disp in red "`from' not a matrix"
            exit 111
        }
        local ncol = colsof(`from')
        local nrow = rowsof(`from')
        local ncolb = colsof(`b')
        if `ncolb'~=`ncol'{
            disp in re "from matrix has `ncol' columns but should have `ncolb'"
            exit 111
        }
        if `nrow'~=1{
            disp in re "from matrix has more than one row"
            exit 111
        }
        local coln: colnames(`b')
        local cole: coleq(`b')
        matrix `b' = `from'
        matrix colnames `b' = `coln'
        matrix coleq `b' = `cole'
    }
    
    if "`s'"~=""|"`xb'"~=""|"`us'"~=""{
        /* run remcor */
        /* set up names for HG_xb`i' */
        local i = 1
        while (`i' <= $HG_tpff){
            tempname junk
            global HG_xb`i' "`junk'"
            local i = `i' + 1
        }
        /* set up names for HG_s`i' */
        local i = 1
        while (`i'<=$HG_tprf){
            tempname junk
            global HG_s`i' "`junk'"
            local i = `i'+1
        }

        qui remcor "`b'" "`us'"

        if "`s'"~=""{
            qui gen double `pref' = ${HG_s1}
        }
        else if "`xb'"~=""{
            qui gen double `pref' = $HG_xb1
            if "`offset'"~=""&"$HG_off"~=""{ /* nooffset specified - changed oct 2004 */
                qui replace `pref' = `pref' - $HG_off
            } 
        }
        else if "`us'"~="" {
            tempvar lpred muu
            local j = 1
            qui gen double `lpred' = $HG_xb1
            if "`offset'"~=""&"$HG_off"~=""{
                qui replace `lpred' = `lpred' - $HG_off
            }
            while `j'<$HG_tprf{
                capture confirm variable `us'`j'
                if _rc~=0{
                    disp in re "variable `us'`j' not found"
                    exit 111
                }
                local jp = `j' + 1
                qui replace `lpred' = `lpred' + `us'`j' * ${HG_s`jp'}
                local j = `j' + 1
            }
        }
    }
    if "`s'"==""&"`xb'"==""{
/* sort out temporary variables for gllas_yu or gllam_ll */
/* sort out denom */
        local denom "`e(denom)'"
        if "`denom'"~=""{
            *capture confirm variable `denom'
            *if _rc>0{
            if substr("`denom'",1,2)=="__" { /*sort this out in future! */
                tempvar den
                qui gen byte `den'=1
                global HG_denom "`den'"
            }
            else{
                * disp in re "denom given"
                global HG_denom `denom'
            }
        }

    /* sort out HG_ind */
        *capture confirm variable $HG_ind
        *if _rc>0{
        if substr("$HG_ind",1,2)=="__" { /*sort this out in future! */
            tempname junk
            global HG_ind "`junk'"
            gen byte $HG_ind=1
        }
    /* sort out HG_lvolo */
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
        
/** added this 24th feb 2004 **/  
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
/** end added this **/
        
        
    /* sort out level 1 clus variable */
        local clus `e(clus)'
        global HG_clus `clus'
        tempvar id
        if $HG_exp~=1&$HG_comp==0{
            gen long `id'=_n
            tokenize "`clus'"
            local l= $HG_tplv
            local `l' "`id'"
            if $HG_tplv>1{
                global HG_clus "`*'"
            }
            else{
                global HG_clus "`1'"
            }   
        }
        *disp "HG_clus: $HG_clus"

        if "`us'"~=""{
            qui gen double `muu' = 0
            qui gen double `pref' = 0
            sort $HG_clus
            gllas_yu `pref' `lpred' `muu' `what'
        }
    }
    if "`s'"==""&"`xb'"==""&"`us'"==""{ /* need to call gllam_ll */
/* sort out temporary variables for gllam_ll */
/* sort out weight */
        local weight "`e(weight)'"
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
        
        tempname lnf


/* deal with adapt */
        if "`adapt'"~=""{
            local adapt = 1
        }
        else if $HG_adapt==0{
            local adapt = 0
        }
        if $HG_adapt==1{
            local adapt = 1
        }
        if `what'==2{ /* posterior probs */
            if $HG_tplv~=2{
                disp in re "cannot compute posterior probabilities in higher level models"
                exit 301
            }
            else if $HG_free~=1{
                if $HG_tprf>2{
                    disp in re "cannot compute posterior probabilities for more than 1 continuous latent variable"
                    exit 301
                }
            }
            else{
                local i=1
                while `i'<=M_nip[1,2]{
                    global HG_p`i' `pref'`i'
                    qui gen double `pref'`i' = 0
                    local i = `i' + 1
                }
                noi gllam_ll 1 `b' "`lnf'" "junk" "junk" `what'
                disp in gr "log-likelihood:" in ye `lnf'
            }
        } 
        if `what'>=4|(`what'==2&$HG_free~=1){ /* ll, mu or resids or posterior probs */
            if `adapt'&$HG_post{ /* want posterior quant., therefore adaptive good */
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
                noi gllam_ll 1 `b' "`lnf'" "junk" "junk" 1

                tempname last
                disp in gre "Non-adaptive log-likelihood: " in ye `lnf'
                global HG_adapt=1
                tempname last
                scalar `last' = 0
                local i = 1
                        qui `noi' disp in gr "Updating posterior means and variances"
                        qui `noi' disp in gr "log-likelihood: "
                while abs((`last'-`lnf')/`lnf')>1e-8&`i'<60&`lnf'~=.{
                        scalar `last' = `lnf'
                        qui gllam_ll 1 "`b'" "`lnf'" "junk" "junk" 1
                        disp in ye %10.4f `lnf' " " _c
                        if mod(`i',6)==0 {disp " " }
                        local j = 1
                        local i = `i' + 1
                }
                if mod(`i',6)~=1{disp " "}
            } /* end if adapt */
            else{ /* want marginal quantity, use ordinary quad */
                global HG_adapt = 0
            }
            if `what'>=5{
                global HG_noC1 = 1
            }
            if `what'==2{
                local i=1
                while `i'<=M_nip[1,2]{
                    *disp in re "making `pref'`i'"
                    global HG_p`i' `pref'`i'
                    qui gen double `pref'`i' = 0
                    local i = `i' + 1
                }
                *noi gllam_ll 1 `b' "`lnf'" "junk" "junk" `what'
                *disp in gr "log-likelihood:" in ye `lnf'
            }
            else {
                qui gen double `pref' = 0
            }
**Test
            global HG_final = 1
            noi gllam_ll 1 `b' "`lnf'" "junk" "junk" `what' `pref'
            if `lnf'==.{
                disp in re "log-likelihood cannot be computed"
                disp in re "for observations that should not contribute to posterior or ll,"
                disp in re "   set response variable to missing"
                exit 198
            }
            if `adapt'==0|(`adapt'==1&$HG_post==1){
                disp in gr "log-likelihood:" in ye `lnf'
            }
        }
        else if `what'==1 { /* u, fac or linpred */
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
            
            noi gllam_ll 1 `b' "`lnf'" "junk" "junk" `what'
            if `lnf'==.{
                disp in re "log-likelihood cannot be computed"
                disp in re "for observations that should not contribute to posterior,"
                disp in re "   set response variable to missing"
                exit 198
            }
            if `adapt'{
                tempname last
                disp in gre "Non-adaptive log-likelihood: " in ye `lnf'
                global HG_adapt=1
                tempname last
                scalar `last' = 0
                local i = 1
                        qui `noi' disp in gr "Updating posterior means and variances"
                        qui `noi' disp in gr "log-likelihood: "
                while abs((`last'-`lnf')/`lnf')>1e-8&`i'<60&`lnf'~=.{
                        scalar `last' = `lnf'
                        qui gllam_ll 1 "`b'" "`lnf'" "junk" "junk" 1
                        disp in ye %10.4f `lnf' " " _c
                        if mod(`i',6)==0 {disp " " }
                        local j = 1
                        local i = `i' + 1
                }
                if mod(`i',6)~=1{disp " "}
                disp in gr "log-likelihood:" in ye `lnf'
                * disp in re "call gllam_ll without running prepadpt"
                global HG_adapt = 2
**Test
                global HG_final = 1
                qui gllam_ll 1 "`b'" "`lnf'" "junk" "junk" 1
                if `lnf'==.{
                    disp in re "log-likelihood cannot be computed"
                    disp in re "for observations that should not contribute to posterior,"
                    disp in re "   set response variable to missing"
                    exit 198
                }
            }
            if "`u'"~=""|"`fac'"~=""{
                * noi matrix list CHmat
                tempname vari
                if $HG_free==0{
                    local lv = 2
                    local rf = 1
                    while `lv'<=$HG_tplv{
                        local minrf = `rf'
                        local maxrf = M_nrfc[2,`lv']
                        while `rf'<`maxrf'{
                            qui gen double `pref'm`rf'=0
                            qui gen double `pref's`rf'=0  /* will be deleted later if option is fac */
                            scalar `vari' = 0   
                            local rf2 = `minrf'
                            while `rf2'<=`rf'{ /* lower block triangular matrix */
                                * disp in re "`pref'm`rf' = `pref'm`rf' + CHmat[`rf',`rf2']*HG_MU`rf2'"
                                qui replace `pref'm`rf'=`pref'm`rf'+CHmat[`rf',`rf2']*${HG_MU`rf2'}
                                * disp in re "`pref's`rf' = `pref's`rf' + CHmat[`rf',`rf2']^2*HG_SD`rf2'^2"
                                qui replace `pref's`rf'=`pref's`rf'+CHmat[`rf',`rf2']^2*${HG_SD`rf2'}^2
                                * was scalar `vari' = `vari' + CHmat[`rf',`rf2']*CHmat[`rf2',`rf']
                                scalar `vari' = `vari' + CHmat[`rf',`rf2']*CHmat[`rf',`rf2']
                                local rf3 = `minrf'
                                while `rf3'<`rf2'{
                                    * disp in re "`pref's`rf' = `pref's`rf' + 2*CHmat[`rf',`rf2']*CHmat[`rf',`rf3']*HG_C`rf2'`rf3'"
                                    qui replace `pref's`rf'=`pref's`rf'+2*CHmat[`rf',`rf2']*CHmat[`rf',`rf3']*${HG_C`rf2'`rf3'}
                                    local rf3 = `rf3' + 1
                                }
                                local rf2 = `rf2' + 1
                            }
                            if "`ustd'"~=""{
                                *disp in re "variance = " `vari'
                                qui replace `pref's`rf' = sqrt(`vari'-`pref's`rf')
                                qui replace `pref'm`rf' =  `pref'm`rf'/`pref's`rf'
                            }
                            else{
                                qui replace `pref's`rf' = sqrt(`pref's`rf')
                            }
                            ** 11/4/06
                            if "`corr'"~=""{
                                *set trace on
                                local rfs = 1
                                while `rfs'<`rf'{
                                    *disp in re "generating `pref'c`rf'`rfs'"
                                    qui gen double `pref'c`rf'`rfs'=0
                                    local rf2 = `minrf'
                                    while `rf2'<= `rf' {
                                        local rf3 = 1
                                        while `rf3'<= `rfs'{
                                            *disp in re "add CHmat[`rf',`rf2']*CHmat[`rfs',`rf3']*HG_C`rf2'`rf3'"
                                            if `rf3'<`rf2'{                           
                                                qui replace `pref'c`rf'`rfs' = `pref'c`rf'`rfs' + CHmat[`rf',`rf2']*CHmat[`rfs',`rf3']*${HG_C`rf2'`rf3'}
                                            }
                                            else if `rf3'==`rf2'{
                                                qui replace `pref'c`rf'`rfs' = `pref'c`rf'`rfs' + CHmat[`rf',`rf2']*CHmat[`rfs',`rf3']*${HG_SD`rf2'}^2
                                            }
                                            else{
                                                qui replace `pref'c`rf'`rfs' = `pref'c`rf'`rfs' + CHmat[`rf',`rf2']*CHmat[`rfs',`rf3']*${HG_C`rf3'`rf2'}
                                            }
                                            local rf3 = `rf3' + 1
                                        }
                                        local rf2 = `rf2' + 1
                                    }
                                    qui replace `pref'c`rf'`rfs' = `pref'c`rf'`rfs'/(`pref's`rf'*`pref's`rfs')
                                    local rfs = `rfs' + 1
                                }
                                *set trace off
                            }
                            local rf = `rf' + 1
                        }
                        local lv = `lv' + 1
                    }
                }
                else{ /* not $HG_free */
                    local i = 1
                    while `i'<$HG_tprf{
                        qui gen double `pref'm`i'=${HG_MU`i'}
                        qui gen double `pref's`i'=${HG_SD`i'}
                        local rf2 = 1
                        while `rf2'<`i'{
                            qui gen double `pref'c`i'`rf2' = ${HG_C`i'`rf2'}/(`pref's`i'*`pref's`rf2')
                            local rf2 = `rf2' + 1
                        }
                        local i = `i' + 1
                    }   
                }
                if "`fac'"~=""{
                    *disp "dealing with geqs"
                    tempname junk s1
                    local i = 1
                    while `i'<=$HG_ngeqs{
                        local k = M_ngeqs[1,`i']
                        local n = M_ngeqs[2,`i']
                        local nxt = M_ngeqs[3,`i']
                        * disp "random effect `k'-1 has `n' covariates"
                        local nxt2 = `nxt'+`n'-1
                        matrix `s1' = `b'[1,`nxt'..`nxt2']
                        * matrix list `s1'
                        local nxt = `nxt2' + 1
                        capture drop `junk'
                        matrix score double `junk' = `s1'
                        local rf = `k' - 1
                        qui replace `pref'm`rf' = `pref'm`rf' + `junk'
                        local i = `i' + 1
                    }
                    *disp "dealing with bmat"
                    if $HG_bmat{
                        local rf  = $HG_tprf - 1
                        /* commands for sds are wrong: qui replace `pref's`rf' = `pref's`rf'^2 */
                        local rf = $HG_tprf - 2
                        while `rf'>0{
                            * qui replace `pref's`rf' = `pref's`rf'^2
                            local rf2 = `rf'+1
                            while `rf2'<=$HG_tprf - 1 { /* upper triangular matrix */
                                *disp in re "`pref'm`rf'=`pref'm`rf'+Bmat[`rf',`rf2']*`pref'm`rf2'"
                                qui replace `pref'm`rf'=`pref'm`rf'+Bmat[`rf',`rf2']*`pref'm`rf2'
                                *qui replace `pref's`rf'=`pref's`rf'+Bmat[`rf',`rf2']^2*`pref's`rf2'/*
                                *    */ + 2*Bmat[`rf',`rf2']*CHmat[`rf2',`rf2']*CHmat[`rf',`rf']${HG_C`rf2'`rf'}
                                *local rf3 = `rf' + 1
                                *while `rf3'<`rf2'{
                                *    qui replace `pref's`rf'=`pref's`rf' /*
                                *        */ + 2*Bmat[`rf',`rf2']*Bmat[`rf',`rf3']*CHmat[`rf2',`rf2']*CHmat[`rf3',`rf3']${HG_C`rf2'`rf3'}
                                *    local rf3 = `rf3' + 1
                                *}
                                local rf2 = `rf2' + 1
                            }
                            local rf = `rf' -1
                        }
                        local rf = 1
                        while `rf'<=$HG_tprf - 1{
                        *    qui replace `pref's`rf' = sqrt(`pref's`rf')
                            drop  `pref's`rf'
                            local rf = `rf' + 1
                        }
                    }
                }
            }
            else if "`linpred'"~="" { /* linpred */
                /* set up variable names $HG_xb1 for remcor */
                local i = 1
                while (`i' <= $HG_tpff){
                    tempname junk
                    global HG_xb`i' "`junk'"
                    local i = `i' + 1
                }
                /* set up names for HG_s`i' */
                local i = 1
                while (`i'<=$HG_tprf){
                    tempname junk
                    global HG_s`i' "`junk'"
                    local i = `i'+1
                }

                qui remcor `b' 
                * fixed part
                
                qui gen double `pref' = $HG_xb1
                if "`offset'"~=""&"$HG_off"~=""{
                    qui replace `pref' = `pref' - $HG_off
                }
                
                * add random part
                local i = 2
                while (`i' <= $HG_tprf){
                    local im = `i' - 1
                    qui replace `pref' = `pref' + ${HG_MU`im'} * ${HG_s`i'}
                    local i = `i' + 1
                }
            }
        }               
    }
/* delete macros */
    delmacs
    } /* endelse influence */
    qui keep `idno' `vars'
    qui sort `idno'
    qui save "`file'", replace
    restore
    sort `idno'
    tempvar mrge
    qui merge `idno' using "`file'", _merge(`mrge')
    qui drop `mrge'
end

program define setmacs
version 6.0
args what
/* sort out depvar */
    local depv "`e(depvar)'"    
    global ML_y1 "`depv'"


/* link and family-related macros */
    global HG_famil "`e(famil)'"
    global HG_link "`e(link)'"
    global HG_linko "`e(linko)'"
    global HG_nolog = `e(nolog)'
    global HG_ethr = `e(ethr)'
    global HG_mlog = `e(mlog)'
    global HG_smlog = `e(smlog)'
    global HG_oth = `e(oth)'
    global HG_lv "`e(lv)'"
    global HG_fv "`e(fv)'"
    capture matrix M_resp=e(mresp)
    capture matrix M_respm=e(mrespm)
    capture matrix M_frld=e(frld)
    capture matrix M_olog=e(olog)
    capture matrix M_oth=e(moth)
    global HG_exp = e(exp)
    global HG_expf = e(expf)
    global HG_ind = "`e(ind)'"
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
    
/* macros related to priors */
    global HP_prior = 0 /* assume that we never use the prior in gllapred */

/* set all other global macros */
    global HG_nats = `e(nats)'
    global HG_noC = `e(noC)'
    global HG_noC1 = `e(noC1)'
    global HG_adapt = `e(adapt)'
    global HG_tplv = e(tplv)
    global HG_tpff = `e(tpff)'
    global HG_tpi = `e(tpi)'
    global HG_tprf = e(tprf)
    local tprf = $HG_tprf
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
    global which = 1
    global HG_off "`e(offset)'"
    global HG_error = 0
    global HG_cor = `e(cor)'
    global HG_bmat = e(bmat)
    global HG_const = 0
    global HG_ngeqs = e(ngeqs)
    global HG_inter = e(inter)
    global HG_dots = 0
    global HG_init = e(init)
    matrix M_nbrf = e(nbrf)
    matrix M_nrfc = e(nrfc)
    matrix M_ip =  J(1,$HG_tprf+2,1)
    matrix M_nffc =  e(nffc)
    if $HG_tprf<2{ local tprf = 2}
    matrix M_znow =J(1,`tprf'-1,1)
    matrix M_nip = e(nip)
    capture matrix M_ngeqs = e(mngeqs)
    capture matrix M_b=e(mb)
    capture matrix M_chol = e(chol)
local lev = 2
while `lev'<=$HG_tplv{
    local l = M_nrfc[1,`lev'-1] + 1  /* loop */
    local k = M_nrfc[2,`lev'-1] + 1  /* r. eff. */
    while `l'<=M_nrfc[1,`lev']&$HG_tplv>1{
        local tp = M_nrfc[2,`lev']
        if $HG_mult{ 
            local tp = `k' /* only one z-matrix per level */
        }
        while `k'<=`tp'{
            *disp "loop " `l' " random effect " `k'
            local kk = `k'
            if $HG_mult{
                local kk = `l'
            }
            local w = M_nip[2,`kk']

            /* same loc and prob as before? */
            local found = 0
            local ii=M_nrfc[2,1] + 1
            while `ii'<`kk'{
                if `w'==M_nip[2,`ii']{
                    local found = 1
                }
                local ii = `ii'+1
            }


            capture matrix M_zps`w' =e(zps`w')
            *matrix list M_zps`w'
            if `what'==2{
                if $HG_free {
                    if `k' == M_nrfc[1,`l']{
                        local nip = colsof(M_zps`w')
                        noi disp in gr "prior probabilities"


                        local j = 2
                        local zz=string(exp(M_zps`w'[1,1]),"%6.0gc")
                        if `nip'>1{ 
                            local mm "0`zz'"
                        }
                        else{
                            local mm "1"
                        }

                        while `j'<=`nip'{
                            local zz=string(exp(M_zps`w'[1,`j']),"%6.0gc")
                            local mm "`mm'" ", " "0`zz'"
                            local j = `j' + 1
                        }
                        disp in gr "    prob: " in ye "`mm'"

                        disp " "
                    }
                }
                else if `found'==0{
                    *noi disp in gr "probabilities for `w' quad. points"
                    *noi matrix list M_zps`w'
                    *disp " "
                }
            }
            * disp "M_zlc`w'"
            matrix M_zlc`w'=e(zlc`w')
            *matrix list M_zlc`w'
            if `what'==2{
                if $HG_free{
                    noi disp in gr "locations for random effect " `w'-1
                    local mm=string(M_zlc`w'[1,1],"%6.0gc")
                    local j = 2
                    while `j'<= `nip'{
                        local zz=string(M_zlc`w'[1,`j'],"%6.0gc")
                        local mm "`mm'" ", " "`zz'"
                        local j = `j' + 1
                    }
                    disp in gr "     loc: " in ye "`mm'"
                    disp " "
                }
                else if `found'==0{
                    *noi disp in gr "locations for `w' quadrature points"
                    *noi matrix list M_zlc`w'
                    *disp " "
                }
                
            }
            local k = `k' + 1
        }
        local l = `l' + 1
    }
local lev = `lev' + 1
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
    if $HG_free==0&$HG_init==0{
        matrix drop M_chol
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
    global HG_nolog
    global HG_olog
    global HG_mlog
    global HG_smlog
    global HG_oth
    global HG_exp
    global HG_expf
    global HG_lv
    global HG_fv
    global HG_nump
    global HG_eqs
    global HG_obs
    global HG_off
    global HG_offs
    global HG_denom
    global HG_cor
    global HG_s1
    global HG_init
    global HG_ind
    global HG_const
    global HG_dots
    global HG_inter
    global HG_ngeqs
    global HG_ethr
    global HG_mult
    global HG_lzpr
    global HG_zip
    global HG_cip
    global HG_post
    global HG_outc
    global HG_comp
    global HG_final
    capture macro drop HG_co*
    capture matrix drop M_above
end
