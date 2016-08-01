*! version 2.2.02 27oct2001  (TSJ-2: st0005)
program define gllam_ll
version 6.0
args todo bo lnf junk1 junk2 what res
* what = 1: update posterior means and standard deviations
* what = 2: posterior probabilities

timer on 3
timer on 8
if "`what'"==""{
	local what = 0
}
*disp in re "what=" `what'

*matrix list `bo'
if $HG_dots {
	noi disp in gr "." _c
}
/* ----------------------------------------------------------------------------- */
/* set up variables and macros needed */

tempname b mzlc

local toplev = $HG_tplv
local topi = $HG_tpi
local clus $HG_clus

sort `clus'

* reset the the clock and reset znow
local i = 1
matrix M_ip[1,1] = 1 /* in case topi=0 */
while (`i' <= `topi'){
	matrix M_ip[1,`i'] = 1
	local i = `i' + 1
}

/* -------------------------------------------------------------------------------- */
/* set up lprod1 ... lint1 */

local i=1
tempvar extra
quietly gen double `extra'=0
while `i' <= `toplev'{               
	tempvar  lint`i'
	gen double `lint`i'' = 0.0   /* used to integrate, therefore must be zero */
	tempvar lfac`i'
	quietly gen double `lfac`i'' = 0  
	if (`i'>1){
		tempvar  lprod`i'
		quietly gen double `lprod`i'' = .
		tempvar lfac`i'
		quietly gen double `lfac`i'' = 0  
	}
	local i = `i' + 1
}

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

if `what'==1{
	/* set up names for HG_E`rf'`lev' and  HG_V`rf'`lev' */
	local lev = 1
	while (`lev'<=$HG_tplv){
		local rf = 1
		if `lev'<$HG_tplv{
			local maxrf =M_nrfc[2,`lev'+1]
		}
		else{
			local maxrf =M_nrfc[2,$HG_tplv]
		}
		while `rf'<`maxrf'{
			* disp in re "creating HG_E`rf'`lev'"
			tempname junk
			global HG_E`rf'`lev' "`junk'"
			gen double ${HG_E`rf'`lev'}=0
			tempname junk
			global HG_V`rf'`lev' "`junk'"
			gen double ${HG_V`rf'`lev'}=0
			local rf = `rf'+1
		}
		local lev= `lev' + 1
	}

}
timer off 8

timer on 7
qui remcor "`bo'"
timer off 7

timer on 8
if $HG_error==1{
	disp in re "error in remcor"
	scalar `lnf' = .
	exit
}

* disp "HG_xb1 after remcor: $HG_xb1[$which]:" $HG_xb1[$which]
* disp "HG_s2 after remcor: $HG_s2[$which]:" $HG_s2[$which]

if $HG_adapt{
	local i = 2
	tempname junk
	global HG_zuoff "`junk'"
	qui gen double $HG_zuoff = 0
	while `i'<=$HG_tprf{
		local im = `i' - 1
		* disp in re "HG_MU`im'[$which] = " ${HG_MU`im'}[$which]
		* disp in re "HG_SD`im'[$which] = " ${HG_SD`im'}[$which]

                qui replace ${HG_MU`im'} = 0 if ${HG_MU`im'} ==.
		qui replace ${HG_SD`im'} = 1e-05 if ${HG_SD`im'} < 1e-25 | ${HG_SD`im'} ==.

		* disp in re "replace HG_zuoff = HG_zuoff + HG_s`i'*HG_MU`im'"
		qui replace $HG_zuoff = $HG_zuoff + ${HG_s`i'}*${HG_MU`im'}

		* disp in re "replace HG_s`i' = HG_SD`im'*HG_s`i'"
		qui replace ${HG_s`i'} = ${HG_SD`im'}*${HG_s`i'}

		local i = `i' + 1
	}
* dis in re "HG_zuoff[$which] = " $HG_zuoff[$which]
}



local i = 2
while `i' <= `toplev'{
	quietly zip `i'
	local i = `i' + 1
}

timer off 8
timer on 9
* disp "STARTING LOOP"
/* --------------------------------------------------------------------------------- */
/* recursive loop through r.effs (levels)    */
/* topi nested loops: irf from 1 ro nip(rf) */
/* ip is "clock": (irf) stages of loops      */

local levno = `toplev'
local rf = `topi'
while (`rf' <= `topi') { /* for each r.eff */

/* ----------------------------------------------------------------------------------*/
/* reset ip to 1st point for all lower r.effs... */
/* update znow                                   */  
	* disp "reset ip up to random effect " `rf'
	while (`rf' > 1) {
		local rf = `rf' - 1
		* disp `rf'
		matrix M_ip[1,`rf'] = 1
	}
	while (`levno' > 1){
	/* update znow for all new ips    */
		quietly zip `levno'
		local levno = `levno' - 1
	}
/* --------------------------------------------------------------------------------- */
/* set lint1 to lpyz for new znow  */
		
	local rf = 1
	local levno = 1
	local sortlst `clus' /* cluster variables to aggregate over */

	*matrix list M_ip
        timer off 9
	timer on 4
	qui lpyz `lint1'
	timer off 4
        timer on 9

	if `what'==1{
		local llev = 1
		while `llev'<$HG_tplv{
			local lrf = M_nrfc[2,`llev']
			while `lrf'<M_nrfc[2,`llev'+1]{
				* disp in re "setting `lrf', `llev' to M_znow[1, " `lrf' "]"
				* qui replace ${HG_E`lrf'`llev'} = M_znow[1,`lrf'-1]
				* qui replace ${HG_V`lrf'`llev'} = M_znow[1,`lrf'-1]^2
				scalar `mzlc' = M_znow[1,`lrf']
				qui replace ${HG_E`lrf'`llev'} = ${HG_MU`lrf'} + ${HG_SD`lrf'}*`mzlc'
				qui replace ${HG_V`lrf'`llev'} = ${HG_E`lrf'`llev'}^2
				local lrf = `lrf' + 1
			}
			local llev = `llev' + 1
		}
	}

	* noi disp " after lpyz lint1 = " `lint1'[$which]
	quietly count if `lint1'==.& $HG_ind==1
	if r(N) > 0{
		* overflow problem
		noi disp "overflow at level 1 ( " r(N) " missing values)"
		*list $HG_clus if `lint1'==.
		*matrix list `bo'
		*lpyz `lint1'
		if `what'==0{
			scalar `lnf' = .
			exit
		}	
	}
	quietly replace `lint1' = `lint1' * $HG_wt1

/* --------------------------------------------------------------------------------- */
/* update lint for all completed levels up to */
/* highest completed level, reset lower lints */
/* to zero (for models including a random effect) */

	while (M_ip[1,`rf'] == M_nip[1,`rf'] & `rf' <= `topi'){
	* digit equals its max => increment next digit	
		if (`rf' == M_nrfc[1,`levno'] & `levno' < `toplev'){
		* done last r.eff of current level
			* disp "********** level " `levno' " complete ************"

			* next level
			local lprev = `levno'
			local levno = `levno' + 1 
 
			/* change sortlst */  
			local prvsort `sortlst'
			local l = `toplev' - `levno' + 2
			tokenize "`sortlst'"
			* take away var. of level to sum over          	
			local `l' " "                 
			local sortlst "`*'"
/*------------------------------------------------------------------------------------ */
/* change lprod`levno' and  */
/* update lint`levno'       */

			if "`f`levno''"==""{ /* first term for lint`levno' */
				local f`levno'=1
				* disp "first term for level `levno'"
			}
			else{   
				local f`levno'=0
				* disp "next term for level `levno'"
			}
                        timer off 9
			timer on 6
			lnupdate `levno' `lint`levno'' `lint`lprev'' `lprod`levno'' /*
				*/ `lfac`levno'' `lfac`lprev'' `extra' /*
				*/ `lnf' "`prvsort'" "`sortlst'" `f`levno'' `what'
			timer off 6
                        timer on 9
			local f`lprev'

*args levno lintlv lintprv lprodlv lfaclv lfacprv extra lnf prevsort sortlst first
/* ------------------------------------------------------------------------------------------- */	
		} /* next digit */
		local rf = `rf' + 1
	}
	* rf is first r.eff that is not complete
	* increase clock in lowest incomplete digit
	* disp "update rf = " `rf'
	matrix M_ip[1,`rf'] = M_ip[1,`rf'] + 1
}
timer off 9
timer on 10
*quietly{ 
	*now rf too high
	*!! disp "********** level " `toplev' " complete ************"
	*a noi disp "lint" `toplev' "[" $which "] = " `lint`toplev''[$which]
	if(`toplev'>1){
		if `what'==1{
			local i = 1
			while `i'<$HG_tprf{
				* disp in re "setting HG_MU`i' and HG_SD`i'"
				* disp in re "by `sortlst': replace HG_MU`i' = HG_E`i'`toplev'/lint`toplev'[_N]"
				qui by `sortlst': replace ${HG_MU`i'} = ${HG_E`i'`toplev'}/`lint`toplev''[_N]
				qui by `sortlst': replace ${HG_SD`i'} = ${HG_V`i'`toplev'}/`lint`toplev''[_N] - ${HG_MU`i'}^2
				qui replace ${HG_SD`i'} = cond(${HG_SD`i'}>0,sqrt(${HG_SD`i'}),0) 
				*noi list ${HG_V`i'`toplev'}  ${HG_MU`i'} if ${HG_SD`i'}==.
				*a noi disp "HG_V`i'`toplev'[$which] = " ${HG_V`i'`toplev'}[$which]
				*a noi disp "HG_E`i'`toplev'[$which] = " ${HG_E`i'`toplev'}[$which]
				*a noi disp "HG_MU`i'[$which] = " ${HG_MU`i'}[$which]
				*a noi disp "HG_SD`i'[$which] = " ${HG_SD`i'}[$which]
				local i = `i' + 1
			}
		}
		else if `what'==2{
			local i = 1
			while `i'<= M_nip[1,2] {
				qui by `sortlst': replace ${HG_p`i'} = ${HG_p`i'}/`lint`toplev''[_N]
				local i = `i' + 1
			}
		}
		*a disp "taking log of lint" `toplev' " = " `lint`toplev''[$which]
		*a disp "subtracting " `lfac`toplev''[$which]
		quietly replace `lint`toplev'' = (ln(`lint`toplev'')-`lfac`toplev'')* ${HG_wt`toplev'}
	}
	*a noi display "lint" `tokplev' "[" $which "] = " `lint`toplev''[$which]
	if `what'==3{
		qui replace `res' = `lint`toplev''
	}
	qui by `sortlst': replace  `extra' = cond(_n==_N,1,0)
	*mlsum `lnf' = `lint`toplev'' if `extra' == 1 /* can only use this when program called by ML */
	qui count if `extra' == 1
	local n = r(N)
	summarize `lint`toplev'', meanonly
	if `n' > r(N) {
		noi disp "there are " r(N) " values of likelihood, should be " `n'
		* noi list `sortlst' if `extra' == 1& `lint`toplev''==.
		noi disp "lnf equal to missing in last step"
		scalar `lnf' = .
		exit
	}
	scalar `lnf' = r(sum)
	* noi display "total lnf = " `lnf'
	* capture drop lint`toplev'
	* gen double lint`toplev' = `lint`toplev''
timer off 10
*} /* qui */
timer off 3
end

program define lnupdate
version 6.0
args levno lintlv lintprv lprodlv lfaclv lfacprv extra lnf prvsort sortlst first what
tempvar lpkpl
* qui gen double `lpkpl' = 0 /* adapt */
quietly{
	*!! disp "!!! update level " `levno'


	/* set previous lint to ln(lint) */
	local lprev = `levno' - 1
	if(`levno' > 2){
		*!! disp " replace lint" `lprev' " by ln(lint" `lprev' ")"
		quietly count if `lintprv' < 1e-308
		if r(N) > 0{
			/* overflow problem */
			noi disp "overflow at level " `lprev'
			scalar `lnf' = .
			exit
		}
		if `what'==1{
			local rf = 1
			while `rf' < M_nrfc[2,`lprev'] {
				* disp "by `prvsort': replace HG_E`rf'`lprev' = HG_E`rf'`lprev'/lintprv[_N]"
		    		qui by `prvsort': replace ${HG_E`rf'`lprev'} = ${HG_E`rf'`lprev'}/`lintprv'[_N]
				qui by `prvsort': replace ${HG_V`rf'`lprev'} = ${HG_V`rf'`lprev'}/`lintprv'[_N]
				local rf = `rf' + 1
			}
		}
		quietly replace `lintprv' = ln(`lintprv')
		quietly replace `lintprv' = (`lintprv'-`lfacprv')*${HG_wt`lprev'}
	}

	/* sum previous lprod within cluster at current level */
	*!! disp " "
	*!! disp "by `sortlst': replace lprod" `levno' "=cond(_n==N, sum(lint" `lprev' "))"
	quietly by `sortlst': replace `lprodlv' = /*
		*/ cond(_n==_N,sum(`lintprv'),.)
	* disp " "
	* disp "lprod" `levno' " = " `lprodlv'[$which]

	/* accumulate terms for integral */

	/* get lpkpl: log of product of r.effs at level */
	* update znow for levno
	qui zip `levno'
	qui lzprob `levno' `lpkpl'
	*a disp "lpkpl = " `lpkpl'[$which]

	if `first' { /* first term for lint`levno' */
		quietly replace `extra' = 0
		quietly replace `lfaclv' = -`lprodlv' - `lpkpl'
		*a noi disp " "
		*a disp "lfac`levno' = " `lfaclv'[$which]
                qui replace `lintlv' = 1
	}
	else{
		local max = 500
		quietly replace `extra' = cond(`lprodlv'+ `lpkpl'+`lfaclv'>`max', /*
                */ -(`lprodlv'+`lpkpl'+`lfaclv')+`max',0)
		*a disp "extra = " `extra'[$which]
		quietly replace `lfaclv'=`lfaclv'+`extra'
		*a disp "lfac`levno' = " `lfaclv'[$which]

                /* increment lint at current level using lprod at previous level */
	        *a disp "increase lint" `levno' " by exp(lprodlv + lpkpl +lfaclv)"
	        quietly replace `lintlv' = exp(`extra')*`lintlv' + exp(`lprodlv'+ `lpkpl'+`lfaclv')
                *a noi disp "increase by " exp(`lprodlv'[$which]+`lpkpl'[$which]+`lfaclv'[$which]) " to "  `lintlv'[$which]
	}


/* posterior means and variances*/
	if `what'==1{
		local rf = 1
		while `rf' < M_nrfc[2,`levno'] {
			* noi disp "update `rf' `levno'"
			quietly by `sortlst': replace ${HG_E`rf'`levno'}=/*
			*/ exp(`extra'[_N])*${HG_E`rf'`levno'}+ ${HG_E`rf'`lprev'}*exp(`lprodlv'[_N]+`lpkpl'+`lfaclv'[_N])
			*a noi disp "HG_E" `rf' `levno' "[" $which "] = "  ${HG_E`rf'`levno'}[$which]
			quietly by `sortlst': replace ${HG_V`rf'`levno'}=/*
			*/ exp(`extra'[_N])*${HG_V`rf'`levno'}+ ${HG_V`rf'`lprev'}*exp(`lprodlv'[_N]+`lpkpl'+`lfaclv'[_N])
			*a noi disp "HG_V" `rf' `levno' "[" $which "] = "  ${HG_V`rf'`levno'}[$which]
			local rf = `rf' + 1
		}
	}
	else if `what'==2{
		* noi matrix list M_ip
		local i = M_ip[1,2]
		local j = 1
		while `j'<`i'{
			quietly by `sortlst': replace ${HG_p`i'} = exp(`extra'[_N])*${HG_p`i'}
			local j = `j' + 1
		}
		quietly by `sortlst': replace ${HG_p`i'} = exp(`lprodlv'[_N]+`lpkpl'+`lfaclv'[_N])
	}
	/* reset previous lint to zero */
	if `levno'>2{
		if `what'==1{
			local rf = 1
			while `rf' < M_nrfc[2,`lprev'] {
				* disp in re "replace HG_E`rf'`lprev' = 0"
		    		qui replace ${HG_E`rf'`lprev'} = 0
				qui replace ${HG_V`rf'`lprev'} = 0
				local rf = `rf' + 1
			}	
		}
		*!! disp "setting lint" `lprev' " to zero"
		quietly replace `lintprv' = 0
		quietly replace `lfacprv' = 0
	}
 } /* qui */
end


program define zip
	version 6.0
	* updates znow 
	* matrix list M_ip
	args levno
/* -----------------------------------------------------------------------------*/
/* do we need to update all r.effs at current level?   */

	* disp "in zip, levno is " `levno'
	local i = M_nrfc[2,`levno'-1] + 1

	*!! disp "update" 
	*local k = M_nrfc[1,`levno']
	*local k = M_ip[1,`k']
	local last = M_nrfc[2,`levno']
	while `i' <= `last'{
		if $HG_free{
			* same class for all random effects
			local which = M_nrfc[1,`levno']
			local which = M_ip[1,`which']
		}
		else{
			local which = M_ip[1,`i']
		}
		local npt = M_nip[2,`i']
		local im = `i' - 1
	 	* disp "     "`im' "th z to " `which' "th location"
		* disp " using M_zlc`npt' "
		matrix M_znow[1,`im'] = M_zlc`npt'[1,`which']
		*!! disp M_znow[1,`im'] 
		local i = `i' + 1
	}
end

program define lzprob
	version 6.0
	* returns product of pk needed for integration at level lev for current ip
	args levno lpkpl
	tempname mzps mznow
	* disp in re "in zprob, levno is " `levno'
	qui gen double `lpkpl' = 0

	local i=M_nrfc[1,`levno'-1] + 1 

	*!! disp "-----------lpkpl: sum of log of" 
	local last = M_nrfc[1,`levno'] 
	while `i' <= `last'{
		local npt = M_nip[2,`i']
		* disp "     prob for " `i' "th r.eff: " `which' "th weight"
		* disp " using M_zps`npt' "
		if $HG_free{
			local which = M_ip[1,`last']
			scalar `mzps' = M_zps`npt'[1,`which']
			qui replace `lpkpl' = `lpkpl' + ln(`mzps')
		}
		else{
			local which = M_ip[1,`i']
			local im = `i' - 1
			scalar `mzps' = M_zps`npt'[1,`which']
			qui replace `lpkpl' = `lpkpl'+ln(`mzps')
			if $HG_adapt{
				scalar `mznow' = M_znow[1,`im']
				qui replace `lpkpl' = `lpkpl' + ln(${HG_SD`im'}) + `mznow'^2/2 - (${HG_MU`im'} + ${HG_SD`im'}*`mznow')^2/2
			}
		}
		local i=`i'+1
	}
	* disp in re "lpkpl[$which] = " `lpkpl'[$which]
end


program define lpyz
	version 6.0
* returns log of prob of obs. given znow
	args lpyz

	* disp "-----------------called lpyz"

	tempvar zu xb mu /* linear predictor and zu: r.eff*design matrix for r.eff */

/* ----------------------------------------------------------------------------- */
*quietly{
	

	if $HG_tprf>1{
		matrix score double `zu' = M_znow
		if $HG_adapt{ 
			qui replace `zu' = $HG_zuoff + `zu'	
		}
	}
	else{
		qui gen double `zu' = 0
	}

	* matrix list M_znow
	* disp "ML_y1: $ML_y1 " $ML_y1[$which]
	* matrix list M_ip
	* disp " xb1 = " $HG_xb1[$which]
	* disp " zu = " `zu'[$which]


	if $HG_mlog>0{
		nominal `lpyz' `zu'
	}

	if $HG_oth{
		if "$HG_lv"~=""&($HG_nolog>0|$HG_mlog>0){
			local myand $HG_lvolo~=1
		}
		quietly gen double `mu' = 0
		timer on 5
		if $HG_noC {
			link "$HG_link" `mu' $HG_xb1 `zu' $HG_s1
			*disp " mu = " `mu'[$which]
			family "$HG_famil" `lpyz' `mu' "`myand'"
		}

		else {
			if $HG_lev1 != 0 {
				local s1opt "st($HG_s1)"
			}
			if "$HG_denom" != "" {
				local denopt "denom($HG_denom)"
			}
			if "$HG_fv" != "" {
				local fvopt "fv($HG_fv)"
			}
			if "$HG_lv" != "" {
				local lvopt "lv($HG_lv)"
				local othopt "oth(M_oth)"
			}
			if "`myand'" != "" {
				local ifopt "if `myand'"
			}
			noi _gllamm_fl `lpyz' `mu' `ifopt', `s1opt' /*
			*/ link($HG_link) family($HG_famil) `denopt' `fvopt' /*
			*/ `lvopt' xb($HG_xb1) zu(`zu') /*
			*/ y($ML_y1) `othopt'

		}
		timer off 5
	}

	if $HG_nolog>0{
		if $HG_noC {
			ordinal `lpyz' `zu'
		}
		else {
			if $HG_lev1 != 0 {
				local stopt st($HG_s1)
			}
			if "$HG_lv"!="" {
				local lvopt lv($HG_lv)
			}
			local j 1
			while `j'<=$HG_tpff {
				local xbeta `xbeta' ${HG_xb`j'}
				local j = `j' + 1
			}
			_gllamm_ord `lpyz', y($ML_y1) xb(`xbeta') /*
			*/ zu(`zu') link($HG_linko) nlog($HG_nolog) /*
			*/ olog(M_olog) nresp(M_nresp) resp(M_resp) /*
			*/ `stopt' `lvopt'
		}
	}

*} /* qui */
end

program define nominal
	version 6.0
	args lpyz zu
	tempvar mu

	if $HG_smlog{
		local s $HG_s1
	}
	else{
		local s = 1
	}
	local and
   	if "$HG_lv"~=""{
		local and & $HG_lv == $HG_mlog
		local mlif if $HG_lv == $HG_mlog
	}
	disp "mlogit link `mlif'"
	if $HG_exp==1&$HG_expf==0{
		qui gen double `mu' = exp(`zu'/`s') if $ML_y1==M_respm[1,1] `and'
		local n=rowsof(M_respm)
		local i=2
		while `i'<=`n'{
			local prev = `i' - 1 
			* disp "xb`prev':" ${HG_xb`prev'}[$which]
			qui replace `mu' = exp((${HG_xb`prev'} + `zu')/`s') if $ML_y1==M_respm[`i',1] `and'
			local i = `i' + 1
		}

		sort $HG_clus $HG_ind
		qui by $HG_clus: replace `lpyz'=cond(_n==_N,sum(`mu'),.) `mlif'
		qui replace `lpyz' = ln(`mu'/`lpyz') `mlif'
		by $HG_clus: list $ML_y1 if _n==_N& `lpyz'==. `and'
	}
	else if $HG_exp==1&$HG_expf==1{
		qui gen double `mu' = exp(($HG_xb1 + `zu')/`s') `mlif'
		sort $HG_clus $HG_ind
		* disp "sort $HG_clus $HG_ind"
		qui by $HG_clus: replace `lpyz'=cond(_n==_N,sum(`mu'),.) `mlif'
		* disp "denom = " `lpyz'[$which]
		qui replace `lpyz' = ln(`mu'/`lpyz') `mlif' 
	}
	else{
		tempvar den tmp
		local n=rowsof(M_respm)
		local i = 2
		qui gen double `mu' = 1 if $ML_y1==M_respm[1,1] `mlif'
		qui gen double `den' = 1
		qui gen double `tmp' = 0
		while `i'<= `n'{
			local prev = `i' - 1 
			qui replace `tmp' = exp((${HG_xb`prev'} + `zu')/`s') `mlif'
			qui replace `mu' =  `tmp' if $ML_y1==M_respm[`i',1] `mlif'
			replace `den' = `den' + `tmp' `mlif'
			local i = `i' + 1
		}
		replace `lpyz' = ln(`mu'/`den') `mlif'
	}
end

program define ordinal
	version 6.0
	args lpyz zu
	local no = 1
	local xbind = 2
	tempvar mu p1 p2
	qui gen double `p1' = 0
	qui gen double `p2' = 0
	qui gen double `mu' = 0

	while `no' <= $HG_nolog{
		local olog = M_olog[1,`no']
		local lnk: word `no' of $HG_linko

		if "`lnk'"=="ologit"{
			local func logitl
		}
		else if "`lnk'"=="oprobit"{
			local func probitl
		}
		else if "`lnk'"=="ocll"{
			local func cll
		}
		else if "`lnk'"=="soprobit"{
			local func sprobitl
		}
		local and
   		if "$HG_lv"~=""&$HG_nolog>0{
			local and & $HG_lv == `olog'
		}
		* disp "ordinal link is `lnk', and = `and'"
		local n=M_nresp[1,`no']

		* disp  "HG_xb1: " $HG_xb1
		* disp  "xbind = " `xbind'
		* disp  ${HG_xb`xbind'}[$which]

		qui replace `mu' = $HG_xb1+`zu'-${HG_xb`xbind'}
		`func' `mu' `p1'
		qui replace `lpyz' = ln(1-`p1') /*
			*/ if $ML_y1==M_resp[1,`no'] `and'
		qui replace `p2' = `p1'
		local i = 2
		while `i' < `n'{
			local nxt = `xbind' + `i' - 1 

			* disp "nxt = " `nxt'
			* disp ${HG_xb`nxt'}[$which]

			qui replace `mu' = $HG_xb1+`zu'-${HG_xb`nxt'}
			`func' `mu' `p2'

			* disp "p1 and p2: "  `p1'[$which] " " `p2'[$which]

			qui replace `lpyz' = ln(`p1' -`p2') /*
				*/ if $ML_y1==M_resp[`i',`no'] `and'
			qui replace `p1' = `p2'
			local i = `i' + 1
		}
		local xbind = `xbind' + `n' -1
		qui replace `lpyz' = ln(`p2') /*
			*/ if $ML_y1==M_resp[`n',`no'] `and'
		local no = `no' + 1
	} /* next ordinal response */
	*tab $ML_y1 if `lpyz'==. `and'
	qui replace `lpyz' = -100 if `lpyz'==. `and'
end

program define logitl
	version 6.0
	args mu p
	qui replace `p' = 1/(1+exp(-`mu'))
end

program define cll
	version 6.0
	args mu p
	qui replace `p' = 1-exp(-exp(`mu'))
end

program define probitl
	version 6.0
	args mu p
	qui replace `p' = normprob(`mu')
end

program define sprobitl
	version 6.0
	args mu p
	qui replace `p' = normprob(`mu'/$HG_s1)
end


program define link
	version 6.0
* returns mu for requested link
	args which mu xb zu s1
	* disp " in link, which is `which' "

	tokenize "`which'"
	local i=1
	local ifs
	while "`1'"~=""{
		if "$HG_lv" ~= ""{
			local oth =  M_oth[1,`i']
			local ifs if $HG_lv==`oth'
		}
		* disp "`1' link `ifs'"
		
		if ("`1'" == "logit"){
			quietly replace `mu' = 1/(1+exp(-`xb'-`zu')) `ifs'
		}
		else if ("`1'" == "probit"){
			* disp "doing probit "
			quietly replace `mu' = normprob((`xb'+`zu')) `ifs'
		}
		else if ("`1'" == "sprobit"){
			quietly replace `mu' = normprob((`xb'+`zu')/`s1') `ifs'
		}
		else if ("`1'" == "log"){
			* disp "doing log "
			quietly replace `mu' = exp(`xb'+`zu') `ifs'
		}
		else if ("`1'" == "recip"){
			* disp "doing recip "
			quietly replace `mu' = 1/(`xb'+`zu') `ifs'
		}
		else if ("`1'" == "cll"){
			* disp "doing cll "
			quietly replace `mu' = 1 - exp(-exp(`xb'+`zu')) `ifs'
		}
		else if ("`1'" == "ident"){
			quietly replace `mu' = `xb'+`zu' `ifs'
		}
		local i = `i' + 1
		mac shift
	}

end

program define family
	version 6.0
	args which lpyz mu und

	tokenize "`which'"
	local i=1
	* disp "in family, und = `und'"
	if "$HG_fv" == ""{
		local ifs
		if "`und'"~=""{local und if `und'}
	}
	else{
		if "`und'"~=""{local und & `und'}
	}
	while "`1'"~=""{
		if "$HG_fv" ~=""{
			local ifs if $HG_fv == `i'
		}
		if ("`1'" == "binom"){
			famb `lpyz' `mu' "`ifs'" "`und'"
		}
		else if ("`1'" == "poiss"){
			famp `lpyz' `mu' "`ifs'" "`und'"
		}
		else if ("`1'" == "gauss") {
			famg `lpyz' `mu' $HG_s1 "`ifs'" "`und'"  /* get log of conditional prob. */
		}
		else if ("`1'" == "gamma"){
			famga `lpyz' `mu' $HG_s1 "`ifs'" "`und'"
		}
		else{
			disp in re "unknown family in gllam_ll"
			exit 198
		}
		local i = `i' + 1
		mac shift
	}
end
	
program define famg
	version 6.0
* returns log of normal density conditional on r.effs
	args lpyz mu s1 if and
	* disp "running famg `if' `and'"
	* disp "s1 = " `s1'[$which] ", mu = " `mu'[$which] " and Y = " $ML_y1[$which]
      	quietly replace `lpyz' = /*
		*/ -(ln(2*_pi*`s1'^2) + (($ML_y1-`mu')/`s1')^2)/2 `if' `and'
end

program define famb
	version 6.0
* returns log of binomial density conditional on r.effs
* $HG_denom is denominator
	args lpyz mu if and
	* disp "running famb `if' `and'"
	* disp "mu = " `mu'[$which] " and Y = " $ML_y1[$which]
	qui replace `lpyz' = cond($ML_y1>0,$ML_y1*ln(`mu'),0) `if' `and'
	qui replace `lpyz' = `lpyz' + cond($HG_denom-$ML_y1>0,($HG_denom-$ML_y1)*ln(1-`mu'),0) `if' `and'
	*tab $ML_y1 `if' `and' & `lpyz'==.
	qui replace `lpyz' = cond(`lpyz'==.,-100,`lpyz') `if' `and'
	*quietly replace `lpyz' = /*
		*/ $ML_y1*ln(`mu')+($HG_denom-$ML_y1)*cond(ln(1-`mu')~=.,ln(1-`mu'),-100) `if' `and'
	* disp "done famb"
end

program define famp
	version 6.0
* returns log of poisson density conditional on r.effs
	args lpyz mu if and
	*!! disp "running famp `if'"
	* disp in re "if and: `if' `and'"
	quietly replace `lpyz' = /*
		*/ $ML_y1*(ln(`mu'))-`mu'-lngamma($ML_y1+1) `if' `and'
	* qui replace `lpyz' = cond(`lpyz'==.,-100,`lpyz') `if' `and'
	* disp "done famp"
end

program define famga
	version 6.0
* returns log of gamma density conditional on r.effs
	args lpyz mu s1 if and
	*!! disp "running famg `if'"
	*!! disp "mu = " `mu'[$which]
	*!! disp "s1 = " `s1'[$which]
	qui replace `mu' = 0.0001 if `mu' <= 0
	tempvar nu
	qui gen double `nu' = `s1'^(-2)
      	quietly replace `lpyz' = /*
		*/ `nu'*(ln(`nu')-ln(`mu')) - lngamma(`nu')/*
		*/ + (`nu'-1)*ln($ML_y1) - `nu'*$ML_y1/`mu' `if' `and'
end

program define timer
version 6.0
end
